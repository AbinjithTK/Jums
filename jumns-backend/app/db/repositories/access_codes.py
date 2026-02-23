"""Repository for jumns-access-codes table."""

from __future__ import annotations

from botocore.exceptions import ClientError

from app.db.base_repository import BaseRepository, utc_now_iso
from app.db.connection import get_table
from app.db.table_config import ACCESS_CODES_TABLE


class AccessCodesRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_table(ACCESS_CODES_TABLE))

    def activate_code(self, user_id: str, code: str) -> bool:
        """Atomically activate a code. Returns True on success."""
        try:
            self._table.update_item(
                Key={"code": code},
                UpdateExpression="SET usedBy = :uid, usedAt = :now",
                ConditionExpression="attribute_exists(code) AND attribute_not_exists(usedBy)",
                ExpressionAttributeValues={
                    ":uid": user_id,
                    ":now": utc_now_iso(),
                },
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False  # code doesn't exist or already used
            raise

    def get_activation_status(self, user_id: str) -> bool:
        """Check if this user has activated any access code."""
        try:
            resp = self._table.scan(
                FilterExpression="usedBy = :uid",
                ExpressionAttributeValues={":uid": user_id},
                Limit=1,
            )
            return len(resp.get("Items", [])) > 0
        except Exception:
            return False
