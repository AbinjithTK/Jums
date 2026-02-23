"""Repository for jumns-tasks table."""

from __future__ import annotations

from boto3.dynamodb.conditions import Attr, Key

from app.db.base_repository import BaseRepository, new_id, utc_now_iso
from app.db.connection import get_table
from app.db.table_config import TASKS_BY_GOAL_GSI, TASKS_TABLE


class TasksRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_table(TASKS_TABLE))

    def create(self, user_id: str, data: dict) -> dict:
        task_id = new_id()
        item = {
            "userId": user_id,
            "taskId": task_id,
            "id": task_id,
            "title": data["title"],
            "time": data.get("time", ""),
            "detail": data.get("detail", ""),
            "type": data.get("type", "task"),
            "completed": False,
            "active": data.get("active", False),
            "goalId": data.get("goalId"),
            "priority": data.get("priority", "medium"),
            "requiresProof": data.get("requiresProof", False),
            "dueDate": data.get("dueDate"),
            "proofUrl": None,
            "proofType": None,
            "proofStatus": "pending",
            "completedAt": None,
            "createdAt": utc_now_iso(),
        }
        item = {k: v for k, v in item.items() if v is not None}
        return self.put_item(item)

    def get(self, user_id: str, task_id: str) -> dict:
        return self.get_item({"userId": user_id, "taskId": task_id})

    def list_all(self, user_id: str, goal_id: str | None = None) -> list[dict]:
        if goal_id:
            return self._list_by_goal(user_id, goal_id)
        return self.query_by_user(user_id)

    def _list_by_goal(self, user_id: str, goal_id: str) -> list[dict]:
        """Query tasks filtered by goalId using the TasksByGoal GSI."""
        try:
            resp = self._table.query(
                IndexName=TASKS_BY_GOAL_GSI,
                KeyConditionExpression=Key("userId").eq(user_id)
                & Key("goalId").eq(goal_id),
            )
            return resp.get("Items", [])
        except Exception:
            # Fallback: filter client-side if GSI not available
            items = self.query_by_user(user_id)
            return [i for i in items if i.get("goalId") == goal_id]

    def update(self, user_id: str, task_id: str, data: dict) -> dict:
        updates = {k: v for k, v in data.items() if v is not None}
        return self.update_item(
            {"userId": user_id, "taskId": task_id}, updates
        )

    def complete(self, user_id: str, task_id: str, data: dict) -> dict:
        updates = {
            "completed": True,
            "completedAt": utc_now_iso(),
        }
        if data.get("proofUrl"):
            updates["proofUrl"] = data["proofUrl"]
        if data.get("proofType"):
            updates["proofType"] = data["proofType"]
            updates["proofStatus"] = "submitted"
        return self.update_item(
            {"userId": user_id, "taskId": task_id}, updates
        )

    def delete(self, user_id: str, task_id: str) -> None:
        self.delete_item({"userId": user_id, "taskId": task_id})
