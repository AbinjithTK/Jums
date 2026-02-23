"""Routes for /api/messages — list and delete-all."""

from fastapi import APIRouter, Request, Response

from app.db.repositories.messages import MessagesRepository
from app.models.responses import MessageResponse

router = APIRouter(prefix="/messages", tags=["messages"])


def _to_response(item: dict) -> MessageResponse:
    return MessageResponse(
        id=item.get("id", ""),
        user_id=item["userId"],
        role=item.get("role", "user"),
        type=item.get("type", "text"),
        content=item.get("content"),
        card_type=item.get("cardType"),
        card_data=item.get("cardData"),
        timestamp=item.get("timestamp", item.get("createdAt", "")),
        created_at=item.get("createdAt"),
    )


@router.get("/")
async def list_messages(request: Request) -> list[MessageResponse]:
    repo = MessagesRepository()
    items = repo.list_messages(request.state.user_id)
    return [_to_response(i) for i in items]


@router.delete("/")
async def delete_all_messages(request: Request):
    repo = MessagesRepository()
    repo.delete_all_messages(request.state.user_id)
    return Response(status_code=204)
