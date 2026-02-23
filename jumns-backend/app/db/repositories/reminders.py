"""Repository for jumns-reminders table."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.db.base_repository import BaseRepository, new_id, utc_now_iso
from app.db.connection import get_table
from app.db.table_config import REMINDERS_TABLE


class RemindersRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_table(REMINDERS_TABLE))

    def create(self, user_id: str, data: dict) -> dict:
        reminder_id = new_id()
        item = {
            "userId": user_id,
            "reminderId": reminder_id,
            "id": reminder_id,
            "title": data["title"],
            "time": data.get("time", ""),
            "active": True,
            "goalId": data.get("goalId"),
            "snoozeCount": 0,
            "snoozedUntil": None,
            "originalTime": data.get("time", ""),
            "createdAt": utc_now_iso(),
        }
        item = {k: v for k, v in item.items() if v is not None}
        return self.put_item(item)

    def get(self, user_id: str, reminder_id: str) -> dict:
        return self.get_item({"userId": user_id, "reminderId": reminder_id})

    def list_all(self, user_id: str) -> list[dict]:
        return self.query_by_user(user_id)

    def update(self, user_id: str, reminder_id: str, data: dict) -> dict:
        updates = {k: v for k, v in data.items() if v is not None}
        return self.update_item(
            {"userId": user_id, "reminderId": reminder_id}, updates
        )

    def snooze(self, user_id: str, reminder_id: str, minutes: int = 30) -> dict:
        """Snooze a reminder by pushing its time forward.

        Increments snoozeCount, sets snoozedUntil to now + minutes,
        and updates the time field with the new schedule.
        """
        current = self.get(user_id, reminder_id)
        snooze_count = current.get("snoozeCount", 0) + 1
        now = datetime.now(timezone.utc)
        snoozed_until = (now + timedelta(minutes=minutes)).isoformat()

        # Build a human-readable snoozed time
        new_time_dt = now + timedelta(minutes=minutes)
        new_time_str = new_time_dt.strftime("%I:%M %p").lstrip("0")
        today_str = new_time_dt.strftime("%b %d")

        updates = {
            "snoozeCount": snooze_count,
            "snoozedUntil": snoozed_until,
            "time": f"Snoozed to {new_time_str}, {today_str}",
            "originalTime": current.get("originalTime", current.get("time", "")),
        }
        return self.update_item(
            {"userId": user_id, "reminderId": reminder_id}, updates
        )

    def delete(self, user_id: str, reminder_id: str) -> None:
        self.delete_item({"userId": user_id, "reminderId": reminder_id})
