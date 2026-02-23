"""POST /api/chat — the main AI conversation endpoint."""

from fastapi import APIRouter, Request

from app.agent.agent_service import AgentService
from app.db.base_repository import utc_now_iso, new_id
from app.middleware.rate_limiter import check_rate_limit
from app.models.requests import ChatRequest
from app.models.responses import MessageResponse

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(request: Request, body: ChatRequest) -> MessageResponse:
    """Send a message to the AI agent and get a response."""
    user_id = request.state.user_id

    # Rate limiting — 10 msgs/day for free users
    await check_rate_limit(user_id)

    # Invoke the agent (returns dict with content, cardType, cardData)
    # Messages are persisted inside agent_service.invoke()
    agent = AgentService()
    result = await agent.invoke(user_id, body.message)

    now = utc_now_iso()
    return MessageResponse(
        id=new_id(),
        user_id=user_id,
        role="assistant",
        type="card" if result.get("cardType") else "text",
        content=result.get("content", ""),
        card_type=result.get("cardType"),
        card_data=result.get("cardData"),
        timestamp=now,
        created_at=now,
    )
