"""Repository for jumns-users table."""

from __future__ import annotations

from app.db.base_repository import BaseRepository, utc_now_iso
from app.db.connection import get_table
from app.db.table_config import USERS_TABLE


class UsersRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_table(USERS_TABLE))

    def get_or_create_user(self, user_id: str) -> dict:
        """Return existing user or create a new one on first access."""
        try:
            return self.get_item({"userId": user_id})
        except Exception:
            item = {
                "userId": user_id,
                "email": "",
                "timezone": "UTC",
                "agentName": "Jumns",
                "agentBehavior": "Friendly & Supportive",
                "onboardingCompleted": False,
                "morningTime": "07:00",
                "eveningTime": "21:00",
                "createdAt": utc_now_iso(),
            }
            return self.put_item(item)

    def get_settings(self, user_id: str) -> dict:
        """Return user settings (stored as attributes on user item)."""
        user = self.get_or_create_user(user_id)
        return {
            "agentName": user.get("agentName", "Jumns"),
            "agentBehavior": user.get("agentBehavior", "Friendly & Supportive"),
            "onboardingCompleted": user.get("onboardingCompleted", False),
            "timezone": user.get("timezone", "UTC"),
            "morningTime": user.get("morningTime", "07:00"),
            "eveningTime": user.get("eveningTime", "21:00"),
        }

    def upsert_settings(self, user_id: str, data: dict) -> dict:
        """Update user settings. Creates user if not exists."""
        self.get_or_create_user(user_id)
        updates = {k: v for k, v in data.items() if v is not None}
        if not updates:
            return self.get_settings(user_id)
        self.update_item({"userId": user_id}, updates)
        return self.get_settings(user_id)
