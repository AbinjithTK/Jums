"""Repository for jumns-skills table."""

from __future__ import annotations

from app.db.base_repository import BaseRepository, new_id, utc_now_iso
from app.db.connection import get_table
from app.db.table_config import SKILLS_TABLE


class SkillsRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_table(SKILLS_TABLE))

    def create(self, user_id: str, data: dict) -> dict:
        skill_id = new_id()
        item = {
            "userId": user_id,
            "skillId": skill_id,
            "id": skill_id,
            "name": data["name"],
            "type": data.get("type", "mcp"),
            "description": data.get("description", ""),
            "status": data.get("status", "inactive"),
            "category": data.get("category", "mcp"),
            "createdAt": utc_now_iso(),
        }
        return self.put_item(item)

    def get(self, user_id: str, skill_id: str) -> dict:
        return self.get_item({"userId": user_id, "skillId": skill_id})

    def list_all(self, user_id: str) -> list[dict]:
        return self.query_by_user(user_id)

    def update(self, user_id: str, skill_id: str, data: dict) -> dict:
        updates = {k: v for k, v in data.items() if v is not None}
        return self.update_item(
            {"userId": user_id, "skillId": skill_id}, updates
        )

    def delete(self, user_id: str, skill_id: str) -> None:
        self.delete_item({"userId": user_id, "skillId": skill_id})
