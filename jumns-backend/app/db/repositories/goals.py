"""Repository for jumns-goals table."""

from __future__ import annotations

from app.db.base_repository import BaseRepository, new_id, utc_now_iso
from app.db.connection import get_table
from app.db.table_config import GOALS_TABLE


class GoalsRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_table(GOALS_TABLE))

    def create(self, user_id: str, data: dict) -> dict:
        goal_id = new_id()
        item = {
            "userId": user_id,
            "goalId": goal_id,
            "id": goal_id,
            "title": data["title"],
            "category": data.get("category", "personal"),
            "progress": data.get("progress", 0),
            "total": data.get("total", 100),
            "unit": data.get("unit", ""),
            "insight": data.get("insight", ""),
            "activeAgent": data.get("activeAgent", ""),
            "completed": data.get("completed", False),
            "createdAt": utc_now_iso(),
        }
        return self.put_item(item)

    def get(self, user_id: str, goal_id: str) -> dict:
        return self.get_item({"userId": user_id, "goalId": goal_id})

    def list_all(self, user_id: str) -> list[dict]:
        return self.query_by_user(user_id)

    def update(self, user_id: str, goal_id: str, data: dict) -> dict:
        updates = {k: v for k, v in data.items() if v is not None}
        return self.update_item(
            {"userId": user_id, "goalId": goal_id}, updates
        )

    def delete(self, user_id: str, goal_id: str) -> None:
        self.delete_item({"userId": user_id, "goalId": goal_id})
