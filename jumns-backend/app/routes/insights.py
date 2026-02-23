"""Routes for /api/insights — list insights + trigger proactive engine."""

from fastapi import APIRouter, Request

from app.agent.agent_service import AgentService
from app.db.repositories.insights import InsightsRepository
from app.models.responses import InsightResponse

router = APIRouter(prefix="/insights", tags=["insights"])


def _to_response(item: dict) -> InsightResponse:
    return InsightResponse(
        id=item.get("id", ""),
        user_id=item["userId"],
        type=item.get("type", "general"),
        title=item.get("title", ""),
        content=item.get("content", ""),
        related_goal_id=item.get("relatedGoalId"),
        created_at=item.get("createdAt"),
    )


@router.get("/")
async def list_insights(request: Request) -> list[InsightResponse]:
    repo = InsightsRepository()
    return [_to_response(i) for i in repo.list_all(request.state.user_id)]


@router.post("/run")
async def trigger_proactive(request: Request) -> dict:
    """Manually trigger the proactive engine for the current user.

    Runs plan_review + smart_suggestions and returns any generated content.
    """
    user_id = request.state.user_id
    agent = AgentService()
    results = []

    for prompt_type in ("plan_review", "smart_suggestions"):
        try:
            result = await agent.invoke_proactive(user_id, prompt_type)
            if result:
                results.append({
                    "type": prompt_type,
                    "content": result.get("content", ""),
                    "cardType": result.get("cardType"),
                    "cardData": result.get("cardData"),
                })
        except Exception:
            pass

    return {"triggered": True, "results": results}
