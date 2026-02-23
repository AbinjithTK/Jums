"""Agent tools for vector memory — search, store, recall.

Mirrors OpenClaw's memory system: semantic search over stored facts,
explicit fact storage, and recall by query.
"""

from __future__ import annotations

from strands import tool

from app.memory.memory_service import MemoryService


_memory_service = MemoryService()


@tool
def search_memory(user_id: str, query: str, top_k: int = 5) -> list[dict]:
    """Search the user's long-term memory for relevant context.

    Uses cosine similarity over embeddings stored in S3 with faiss-cpu.
    The search is semantic — finds related memories even if exact words differ.

    Args:
        user_id: The authenticated user's ID.
        query: Natural language search query.
        top_k: Maximum number of results to return.

    Returns:
        List of memory dicts with content, score, and createdAt.
    """
    return _memory_service.search(user_id, query, top_k=top_k)


@tool
def remember_fact(
    user_id: str,
    content: str,
    category: str = "personal_info",
    importance: str = "medium",
) -> dict:
    """Store an important fact about the user in long-term memory.

    Use when the user shares personal information, preferences, habits,
    important dates, or anything worth remembering for future conversations.

    Examples: their name, job, hobbies, dietary preferences, sleep schedule,
    important relationships, workout preferences.

    Args:
        user_id: The authenticated user's ID.
        content: The fact to remember (e.g. "User prefers morning workouts").
        category: One of: preference, personal_info, goal_context, habit,
                  important_date, relationship, health, work, skill, emotional.
        importance: One of: critical, high, medium, low.

    Returns:
        Confirmation dict with stored memory ID.
    """
    try:
        _memory_service.extract_and_store(
            user_id,
            f"[{category}|{importance}] {content}",
        )
        return {"stored": True, "content": content, "category": category}
    except Exception:
        return {"stored": False, "reason": "Memory storage failed"}


@tool
def recall_memories(user_id: str, query: str, limit: int = 5) -> dict:
    """Recall facts about the user from long-term memory.

    Use when you need to remember something the user told you before,
    their preferences, past conversations, or context.

    Args:
        user_id: The authenticated user's ID.
        query: What you're trying to remember (e.g. "user's exercise preferences").
        limit: Max number of memories to recall.

    Returns:
        Dict with found status and list of memories.
    """
    memories = _memory_service.search(user_id, query, top_k=limit)
    if not memories:
        return {"found": False, "message": "No matching memories found"}
    return {
        "found": True,
        "count": len(memories),
        "memories": [
            {
                "content": m.get("content", ""),
                "score": round(m.get("score", 0), 2),
                "createdAt": m.get("createdAt", ""),
            }
            for m in memories
        ],
    }
