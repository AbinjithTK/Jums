"""Free-tier rate limiting — 10 chat messages per calendar day."""

from __future__ import annotations

from datetime import datetime, timezone

from app.db.repositories.messages import MessagesRepository
from app.exceptions import RateLimitExceededError

FREE_TIER_LIMIT = 10


async def check_rate_limit(user_id: str) -> None:
    """Raise RateLimitExceededError if free-tier daily limit is reached.

    Pro subscribers and access-code holders get unlimited messages.
    For MVP, we just count messages — subscription check comes later.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    repo = MessagesRepository()
    count = repo.count_user_messages_today(user_id, today)
    if count >= FREE_TIER_LIMIT:
        raise RateLimitExceededError(FREE_TIER_LIMIT)
