"""Repository for jumns-insights table."""

from __future__ import annotations

from app.db.base_repository import BaseRepository, new_id, utc_now_iso
from app.db.connection import get_table
from app.db.table_config import INSIGHTS_TABLE


class InsightsRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_table(INSIGHTS_TABLE))

    def create(self, user_id: str, data: dict) -> dict:
        insight_id = new_id()
        now = utc_now_iso()
        item = {
            "userId": user_id,
            "createdAt#insightId": f"{now}#{insight_id}",
            "id": insight_id,
            "type": data.get("type", "general"),
            "title": data.get("title", ""),
            "content": data.get("content", ""),
            "relatedGoalId": data.get("relatedGoalId"),
            "createdAt": now,
        }
        item = {k: v for k, v in item.items() if v is not None}
        return self.put_item(item)

    def list_all(self, user_id: str) -> list[dict]:
        return self.query_by_user(user_id, scan_forward=False)
