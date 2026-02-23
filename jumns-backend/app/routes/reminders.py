"""CRUD routes for /api/reminders + snooze."""

from fastapi import APIRouter, Request, Response

from app.db.repositories.reminders import RemindersRepository
from app.models.requests import (
    CreateReminderRequest,
    SnoozeReminderRequest,
    UpdateReminderRequest,
)
from app.models.responses import ReminderResponse

router = APIRouter(prefix="/reminders", tags=["reminders"])


def _to_response(item: dict) -> ReminderResponse:
    return ReminderResponse(
        id=item.get("id", item.get("reminderId", "")),
        user_id=item["userId"],
        title=item["title"],
        time=item.get("time", ""),
        active=item.get("active", True),
        goal_id=item.get("goalId"),
        snooze_count=item.get("snoozeCount", 0),
        snoozed_until=item.get("snoozedUntil"),
        original_time=item.get("originalTime"),
        created_at=item.get("createdAt"),
    )


@router.get("/")
async def list_reminders(request: Request) -> list[ReminderResponse]:
    repo = RemindersRepository()
    return [_to_response(i) for i in repo.list_all(request.state.user_id)]


@router.get("/{reminder_id}")
async def get_reminder(request: Request, reminder_id: str) -> ReminderResponse:
    repo = RemindersRepository()
    return _to_response(repo.get(request.state.user_id, reminder_id))


@router.post("/")
async def create_reminder(
    request: Request, body: CreateReminderRequest,
) -> ReminderResponse:
    repo = RemindersRepository()
    item = repo.create(request.state.user_id, body.model_dump())
    return _to_response(item)


@router.patch("/{reminder_id}")
async def update_reminder(
    request: Request, reminder_id: str, body: UpdateReminderRequest,
) -> ReminderResponse:
    repo = RemindersRepository()
    item = repo.update(
        request.state.user_id, reminder_id, body.model_dump(exclude_none=True),
    )
    return _to_response(item)


@router.post("/{reminder_id}/snooze")
async def snooze_reminder(
    request: Request, reminder_id: str, body: SnoozeReminderRequest,
) -> ReminderResponse:
    """Snooze a reminder by pushing it forward N minutes."""
    repo = RemindersRepository()
    item = repo.snooze(request.state.user_id, reminder_id, body.minutes)
    return _to_response(item)


@router.delete("/{reminder_id}")
async def delete_reminder(request: Request, reminder_id: str):
    repo = RemindersRepository()
    repo.delete(request.state.user_id, reminder_id)
    return Response(status_code=204)
