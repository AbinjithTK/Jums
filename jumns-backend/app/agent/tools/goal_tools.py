"""Agent tools for goal management — full CRUD.

Mirrors OpenClaw's tool pattern: each tool is a plain function
that will be wrapped with user_id injection by the agent service.
"""

from __future__ import annotations

from strands import tool

from app.db.repositories.goals import GoalsRepository
from app.db.repositories.tasks import TasksRepository


_goals_repo = GoalsRepository()
_tasks_repo = TasksRepository()


@tool
def get_goals(user_id: str) -> list[dict]:
    """Retrieve all user goals with progress, categories, and insights.

    Use this to review the user's current goals before providing status
    updates, recommendations, or planning new actions.

    Args:
        user_id: The authenticated user's ID.

    Returns:
        List of goal dicts with id, title, category, progress, total, unit,
        insight, completed, and activeAgent fields.
    """
    goals = _goals_repo.list_all(user_id)
    return [
        {
            "id": g.get("id", g.get("goalId", "")),
            "title": g.get("title", ""),
            "category": g.get("category", ""),
            "progress": g.get("progress", 0),
            "total": g.get("total", 100),
            "unit": g.get("unit", ""),
            "insight": g.get("insight", ""),
            "completed": g.get("completed", False),
            "activeAgent": g.get("activeAgent", ""),
        }
        for g in goals
    ]


@tool
def create_goal(
    user_id: str,
    title: str,
    category: str = "Personal",
    total: int = 100,
    unit: str = "%",
    insight: str = "",
) -> dict:
    """Create a new goal for the user.

    After creating a goal, you MUST immediately call decompose_goal_into_plan
    to break it into milestones, tasks, and reminders. Never leave a goal
    without a plan.

    Args:
        user_id: The authenticated user's ID.
        title: Goal title (e.g. "Run a half marathon").
        category: One of: Health, Learning, Finance, Personal, Professional, Creative.
        total: Target number to reach (e.g. 21 for 21km).
        unit: Unit of measurement (km, lessons, $, books, %, etc).
        insight: Initial motivational insight or strategy tip.

    Returns:
        The created goal dict with its ID.
    """
    goal = _goals_repo.create(user_id, {
        "title": title,
        "category": category,
        "total": total,
        "unit": unit,
        "insight": insight,
    })
    return {
        "id": goal.get("id", goal.get("goalId", "")),
        "title": goal["title"],
        "category": goal["category"],
        "total": goal["total"],
        "unit": goal["unit"],
    }


@tool
def update_goal(
    user_id: str,
    goal_id: str,
    progress: int | None = None,
    insight: str | None = None,
    completed: bool | None = None,
    title: str | None = None,
    category: str | None = None,
    total: int | None = None,
    unit: str | None = None,
) -> dict:
    """Update a goal's progress, insight, completion status, or other fields.

    Use get_goals first to find the goal ID.

    Args:
        user_id: The authenticated user's ID.
        goal_id: The goal ID to update.
        progress: New progress value.
        insight: Updated AI insight about the goal.
        completed: Mark goal as completed.
        title: New title.
        category: New category.
        total: New target total.
        unit: New unit.

    Returns:
        The updated goal dict.
    """
    updates: dict = {}
    if progress is not None:
        updates["progress"] = progress
    if insight is not None:
        updates["insight"] = insight
    if completed is not None:
        updates["completed"] = completed
    if title is not None:
        updates["title"] = title
    if category is not None:
        updates["category"] = category
    if total is not None:
        updates["total"] = total
    if unit is not None:
        updates["unit"] = unit

    try:
        goal = _goals_repo.update(user_id, goal_id, updates)
        return {
            "id": goal.get("id", goal.get("goalId", "")),
            "title": goal.get("title", ""),
            "progress": goal.get("progress", 0),
            "total": goal.get("total", 100),
            "unit": goal.get("unit", ""),
            "completed": goal.get("completed", False),
        }
    except Exception:
        return {"error": "Goal not found"}


@tool
def delete_goal(user_id: str, goal_id: str) -> dict:
    """Delete a goal and all its linked tasks permanently.

    Warn the user before deleting. Use get_goals first to find the goal ID.

    Args:
        user_id: The authenticated user's ID.
        goal_id: The goal ID to delete.

    Returns:
        Confirmation dict.
    """
    # Also clean up linked tasks
    linked_tasks = _tasks_repo.list_all(user_id, goal_id=goal_id)
    for t in linked_tasks:
        try:
            _tasks_repo.delete(user_id, t.get("id", t.get("taskId", "")))
        except Exception:
            pass

    _goals_repo.delete(user_id, goal_id)
    return {"success": True, "deleted": goal_id, "linkedTasksRemoved": len(linked_tasks)}
