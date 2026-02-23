"""CRUD routes for /api/goals."""

from fastapi import APIRouter, Request, Response

from app.db.repositories.goals import GoalsRepository
from app.models.requests import CreateGoalRequest, UpdateGoalRequest
from app.models.responses import GoalResponse

router = APIRouter(prefix="/goals", tags=["goals"])


def _to_response(item: dict) -> GoalResponse:
    return GoalResponse(
        id=item.get("id", item.get("goalId", "")),
        user_id=item["userId"],
        title=item["title"],
        category=item.get("category", "personal"),
        progress=item.get("progress", 0),
        total=item.get("total", 100),
        unit=item.get("unit", ""),
        insight=item.get("insight", ""),
        active_agent=item.get("activeAgent", ""),
        completed=item.get("completed", False),
        created_at=item.get("createdAt"),
    )


@router.get("/")
async def list_goals(request: Request) -> list[GoalResponse]:
    repo = GoalsRepository()
    items = repo.list_all(request.state.user_id)
    return [_to_response(i) for i in items]


@router.get("/{goal_id}")
async def get_goal(request: Request, goal_id: str) -> GoalResponse:
    repo = GoalsRepository()
    item = repo.get(request.state.user_id, goal_id)
    return _to_response(item)


@router.post("/")
async def create_goal(request: Request, body: CreateGoalRequest) -> GoalResponse:
    repo = GoalsRepository()
    item = repo.create(request.state.user_id, body.model_dump())
    return _to_response(item)


@router.patch("/{goal_id}")
async def update_goal(
    request: Request, goal_id: str, body: UpdateGoalRequest
) -> GoalResponse:
    repo = GoalsRepository()
    item = repo.update(
        request.state.user_id, goal_id, body.model_dump(exclude_none=True)
    )
    return _to_response(item)


@router.delete("/{goal_id}")
async def delete_goal(request: Request, goal_id: str):
    repo = GoalsRepository()
    repo.delete(request.state.user_id, goal_id)
    return Response(status_code=204)
