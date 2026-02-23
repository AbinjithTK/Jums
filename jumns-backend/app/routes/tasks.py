"""CRUD routes for /api/tasks + completion."""

from fastapi import APIRouter, Query, Request, Response

from app.db.repositories.tasks import TasksRepository
from app.models.requests import (
    CompleteTaskRequest,
    CreateTaskRequest,
    UpdateTaskRequest,
)
from app.models.responses import TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _to_response(item: dict) -> TaskResponse:
    return TaskResponse(
        id=item.get("id", item.get("taskId", "")),
        user_id=item["userId"],
        title=item["title"],
        time=item.get("time", ""),
        detail=item.get("detail", ""),
        type=item.get("type", "task"),
        completed=item.get("completed", False),
        active=item.get("active", False),
        goal_id=item.get("goalId"),
        priority=item.get("priority", "medium"),
        requires_proof=item.get("requiresProof", False),
        due_date=item.get("dueDate"),
        proof_url=item.get("proofUrl"),
        proof_type=item.get("proofType"),
        proof_status=item.get("proofStatus", "pending"),
        completed_at=item.get("completedAt"),
        created_at=item.get("createdAt"),
    )


@router.get("/")
async def list_tasks(
    request: Request, goalId: str | None = Query(None),
) -> list[TaskResponse]:
    repo = TasksRepository()
    items = repo.list_all(request.state.user_id, goal_id=goalId)
    return [_to_response(i) for i in items]


@router.get("/{task_id}")
async def get_task(request: Request, task_id: str) -> TaskResponse:
    repo = TasksRepository()
    return _to_response(repo.get(request.state.user_id, task_id))


@router.post("/")
async def create_task(request: Request, body: CreateTaskRequest) -> TaskResponse:
    repo = TasksRepository()
    item = repo.create(request.state.user_id, body.model_dump())
    return _to_response(item)


@router.patch("/{task_id}")
async def update_task(
    request: Request, task_id: str, body: UpdateTaskRequest,
) -> TaskResponse:
    repo = TasksRepository()
    item = repo.update(
        request.state.user_id, task_id, body.model_dump(exclude_none=True),
    )
    return _to_response(item)


@router.post("/{task_id}/complete")
async def complete_task(
    request: Request, task_id: str, body: CompleteTaskRequest,
) -> TaskResponse:
    repo = TasksRepository()
    item = repo.complete(
        request.state.user_id, task_id, body.model_dump(exclude_none=True),
    )
    return _to_response(item)


@router.delete("/{task_id}")
async def delete_task(request: Request, task_id: str):
    repo = TasksRepository()
    repo.delete(request.state.user_id, task_id)
    return Response(status_code=204)
