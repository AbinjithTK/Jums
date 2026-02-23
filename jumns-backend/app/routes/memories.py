"""Routes for /api/memories — list and delete."""

from fastapi import APIRouter, Request, Response

from app.models.responses import MemoryResponse

router = APIRouter(prefix="/memories", tags=["memories"])


@router.get("/")
async def list_memories(request: Request) -> list[MemoryResponse]:
    """List all memory entries for the user.

    Note: actual implementation requires OpenSearch Serverless.
    Returns empty list until vector memory service is wired (Phase 11).
    """
    return []


@router.delete("/{memory_id}")
async def delete_memory(request: Request, memory_id: str):
    """Delete a specific memory entry.

    Note: actual implementation requires OpenSearch Serverless (Phase 11).
    """
    return Response(status_code=204)
