"""EventBridge Scheduler Lambda handlers for proactive agent behavior.

Borrowed from OpenClaw's CronService + Projectj's proactive-engine.ts:
- morning_briefing: daily overview of goals, tasks, reminders
- evening_journal: reflection prompts based on the day's activity
- reminder_check: fires every 5 min to check due reminders
- plan_review: periodic goal adaptation + overdue task rescheduling
- smart_suggestions: periodic suggestion generation for engagement
"""

from __future__ import annotations

import asyncio
import logging

from app.agent.agent_service import AgentService
from app.db.repositories.users import UsersRepository

logger = logging.getLogger(__name__)


def _get_eligible_users() -> list[str]:
    """Query all users from DynamoDB.

    In production, filter by timezone and schedule preferences
    (morningTime/eveningTime fields on user records).
    """
    try:
        repo = UsersRepository()
        # Scan for all users — fine for MVP scale.
        # For production, use a GSI or maintain a schedule index.
        items = repo._table.scan(
            ProjectionExpression="userId",
            Limit=500,
        ).get("Items", [])
        return [item["userId"] for item in items if item.get("userId")]
    except Exception:
        logger.exception("Failed to query eligible users")
        return []


def _run_proactive(prompt_type: str) -> dict:
    """Run proactive agent for all eligible users."""
    agent = AgentService()
    user_ids = _get_eligible_users()
    results = {"processed": 0, "delivered": 0, "errors": 0}

    for user_id in user_ids:
        results["processed"] += 1
        try:
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(
                agent.invoke_proactive(user_id, prompt_type)
            )
            loop.close()
            if result is not None:
                results["delivered"] += 1
        except Exception:
            logger.exception("Proactive %s failed for user %s", prompt_type, user_id)
            results["errors"] += 1

    logger.info("Proactive %s: %s", prompt_type, results)
    return results


# ---------------------------------------------------------------------------
# EventBridge Lambda handlers
# ---------------------------------------------------------------------------


def morning_briefing_handler(event, context):
    """EventBridge target: hourly cron, filters by user timezone."""
    results = _run_proactive("morning_briefing")
    return {"statusCode": 200, "body": results}


def evening_journal_handler(event, context):
    """EventBridge target: hourly cron, filters by user timezone."""
    results = _run_proactive("evening_journal")
    return {"statusCode": 200, "body": results}


def reminder_check_handler(event, context):
    """EventBridge target: every 5 minutes."""
    results = _run_proactive("reminder_check")
    return {"statusCode": 200, "body": results}


def plan_review_handler(event, context):
    """EventBridge target: daily at noon UTC.

    Reviews all active goals, runs adapt_plan + reschedule_failed_tasks
    for any that are falling behind.
    """
    results = _run_proactive("plan_review")
    return {"statusCode": 200, "body": results}


def smart_suggest_handler(event, context):
    """EventBridge target: twice daily (morning + afternoon).

    Generates proactive suggestions to keep users engaged.
    """
    results = _run_proactive("smart_suggestions")
    return {"statusCode": 200, "body": results}
