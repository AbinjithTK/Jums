"""CRUD routes for /api/skills."""

from fastapi import APIRouter, Request, Response

from app.db.repositories.skills import SkillsRepository
from app.models.requests import CreateSkillRequest, UpdateSkillRequest
from app.models.responses import SkillResponse

router = APIRouter(prefix="/skills", tags=["skills"])


def _to_response(item: dict) -> SkillResponse:
    return SkillResponse(
        id=item.get("id", item.get("skillId", "")),
        user_id=item["userId"],
        name=item["name"],
        type=item.get("type", "mcp"),
        description=item.get("description", ""),
        status=item.get("status", "inactive"),
        category=item.get("category", "mcp"),
        created_at=item.get("createdAt"),
    )


@router.get("/")
async def list_skills(request: Request) -> list[SkillResponse]:
    repo = SkillsRepository()
    return [_to_response(i) for i in repo.list_all(request.state.user_id)]


@router.post("/")
async def create_skill(request: Request, body: CreateSkillRequest) -> SkillResponse:
    repo = SkillsRepository()
    return _to_response(repo.create(request.state.user_id, body.model_dump()))


@router.patch("/{skill_id}")
async def update_skill(
    request: Request, skill_id: str, body: UpdateSkillRequest,
) -> SkillResponse:
    repo = SkillsRepository()
    item = repo.update(
        request.state.user_id, skill_id, body.model_dump(exclude_none=True),
    )
    return _to_response(item)


@router.delete("/{skill_id}")
async def delete_skill(request: Request, skill_id: str):
    repo = SkillsRepository()
    repo.delete(request.state.user_id, skill_id)
    return Response(status_code=204)
