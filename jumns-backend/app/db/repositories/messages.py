"""Repository for jumns-messages table."""

from __future__ import annotations

from app.db.base_repository import BaseRepository, new_id, utc_now_iso
from app.db.connection import get_table
from app.db.table_config import MESSAGES_TABLE


class MessagesRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_table(MESSAGES_TABLE))

    def create_message(self, user_id: str, data: dict) -> dict:
        """Store a new message. SK = createdAt#msgId for time ordering."""
        msg_id = new_id()
        now = utc_now_iso()
        item = {
            "userId": user_id,
            "createdAt#msgId": f"{now}#{msg_id}",
            "id": msg_id,
            "role": data.get("role", "user"),
            "type": data.get("type", "text"),
            "content": data.get("content"),
            "cardType": data.get("cardType"),
            "cardData": self._sanitize_card_data(data.get("cardData")),
            "timestamp": now,
            "createdAt": now,
        }
        # Remove None values and empty strings (DynamoDB doesn't like them)
        item = {k: v for k, v in item.items() if v is not None}
        return self.put_item(item)

    @staticmethod
    def _sanitize_card_data(card_data) -> dict | None:
        """Sanitize cardData for DynamoDB storage.

        DynamoDB doesn't allow empty strings in sets, and nested structures
        with empty strings can cause issues. Replace empty strings with a
        placeholder and ensure all values are DynamoDB-compatible types.
        """
        if card_data is None:
            return None
        if not isinstance(card_data, dict):
            return {"content": str(card_data)}

        def _clean(obj):
            if isinstance(obj, dict):
                return {k: _clean(v) for k, v in obj.items() if v is not None}
            if isinstance(obj, list):
                return [_clean(v) for v in obj if v is not None]
            if isinstance(obj, str) and obj == "":
                return "-"  # DynamoDB-safe placeholder for empty string
            if isinstance(obj, (int, float, bool)):
                return obj
            return str(obj)

        return _clean(card_data)

    def list_messages(self, user_id: str) -> list[dict]:
        """Return all messages for a user in chronological order."""
        return self.query_by_user(user_id, scan_forward=True)

    def count_user_messages_today(self, user_id: str, date_prefix: str) -> int:
        """Count user-role messages sent today (for rate limiting)."""
        from boto3.dynamodb.conditions import Attr, Key

        try:
            resp = self._table.query(
                KeyConditionExpression=Key("userId").eq(user_id)
                & Key("createdAt#msgId").begins_with(date_prefix),
                FilterExpression=Attr("role").eq("user"),
                Select="COUNT",
            )
            return resp.get("Count", 0)
        except Exception:
            return 0

    def delete_all_messages(self, user_id: str) -> None:
        """Delete all messages for a user (paginated batch delete)."""
        items = self.query_by_user(user_id)
        keys = [
            {"userId": item["userId"], "createdAt#msgId": item["createdAt#msgId"]}
            for item in items
        ]
        if keys:
            self.batch_delete(keys)
