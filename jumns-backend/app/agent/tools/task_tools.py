"""Agent tools for task management — full CRUD + completion."""

from __future__ import annotations

from strands import tool

from app.db.repositories.tasks import TasksRepository


_tasks_repo = TasksRepository()


@tool
def get_tasks(user_id: str, goal_id: str | None = None) -> list[dict]:
    """Get all tasks, optionally filtered by goal.

    Args:
        user_id: The authenticated user's ID.
        goal_id: Optional goal ID to filter tasks by.

    Returns:
        List of task dicts.
    """
    tasks = _tasks_repo.list_all(user_id, goal_id=goal_id)
    return [
        {
            "id": t.get("id", t.get("taskId", "")),
            "title": t.get("title", ""),
            "time": t.get("time", ""),
            "detail": t.get("detail", ""),
            "type": t.get("type", "task"),
            "completed": t.get("completed", False),
            "active": t.get("active", False),
            "goalId": t.get("goalId"),
            "priority": t.get("priority", "medium"),
            "dueDate": t.get("dueDate"),
            "requiresProof": t.get("requiresProof", False),
            "proofStatus": t.get("proofStatus", "pending"),
        }
        for t in tasks
    ]


@tool
def create_task(
    user_id: str,
    title: str,
    time: str = "",
    detail: str = "",
    type: str = "task",
    goal_id: str | None = None,
    priority: str = "medium",
    due_date: str | None = None,
    requires_proof: bool = False,
) -> dict:
    """Create a new task, habit, or event.

    Link to a goal with goal_id if relevant. Set requires_proof to true
    ONLY for important tasks that need photo/video verification.

    Args:
        user_id: The authenticated user's ID.
        title: Task title.
        time: Scheduled time (e.g. "9:00 AM", "Tomorrow 3 PM").
        detail: Additional context or notes.
        type: One of: task, habit, event.
        goal_id: Link to a goal ID if this task supports a goal.
        priority: Priority level: high, medium, or low.
        due_date: ISO 8601 date string for the deadline.
        requires_proof: Whether this task requires photo/video proof.

    Returns:
        The created task dict.
    """
    data: dict = {
        "title": title,
        "time": time,
        "detail": detail,
        "type": type,
        "priority": priority,
        "requiresProof": requires_proof,
    }
    if goal_id:
        data["goalId"] = goal_id
    if due_date:
        data["dueDate"] = due_date

    task = _tasks_repo.create(user_id, data)
    return {
        "id": task.get("id", task.get("taskId", "")),
        "title": task["title"],
        "type": task.get("type", "task"),
        "goalId": task.get("goalId"),
        "priority": task.get("priority", "medium"),
    }


@tool
def update_task(
    user_id: str,
    task_id: str,
    title: str | None = None,
    time: str | None = None,
    detail: str | None = None,
    active: bool | None = None,
    priority: str | None = None,
    due_date: str | None = None,
    type: str | None = None,
) -> dict:
    """Update a task's details. Cannot mark as completed — use complete_task.

    Args:
        user_id: The authenticated user's ID.
        task_id: The task ID to update.
        title: New title.
        time: New time.
        detail: New detail.
        active: Mark as currently active.
        priority: New priority.
        due_date: New due date.
        type: New type (task/habit/event).

    Returns:
        The updated task dict.
    """
    updates: dict = {}
    if title is not None:
        updates["title"] = title
    if time is not None:
        updates["time"] = time
    if detail is not None:
        updates["detail"] = detail
    if active is not None:
        updates["active"] = active
    if priority is not None:
        updates["priority"] = priority
    if due_date is not None:
        updates["dueDate"] = due_date
    if type is not None:
        updates["type"] = type

    try:
        task = _tasks_repo.update(user_id, task_id, updates)
        return {
            "id": task.get("id", task.get("taskId", "")),
            "title": task.get("title", ""),
            "completed": task.get("completed", False),
        }
    except Exception:
        return {"error": "Task not found"}


@tool
def complete_task(user_id: str, task_id: str) -> dict:
    """Mark a task as completed.

    After completing a task linked to a goal, consider updating the goal's
    progress and checking if the plan needs adaptation.

    Args:
        user_id: The authenticated user's ID.
        task_id: The task to complete.

    Returns:
        The updated task dict.
    """
    try:
        task = _tasks_repo.complete(user_id, task_id, {})
        return {
            "id": task.get("id", task.get("taskId", "")),
            "title": task.get("title", ""),
            "completed": True,
            "goalId": task.get("goalId"),
        }
    except Exception:
        return {"error": "Task not found"}


@tool
def delete_task(user_id: str, task_id: str) -> dict:
    """Delete a task permanently.

    Args:
        user_id: The authenticated user's ID.
        task_id: The task ID to delete.

    Returns:
        Confirmation dict.
    """
    _tasks_repo.delete(user_id, task_id)
    return {"success": True, "deleted": task_id}
