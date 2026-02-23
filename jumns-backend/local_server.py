"""
Jumns Local Dev Server — Strands Agent with real @tool functions.

Uses Strands SDK + GeminiModel. Tools operate on in-memory dicts.
The agent ACTUALLY creates goals/tasks/reminders via tool calls.

Usage:
    cd jumns-backend
    pip install "strands-agents[gemini]" fastapi uvicorn httpx
    python local_server.py

Flutter app connects at: http://10.0.2.2:8000 (Android emulator)
"""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("jumns")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY", "AIzaSyDgSAaTXhsVDc5_ZlaiOkxrKaH5FiztLKU"
)
PORT = int(os.getenv("PORT", "8000"))
FAKE_USER_ID = "local-dev-user"

# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------
db: dict[str, list[dict]] = {
    "users": [],
    "messages": [],
    "goals": [],
    "tasks": [],
    "reminders": [],
    "skills": [],
    "insights": [],
    "memories": [],
}
_user_settings: dict[str, dict] = {}


def _id() -> str:
    return str(uuid.uuid4())


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _find(table: str, uid: str) -> list[dict]:
    return [r for r in db[table] if r.get("userId") == uid]


def _find_one(table: str, uid: str, item_id: str) -> dict | None:
    for r in db[table]:
        if r.get("userId") == uid and r.get("id") == item_id:
            return r
    return None


def _delete_one(table: str, uid: str, item_id: str) -> bool:
    for i, r in enumerate(db[table]):
        if r.get("userId") == uid and r.get("id") == item_id:
            db[table].pop(i)
            return True
    return False


def _compute_next_run(schedule_type: str, schedule_value: str) -> str | None:
    """Compute the next run time for a cron job based on its schedule type."""
    now = datetime.now(timezone.utc)
    try:
        if schedule_type == "once":
            if schedule_value:
                target = datetime.fromisoformat(schedule_value.replace("Z", "+00:00"))
                return target.isoformat() if target > now else None
            return None
        elif schedule_type == "daily":
            # schedule_value = "HH:MM"
            parts = schedule_value.split(":")
            hour = int(parts[0]) if len(parts) > 0 else 8
            minute = int(parts[1]) if len(parts) > 1 else 0
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            return target.isoformat()
        elif schedule_type == "weekly":
            # schedule_value = "Monday 09:00"
            parts = schedule_value.split()
            day_name = parts[0] if parts else "Monday"
            time_str = parts[1] if len(parts) > 1 else "09:00"
            time_parts = time_str.split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            days_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                        "friday": 4, "saturday": 5, "sunday": 6}
            target_day = days_map.get(day_name.lower(), 0)
            days_ahead = target_day - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            target = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=7)
            return target.isoformat()
        elif schedule_type == "interval":
            # schedule_value = minutes as string
            minutes = int(schedule_value) if schedule_value else 30
            return (now + timedelta(minutes=minutes)).isoformat()
        elif schedule_type == "cron":
            # Basic cron expression — for local dev, just compute approximate next
            # Full cron parsing would need a library; approximate with daily
            return (now + timedelta(hours=1)).isoformat()
        else:
            return None
    except (ValueError, TypeError, IndexError):
        return (now + timedelta(hours=1)).isoformat()


# ═══════════════════════════════════════════════════════════════════════════
# STRANDS @tool FUNCTIONS — operate on in-memory db
# ═══════════════════════════════════════════════════════════════════════════

from strands import tool

# ── Goals ──────────────────────────────────────────────────────────────────

@tool
def get_goals(user_id: str = FAKE_USER_ID) -> list[dict]:
    """Retrieve all user goals with progress, categories, and insights.

    Args:
        user_id: The authenticated user's ID.

    Returns:
        List of goal dicts.
    """
    return [
        {k: g[k] for k in ("id", "title", "category", "progress", "total", "unit", "insight", "completed") if k in g}
        for g in _find("goals", user_id)
    ]


@tool
def create_goal(
    title: str,
    category: str = "Personal",
    total: int = 100,
    unit: str = "%",
    insight: str = "",
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Create a new goal. After creating, ALWAYS call decompose_goal_into_plan.

    Args:
        title: Goal title.
        category: Health, Learning, Finance, Personal, Professional, Creative.
        total: Target number.
        unit: Unit of measurement.
        insight: Initial motivational insight.
        user_id: The authenticated user's ID.

    Returns:
        The created goal dict with its ID.
    """
    goal = {
        "id": _id(), "userId": user_id, "title": title, "category": category,
        "progress": 0, "total": total, "unit": unit, "insight": insight,
        "completed": False, "activeAgent": "", "createdAt": _now(),
    }
    db["goals"].append(goal)
    logger.info("✅ Created goal: %s (%s)", title, goal["id"])
    return {"id": goal["id"], "title": title, "category": category, "total": total, "unit": unit}


@tool
def update_goal(
    goal_id: str,
    progress: int | None = None,
    insight: str | None = None,
    completed: bool | None = None,
    title: str | None = None,
    category: str | None = None,
    total: int | None = None,
    unit: str | None = None,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Update a goal's fields.

    Args:
        goal_id: The goal ID to update.
        progress: New progress value.
        insight: Updated insight.
        completed: Mark as completed.
        title: New title.
        category: New category.
        total: New target.
        unit: New unit.
        user_id: The authenticated user's ID.

    Returns:
        The updated goal dict.
    """
    g = _find_one("goals", user_id, goal_id)
    if not g:
        return {"error": "Goal not found"}
    for k, v in [("progress", progress), ("insight", insight), ("completed", completed),
                 ("title", title), ("category", category), ("total", total), ("unit", unit)]:
        if v is not None:
            g[k] = v
    return {"id": g["id"], "title": g["title"], "progress": g["progress"], "total": g["total"], "completed": g["completed"]}


@tool
def delete_goal(goal_id: str, user_id: str = FAKE_USER_ID) -> dict:
    """Delete a goal and its linked tasks.

    Args:
        goal_id: The goal ID to delete.
        user_id: The authenticated user's ID.

    Returns:
        Confirmation dict.
    """
    linked = [t for t in db["tasks"] if t.get("userId") == user_id and t.get("goalId") == goal_id]
    for t in linked:
        _delete_one("tasks", user_id, t["id"])
    _delete_one("goals", user_id, goal_id)
    return {"success": True, "deleted": goal_id, "linkedTasksRemoved": len(linked)}


# ── Tasks ──────────────────────────────────────────────────────────────────

@tool
def get_tasks(goal_id: str | None = None, user_id: str = FAKE_USER_ID) -> list[dict]:
    """Get all tasks, optionally filtered by goal.

    Args:
        goal_id: Optional goal ID filter.
        user_id: The authenticated user's ID.

    Returns:
        List of task dicts.
    """
    tasks = _find("tasks", user_id)
    if goal_id:
        tasks = [t for t in tasks if t.get("goalId") == goal_id]
    return [
        {k: t.get(k) for k in ("id", "title", "time", "detail", "type", "completed", "active",
                                 "goalId", "priority", "dueDate", "requiresProof", "proofStatus")}
        for t in tasks
    ]


@tool
def create_task(
    title: str,
    time: str = "",
    detail: str = "",
    type: str = "task",
    goal_id: str | None = None,
    priority: str = "medium",
    due_date: str | None = None,
    requires_proof: bool = False,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Create a new task, habit, or event.

    Args:
        title: Task title.
        time: Scheduled time.
        detail: Additional context.
        type: task, habit, or event.
        goal_id: Link to a goal.
        priority: high, medium, low.
        due_date: ISO date for deadline.
        requires_proof: Whether proof is needed.
        user_id: The authenticated user's ID.

    Returns:
        The created task dict.
    """
    task = {
        "id": _id(), "userId": user_id, "title": title, "time": time,
        "detail": detail, "type": type, "completed": False, "active": False,
        "goalId": goal_id, "priority": priority, "dueDate": due_date or "",
        "requiresProof": requires_proof, "proofStatus": "pending", "createdAt": _now(),
    }
    db["tasks"].append(task)
    logger.info("✅ Created task: %s (goal=%s)", title, goal_id or "none")
    return {"id": task["id"], "title": title, "type": type, "goalId": goal_id, "priority": priority}


@tool
def update_task(
    task_id: str,
    title: str | None = None,
    time: str | None = None,
    detail: str | None = None,
    active: bool | None = None,
    priority: str | None = None,
    due_date: str | None = None,
    type: str | None = None,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Update a task's details.

    Args:
        task_id: The task ID.
        title: New title.
        time: New time.
        detail: New detail.
        active: Mark active.
        priority: New priority.
        due_date: New due date.
        type: New type.
        user_id: The authenticated user's ID.

    Returns:
        Updated task dict.
    """
    t = _find_one("tasks", user_id, task_id)
    if not t:
        return {"error": "Task not found"}
    for k, v in [("title", title), ("time", time), ("detail", detail), ("active", active),
                 ("priority", priority), ("dueDate", due_date), ("type", type)]:
        if v is not None:
            t[k] = v
    return {"id": t["id"], "title": t["title"], "completed": t["completed"]}


@tool
def complete_task(task_id: str, user_id: str = FAKE_USER_ID) -> dict:
    """Mark a task as completed.

    Args:
        task_id: The task to complete.
        user_id: The authenticated user's ID.

    Returns:
        Updated task dict.
    """
    t = _find_one("tasks", user_id, task_id)
    if not t:
        return {"error": "Task not found"}
    t["completed"] = True
    logger.info("✅ Completed task: %s", t["title"])
    return {"id": t["id"], "title": t["title"], "completed": True, "goalId": t.get("goalId")}


@tool
def delete_task(task_id: str, user_id: str = FAKE_USER_ID) -> dict:
    """Delete a task.

    Args:
        task_id: The task ID.
        user_id: The authenticated user's ID.

    Returns:
        Confirmation dict.
    """
    _delete_one("tasks", user_id, task_id)
    return {"success": True, "deleted": task_id}


# ── Reminders ──────────────────────────────────────────────────────────────

@tool
def get_reminders(user_id: str = FAKE_USER_ID) -> list[dict]:
    """Get all reminders.

    Args:
        user_id: The authenticated user's ID.

    Returns:
        List of reminder dicts.
    """
    return [
        {k: r.get(k) for k in ("id", "title", "time", "active", "goalId", "snoozeCount", "snoozedUntil", "originalTime")}
        for r in _find("reminders", user_id)
    ]


@tool
def create_reminder(
    title: str,
    time: str = "",
    goal_id: str | None = None,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Create a new reminder. ALWAYS create reminders alongside tasks in plans.

    Args:
        title: What to remind about.
        time: When — e.g. "Every morning 8 AM", "Weekdays 7 PM".
        goal_id: Link to a goal.
        user_id: The authenticated user's ID.

    Returns:
        The created reminder dict.
    """
    reminder = {
        "id": _id(), "userId": user_id, "title": title, "time": time,
        "active": True, "goalId": goal_id, "snoozeCount": 0,
        "snoozedUntil": None, "originalTime": time, "createdAt": _now(),
    }
    db["reminders"].append(reminder)
    logger.info("✅ Created reminder: %s", title)
    return {"id": reminder["id"], "title": title, "time": time}


@tool
def update_reminder(
    reminder_id: str,
    title: str | None = None,
    time: str | None = None,
    active: bool | None = None,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Update a reminder.

    Args:
        reminder_id: The reminder ID.
        title: New title.
        time: New schedule.
        active: Pause/resume.
        user_id: The authenticated user's ID.

    Returns:
        Updated reminder dict.
    """
    r = _find_one("reminders", user_id, reminder_id)
    if not r:
        return {"error": "Reminder not found"}
    for k, v in [("title", title), ("time", time), ("active", active)]:
        if v is not None:
            r[k] = v
    return {"id": r["id"], "title": r["title"], "time": r["time"], "active": r["active"]}


@tool
def snooze_reminder(
    reminder_id: str,
    minutes: int = 30,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Snooze a reminder forward.

    Args:
        reminder_id: The reminder to snooze.
        minutes: Minutes to push forward (default 30).
        user_id: The authenticated user's ID.

    Returns:
        Updated reminder with snooze info.
    """
    r = _find_one("reminders", user_id, reminder_id)
    if not r:
        return {"error": "Reminder not found"}
    r["snoozeCount"] = r.get("snoozeCount", 0) + 1
    snoozed_until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    r["snoozedUntil"] = snoozed_until.isoformat()
    resp = {"id": r["id"], "title": r["title"], "snoozeCount": r["snoozeCount"], "snoozedUntil": r["snoozedUntil"]}
    if r["snoozeCount"] >= 3:
        resp["warning"] = f"Snoozed {r['snoozeCount']} times. Consider rescheduling."
    return resp


@tool
def delete_reminder(reminder_id: str, user_id: str = FAKE_USER_ID) -> dict:
    """Delete a reminder.

    Args:
        reminder_id: The reminder ID.
        user_id: The authenticated user's ID.

    Returns:
        Confirmation dict.
    """
    _delete_one("reminders", user_id, reminder_id)
    return {"success": True, "deleted": reminder_id}


# ── Planning (AUTONOMOUS) ─────────────────────────────────────────────────

@tool
def decompose_goal_into_plan(
    goal_id: str,
    milestones_json: str,
    tasks_json: str,
    reminders_json: str,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Decompose a goal into milestones, tasks, and reminders — all at once.

    This is the CORE planning tool. ALWAYS call after creating a goal.

    Args:
        goal_id: The goal to plan for.
        milestones_json: JSON array of milestone objects.
        tasks_json: JSON array of task objects with title, detail, type, priority, due_date.
        reminders_json: JSON array of reminder objects with title, time.
        user_id: The authenticated user's ID.

    Returns:
        Summary of the created plan.
    """
    g = _find_one("goals", user_id, goal_id)
    if not g:
        return {"error": f"Goal {goal_id} not found"}

    def _parse_json_or_list(val):
        if isinstance(val, list):
            return val
        if isinstance(val, str) and val.strip():
            try:
                parsed = json.loads(val)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    milestones = _parse_json_or_list(milestones_json)
    tasks = _parse_json_or_list(tasks_json)
    reminders = _parse_json_or_list(reminders_json)

    logger.info("📋 decompose args: milestones_json type=%s, tasks_json type=%s, reminders_json type=%s",
                type(milestones_json).__name__, type(tasks_json).__name__, type(reminders_json).__name__)
    logger.info("📋 parsed: %d milestones, %d tasks, %d reminders", len(milestones), len(tasks), len(reminders))

    created_tasks = []
    created_reminders = []

    # Store milestones as insights
    goal_title = next((g["title"] for g in db["goals"] if g["id"] == goal_id), "your goal")
    for i, ms in enumerate(milestones):
        ms_title = ms.get("title", "")
        target_date = ms.get("target_date", "")
        date_hint = f" — target: {target_date}" if target_date else ""
        db["insights"].append({
            "id": _id(), "userId": user_id, "type": "milestone",
            "title": f"Milestone {i+1}: {ms_title}",
            "content": f"Part of \"{goal_title}\". {ms_title}{date_hint}. Keep pushing!",
            "priority": "medium", "read": False, "dismissed": False,
            "relatedGoalId": goal_id, "createdAt": _now(),
        })

    # Create tasks
    for t in tasks:
        due = t.get("due_date", "")
        if not due and t.get("day_offset"):
            due = (datetime.now(timezone.utc) + timedelta(days=int(t["day_offset"]))).strftime("%Y-%m-%d")
        task = {
            "id": _id(), "userId": user_id, "title": t.get("title", "Untitled"),
            "detail": t.get("detail", ""), "type": t.get("type", "task"),
            "completed": False, "active": False, "goalId": goal_id,
            "priority": t.get("priority", "medium"), "dueDate": due,
            "requiresProof": False, "proofStatus": "pending", "time": "", "createdAt": _now(),
        }
        db["tasks"].append(task)
        created_tasks.append({"id": task["id"], "title": task["title"], "dueDate": due})

    # Create reminders
    for r in reminders:
        rem = {
            "id": _id(), "userId": user_id, "title": r.get("title", ""),
            "time": r.get("time", ""), "active": True, "goalId": goal_id,
            "snoozeCount": 0, "snoozedUntil": None, "originalTime": r.get("time", ""), "createdAt": _now(),
        }
        db["reminders"].append(rem)
        created_reminders.append({"id": rem["id"], "title": rem["title"]})

    # Update goal insight
    g["insight"] = f"Plan active: {len(milestones)} milestones, {len(created_tasks)} tasks, {len(created_reminders)} reminders"
    g["activeAgent"] = "planner"

    logger.info("📋 Plan created for '%s': %d milestones, %d tasks, %d reminders",
                g["title"], len(milestones), len(created_tasks), len(created_reminders))
    return {
        "goalId": goal_id, "goalTitle": g["title"],
        "milestonesCreated": len(milestones), "tasksCreated": len(created_tasks),
        "remindersCreated": len(created_reminders),
        "tasks": created_tasks[:10], "reminders": created_reminders[:5],
    }


@tool
def adapt_plan(goal_id: str, user_id: str = FAKE_USER_ID) -> dict:
    """Review a goal's progress and recommend adjustments.

    Args:
        goal_id: The goal to review.
        user_id: The authenticated user's ID.

    Returns:
        Analysis with status, stats, and recommendations.
    """
    g = _find_one("goals", user_id, goal_id)
    if not g:
        return {"error": f"Goal {goal_id} not found"}

    all_tasks = [t for t in _find("tasks", user_id) if t.get("goalId") == goal_id]
    completed = [t for t in all_tasks if t.get("completed")]
    pending = [t for t in all_tasks if not t.get("completed")]
    today = _today()
    overdue = [t for t in pending if t.get("dueDate") and t["dueDate"] < today]

    total = g.get("total", 100)
    progress = g.get("progress", 0)
    pct = round((progress / total) * 100) if total > 0 else 0
    velocity = round((len(completed) / len(all_tasks)) * 100) if all_tasks else 0

    if pct >= 100:
        status = "completed"
    elif len(overdue) > len(pending) // 2 and pending:
        status = "falling_behind"
    elif velocity >= 60:
        status = "on_track"
    else:
        status = "needs_attention"

    recs = []
    if not all_tasks:
        recs.append("No tasks. Use decompose_goal_into_plan.")
    if overdue:
        recs.append(f"{len(overdue)} overdue tasks. Use reschedule_failed_tasks.")
    if len(completed) == len(all_tasks) and all_tasks and pct < 100:
        recs.append("All tasks done but goal incomplete. Create new tasks.")

    return {
        "goalId": goal_id, "goalTitle": g["title"], "status": status,
        "progress": progress, "total": total, "percentComplete": pct,
        "taskVelocity": velocity, "totalTasks": len(all_tasks),
        "completedTasks": len(completed), "pendingTasks": len(pending),
        "overdueTasks": len(overdue), "recommendations": recs,
    }


@tool
def reschedule_failed_tasks(
    goal_id: str,
    days_forward: int = 3,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Reschedule overdue tasks by pushing due dates forward.

    Args:
        goal_id: The goal whose tasks to reschedule.
        days_forward: Days to push forward (default 3).
        user_id: The authenticated user's ID.

    Returns:
        Summary of rescheduled tasks.
    """
    all_tasks = [t for t in _find("tasks", user_id) if t.get("goalId") == goal_id]
    today = _today()
    rescheduled = []
    for t in all_tasks:
        if t.get("completed"):
            continue
        dd = t.get("dueDate", "")
        if dd and dd < today:
            new_dd = (datetime.now(timezone.utc) + timedelta(days=days_forward)).strftime("%Y-%m-%d")
            t["dueDate"] = new_dd
            rescheduled.append({"id": t["id"], "title": t["title"], "oldDate": dd, "newDate": new_dd})
    return {"goalId": goal_id, "rescheduledCount": len(rescheduled), "daysPushed": days_forward, "tasks": rescheduled}


@tool
def reschedule_plan(
    goal_id: str,
    start_date: str = "",
    spread_days: int = 7,
    preserve_order: bool = True,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Reschedule ALL pending tasks for a goal into a new time window.

    Use this when the user says things like "reschedule to next week",
    "spread it over 2 weeks", "push everything to start Monday", etc.

    Args:
        goal_id: The goal whose plan to reschedule.
        start_date: ISO date (YYYY-MM-DD) for the new start. Defaults to tomorrow.
        spread_days: Number of days to spread tasks across (default 7 = one week).
        preserve_order: Keep original task ordering when redistributing.
        user_id: The authenticated user's ID.

    Returns:
        Summary of all rescheduled tasks with old and new dates.
    """
    g = _find_one("goals", user_id, goal_id)
    if not g:
        return {"error": f"Goal {goal_id} not found"}

    all_tasks = [t for t in _find("tasks", user_id) if t.get("goalId") == goal_id and not t.get("completed")]
    if not all_tasks:
        return {"goalId": goal_id, "message": "No pending tasks to reschedule"}

    # Determine start date
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            start = datetime.now(timezone.utc) + timedelta(days=1)
    else:
        start = datetime.now(timezone.utc) + timedelta(days=1)

    # Sort by current due date if preserving order
    if preserve_order:
        all_tasks.sort(key=lambda t: t.get("dueDate") or "9999-99-99")

    # Distribute tasks evenly across the spread window
    rescheduled = []
    task_count = len(all_tasks)
    for i, t in enumerate(all_tasks):
        day_offset = int((i / max(task_count, 1)) * spread_days)
        new_date = (start + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        old_date = t.get("dueDate", "")
        t["dueDate"] = new_date
        rescheduled.append({
            "id": t["id"], "title": t["title"],
            "oldDate": old_date, "newDate": new_date,
        })

    # Also reschedule linked reminders
    reminders_updated = 0
    linked_reminders = [r for r in _find("reminders", user_id) if r.get("goalId") == goal_id and r.get("active")]
    for r in linked_reminders:
        # Keep the time pattern but note the reschedule
        r["snoozedUntil"] = None
        r["snoozeCount"] = 0
        reminders_updated += 1

    # Update goal insight
    end_date = (start + timedelta(days=spread_days - 1)).strftime("%Y-%m-%d")
    g["insight"] = f"Plan rescheduled: {task_count} tasks spread {start.strftime('%Y-%m-%d')} to {end_date}"

    logger.info("📅 Rescheduled plan for '%s': %d tasks over %d days starting %s",
                g["title"], task_count, spread_days, start.strftime("%Y-%m-%d"))
    return {
        "goalId": goal_id, "goalTitle": g["title"],
        "rescheduledCount": task_count, "remindersReset": reminders_updated,
        "startDate": start.strftime("%Y-%m-%d"), "endDate": end_date,
        "spreadDays": spread_days, "tasks": rescheduled,
    }


@tool
def shift_plan(
    goal_id: str,
    days: int = 7,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Shift ALL pending tasks and reminders for a goal forward or backward by N days.

    Use this when the user says "push everything back a week" or "move it all forward 3 days".

    Args:
        goal_id: The goal whose plan to shift.
        days: Number of days to shift (positive = forward, negative = backward).
        user_id: The authenticated user's ID.

    Returns:
        Summary of shifted tasks.
    """
    g = _find_one("goals", user_id, goal_id)
    if not g:
        return {"error": f"Goal {goal_id} not found"}

    all_tasks = [t for t in _find("tasks", user_id) if t.get("goalId") == goal_id and not t.get("completed")]
    shifted = []
    for t in all_tasks:
        old_date = t.get("dueDate", "")
        if old_date:
            try:
                d = datetime.strptime(old_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                new_d = d + timedelta(days=days)
                t["dueDate"] = new_d.strftime("%Y-%m-%d")
                shifted.append({"id": t["id"], "title": t["title"], "oldDate": old_date, "newDate": t["dueDate"]})
            except ValueError:
                pass
        else:
            # No date set — assign relative to today
            new_d = datetime.now(timezone.utc) + timedelta(days=max(1, days))
            t["dueDate"] = new_d.strftime("%Y-%m-%d")
            shifted.append({"id": t["id"], "title": t["title"], "oldDate": "(none)", "newDate": t["dueDate"]})

    g["insight"] = f"Plan shifted by {days:+d} days — {len(shifted)} tasks updated"
    logger.info("📅 Shifted plan for '%s' by %+d days: %d tasks", g["title"], days, len(shifted))
    return {
        "goalId": goal_id, "goalTitle": g["title"],
        "shiftedCount": len(shifted), "daysMoved": days,
        "tasks": shifted,
    }


@tool
def bulk_update_tasks(
    task_ids_json: str,
    due_date: str | None = None,
    priority: str | None = None,
    active: bool | None = None,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Update multiple tasks at once — set due date, priority, or active status in bulk.

    Args:
        task_ids_json: JSON array of task ID strings.
        due_date: New due date for all tasks (YYYY-MM-DD).
        priority: New priority for all tasks (high/medium/low).
        active: Set active status for all tasks.
        user_id: The authenticated user's ID.

    Returns:
        Summary of updated tasks.
    """
    try:
        task_ids = json.loads(task_ids_json) if isinstance(task_ids_json, str) else task_ids_json
    except (json.JSONDecodeError, TypeError):
        return {"error": "Invalid task_ids_json"}

    updated = []
    for tid in task_ids:
        t = _find_one("tasks", user_id, str(tid))
        if not t:
            continue
        if due_date is not None:
            t["dueDate"] = due_date
        if priority is not None:
            t["priority"] = priority
        if active is not None:
            t["active"] = active
        updated.append({"id": t["id"], "title": t["title"], "dueDate": t.get("dueDate"), "priority": t.get("priority")})

    return {"updatedCount": len(updated), "tasks": updated}


@tool
def clear_and_replan(
    goal_id: str,
    keep_completed: bool = True,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Delete all pending tasks and reminders for a goal so the agent can create a fresh plan.

    Use this when the user wants to start over with a completely new schedule.

    Args:
        goal_id: The goal to clear.
        keep_completed: Whether to keep already-completed tasks (default True).
        user_id: The authenticated user's ID.

    Returns:
        Summary of what was cleared.
    """
    g = _find_one("goals", user_id, goal_id)
    if not g:
        return {"error": f"Goal {goal_id} not found"}

    # Remove pending tasks
    tasks_before = len(db["tasks"])
    if keep_completed:
        db["tasks"] = [t for t in db["tasks"] if not (
            t.get("userId") == user_id and t.get("goalId") == goal_id and not t.get("completed")
        )]
    else:
        db["tasks"] = [t for t in db["tasks"] if not (
            t.get("userId") == user_id and t.get("goalId") == goal_id
        )]
    tasks_removed = tasks_before - len(db["tasks"])

    # Remove linked reminders
    rems_before = len(db["reminders"])
    db["reminders"] = [r for r in db["reminders"] if not (
        r.get("userId") == user_id and r.get("goalId") == goal_id
    )]
    rems_removed = rems_before - len(db["reminders"])

    # Reset goal progress metadata
    g["insight"] = "Plan cleared — ready for a fresh start"
    g["activeAgent"] = ""

    logger.info("🗑️ Cleared plan for '%s': %d tasks, %d reminders removed", g["title"], tasks_removed, rems_removed)
    return {
        "goalId": goal_id, "goalTitle": g["title"],
        "tasksRemoved": tasks_removed, "remindersRemoved": rems_removed,
        "message": "Plan cleared. Call decompose_goal_into_plan to create a new plan.",
    }


# ── Cron Jobs (Scheduled Automation) ──────────────────────────────────────

# In-memory cron job store
_cron_jobs: list[dict] = []
_cron_next_check: float = 0


@tool
def cron_add(
    name: str,
    schedule_type: str,
    action_message: str,
    schedule_value: str = "",
    description: str = "",
    enabled: bool = True,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Create a scheduled cron job that runs automatically.

    Use this when the user says "remind me every morning", "check my goals weekly",
    "run a daily briefing at 8am", etc.

    Args:
        name: Short name for the job (e.g. "Morning Briefing").
        schedule_type: One of: "once", "daily", "weekly", "interval", "cron".
        action_message: The message/prompt to execute when the job fires.
        schedule_value: Schedule details depending on type:
            - once: ISO datetime (e.g. "2026-03-01T08:00:00Z")
            - daily: Time in HH:MM format (e.g. "08:00")
            - weekly: Day and time (e.g. "Monday 09:00")
            - interval: Minutes between runs (e.g. "30")
            - cron: Cron expression (e.g. "0 8 * * *")
        description: What this job does.
        enabled: Whether the job starts enabled.
        user_id: The authenticated user's ID.

    Returns:
        The created cron job.
    """
    job = {
        "id": _id(), "userId": user_id, "name": name,
        "description": description, "enabled": enabled,
        "scheduleType": schedule_type, "scheduleValue": schedule_value,
        "actionMessage": action_message,
        "createdAt": _now(), "updatedAt": _now(),
        "lastRunAt": None, "nextRunAt": None,
        "runCount": 0, "lastStatus": None,
    }
    # Compute next run
    job["nextRunAt"] = _compute_next_run(schedule_type, schedule_value)
    _cron_jobs.append(job)
    logger.info("⏰ Created cron job: %s (%s %s)", name, schedule_type, schedule_value)
    return {
        "id": job["id"], "name": name, "scheduleType": schedule_type,
        "scheduleValue": schedule_value, "enabled": enabled,
        "nextRunAt": job["nextRunAt"],
    }


@tool
def cron_list(include_disabled: bool = False, user_id: str = FAKE_USER_ID) -> list[dict]:
    """List all scheduled cron jobs.

    Args:
        include_disabled: Whether to include disabled jobs.
        user_id: The authenticated user's ID.

    Returns:
        List of cron jobs.
    """
    jobs = [j for j in _cron_jobs if j.get("userId") == user_id]
    if not include_disabled:
        jobs = [j for j in jobs if j.get("enabled", True)]
    return [{
        "id": j["id"], "name": j["name"], "description": j.get("description", ""),
        "scheduleType": j["scheduleType"], "scheduleValue": j["scheduleValue"],
        "enabled": j["enabled"], "nextRunAt": j.get("nextRunAt"),
        "lastRunAt": j.get("lastRunAt"), "runCount": j.get("runCount", 0),
    } for j in jobs]


@tool
def cron_update(
    job_id: str,
    name: str | None = None,
    schedule_type: str | None = None,
    schedule_value: str | None = None,
    action_message: str | None = None,
    enabled: bool | None = None,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Update a cron job's schedule, message, or enabled status.

    Args:
        job_id: The cron job ID.
        name: New name.
        schedule_type: New schedule type.
        schedule_value: New schedule value.
        action_message: New action message.
        enabled: Enable or disable.
        user_id: The authenticated user's ID.

    Returns:
        Updated cron job.
    """
    job = next((j for j in _cron_jobs if j["id"] == job_id and j.get("userId") == user_id), None)
    if not job:
        return {"error": "Cron job not found"}
    if name is not None:
        job["name"] = name
    if schedule_type is not None:
        job["scheduleType"] = schedule_type
    if schedule_value is not None:
        job["scheduleValue"] = schedule_value
    if action_message is not None:
        job["actionMessage"] = action_message
    if enabled is not None:
        job["enabled"] = enabled
    job["updatedAt"] = _now()
    # Recompute next run
    job["nextRunAt"] = _compute_next_run(job["scheduleType"], job["scheduleValue"])
    return {
        "id": job["id"], "name": job["name"],
        "scheduleType": job["scheduleType"], "scheduleValue": job["scheduleValue"],
        "enabled": job["enabled"], "nextRunAt": job["nextRunAt"],
    }


@tool
def cron_remove(job_id: str, user_id: str = FAKE_USER_ID) -> dict:
    """Delete a cron job.

    Args:
        job_id: The cron job ID.
        user_id: The authenticated user's ID.

    Returns:
        Confirmation.
    """
    global _cron_jobs
    before = len(_cron_jobs)
    _cron_jobs = [j for j in _cron_jobs if not (j["id"] == job_id and j.get("userId") == user_id)]
    return {"success": len(_cron_jobs) < before, "deleted": job_id}


@tool
def cron_run(job_id: str, user_id: str = FAKE_USER_ID) -> dict:
    """Manually trigger a cron job to run immediately.

    Args:
        job_id: The cron job ID.
        user_id: The authenticated user's ID.

    Returns:
        Execution result.
    """
    job = next((j for j in _cron_jobs if j["id"] == job_id and j.get("userId") == user_id), None)
    if not job:
        return {"error": "Cron job not found"}
    job["lastRunAt"] = _now()
    job["runCount"] = job.get("runCount", 0) + 1
    job["lastStatus"] = "ok"
    job["nextRunAt"] = _compute_next_run(job["scheduleType"], job["scheduleValue"])
    return {
        "id": job["id"], "name": job["name"],
        "ran": True, "actionMessage": job["actionMessage"],
        "message": f"Job '{job['name']}' executed. Action: {job['actionMessage'][:100]}",
    }


# ── MCP Server Management ────────────────────────────────────────────────

@tool
def connect_mcp_server(
    name: str,
    server_url: str,
    description: str = "",
    auth_token: str = "",
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Register and connect an MCP (Model Context Protocol) server as a skill.

    Use this when the user says "connect to my MCP server", "add an MCP tool",
    "link my calendar MCP", etc.

    Args:
        name: Display name for the MCP server (e.g. "Google Calendar", "Notion").
        server_url: The MCP server URL or endpoint.
        description: What this MCP server provides.
        auth_token: Optional auth token for the server.
        user_id: The authenticated user's ID.

    Returns:
        The registered MCP skill.
    """
    skill = {
        "id": _id(), "userId": user_id, "name": name,
        "type": "mcp_server", "description": description,
        "category": "mcp", "status": "connected",
        "serverUrl": server_url, "authToken": auth_token,
        "enabled": True, "createdAt": _now(),
    }
    db["skills"].append(skill)
    logger.info("🔌 Connected MCP server: %s at %s", name, server_url)
    return {
        "id": skill["id"], "name": name, "status": "connected",
        "serverUrl": server_url, "message": f"MCP server '{name}' connected successfully.",
    }


@tool
def disconnect_mcp_server(
    skill_id: str,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Disconnect and remove an MCP server.

    Args:
        skill_id: The skill/MCP server ID to disconnect.
        user_id: The authenticated user's ID.

    Returns:
        Confirmation.
    """
    s = _find_one("skills", user_id, skill_id)
    if not s:
        return {"error": "MCP server not found"}
    s["status"] = "disconnected"
    s["enabled"] = False
    logger.info("🔌 Disconnected MCP server: %s", s.get("name", skill_id))
    return {"id": skill_id, "name": s.get("name"), "status": "disconnected"}


@tool
def list_mcp_servers(user_id: str = FAKE_USER_ID) -> list[dict]:
    """List all connected MCP servers.

    Args:
        user_id: The authenticated user's ID.

    Returns:
        List of MCP server skills.
    """
    skills = [s for s in _find("skills", user_id) if s.get("category") == "mcp"]
    return [{
        "id": s["id"], "name": s["name"], "status": s.get("status", "unknown"),
        "serverUrl": s.get("serverUrl", ""), "description": s.get("description", ""),
    } for s in skills]


# ── Calendar & Scheduling ─────────────────────────────────────────────────

@tool
def get_schedule(
    date: str = "",
    days: int = 1,
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Get the user's schedule for a date range.

    Args:
        date: ISO date (YYYY-MM-DD). Defaults to today.
        days: Number of days to include.
        user_id: The authenticated user's ID.

    Returns:
        Schedule grouped by date.
    """
    now = datetime.now(timezone.utc)
    start = now
    if date:
        try:
            start = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    all_tasks = _find("tasks", user_id)
    all_reminders = _find("reminders", user_id)
    schedule = {}

    for d in range(days):
        current = start + timedelta(days=d)
        day_iso = current.strftime("%Y-%m-%d")
        day_tasks = [t for t in all_tasks if t.get("dueDate") == day_iso]
        day_reminders = []
        for r in all_reminders:
            if not r.get("active", True):
                continue
            ts = r.get("time", "").lower()
            if any(kw in ts for kw in ["every", "daily", "morning", "evening"]) or \
               ("weekday" in ts and current.weekday() < 5) or \
               current.strftime("%A").lower() in ts or day_iso in r.get("time", ""):
                day_reminders.append({"id": r["id"], "title": r["title"], "time": r["time"]})

        schedule[day_iso] = {
            "dayName": current.strftime("%A"),
            "tasks": [{"id": t["id"], "title": t["title"], "type": t.get("type", "task"),
                        "priority": t.get("priority", "medium"), "completed": t.get("completed", False)}
                       for t in day_tasks],
            "reminders": day_reminders,
            "totalItems": len(day_tasks) + len(day_reminders),
        }

    return {"startDate": start.strftime("%Y-%m-%d"), "days": days, "schedule": schedule}


@tool
def assign_task_to_date(task_id: str, date: str, user_id: str = FAKE_USER_ID) -> dict:
    """Assign a task to a specific calendar date.

    Args:
        task_id: The task to assign.
        date: ISO date (YYYY-MM-DD).
        user_id: The authenticated user's ID.

    Returns:
        Updated task.
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"error": f"Invalid date: {date}"}
    t = _find_one("tasks", user_id, task_id)
    if not t:
        return {"error": "Task not found"}
    t["dueDate"] = date
    return {"id": t["id"], "title": t["title"], "dueDate": date, "assigned": True}


@tool
def analyze_goal_timeline(goal_id: str, user_id: str = FAKE_USER_ID) -> dict:
    """Analyze whether a goal is short/medium/long-term.

    Args:
        goal_id: The goal to analyze.
        user_id: The authenticated user's ID.

    Returns:
        Timeline classification and planning recommendations.
    """
    g = _find_one("goals", user_id, goal_id)
    if not g:
        return {"error": f"Goal {goal_id} not found"}

    total = g.get("total", 100)
    progress = g.get("progress", 0)
    remaining = total - progress

    if total <= 10 or remaining <= 3:
        timeline, est_days, freq, ms_count = "short_term", max(7, remaining * 2), "daily", 2
    elif total <= 50 or remaining <= 20:
        timeline, est_days, freq, ms_count = "medium_term", max(30, remaining * 3), "3-4x/week", 3
    else:
        timeline, est_days, freq, ms_count = "long_term", max(90, remaining * 5), "2-3x/week", 5

    target = (datetime.now(timezone.utc) + timedelta(days=est_days)).strftime("%Y-%m-%d")
    return {
        "goalId": goal_id, "goalTitle": g["title"], "timeline": timeline,
        "estimatedDays": est_days, "targetCompletionDate": target,
        "recommendedTaskFrequency": freq, "recommendedMilestoneCount": ms_count,
    }


# ── Analysis ──────────────────────────────────────────────────────────────

@tool
def analyze_progress(user_id: str = FAKE_USER_ID) -> dict:
    """Deep analysis across all goals with risk assessment.

    Args:
        user_id: The authenticated user's ID.

    Returns:
        Detailed analysis with goal breakdowns and recommendations.
    """
    goals = _find("goals", user_id)
    tasks = _find("tasks", user_id)
    reminders = _find("reminders", user_id)
    active_goals = [g for g in goals if not g.get("completed")]
    completed_tasks = [t for t in tasks if t.get("completed")]
    pending_tasks = [t for t in tasks if not t.get("completed")]

    goal_analysis = []
    for g in active_goals:
        gid = g["id"]
        total = g.get("total", 100)
        progress = g.get("progress", 0)
        pct = round((progress / total) * 100) if total > 0 else 0
        linked = [t for t in tasks if t.get("goalId") == gid]
        linked_done = [t for t in linked if t.get("completed")]
        velocity = round((len(linked_done) / len(linked)) * 100) if linked else 0
        status = "on_track" if velocity >= 60 else ("at_risk" if pct < 25 else "needs_attention")
        goal_analysis.append({"id": gid, "title": g["title"], "percentComplete": pct, "status": status, "taskVelocity": velocity})

    return {
        "summary": {"totalGoals": len(goals), "activeGoals": len(active_goals),
                     "totalTasks": len(tasks), "completedTasks": len(completed_tasks), "pendingTasks": len(pending_tasks)},
        "goalAnalysis": goal_analysis,
        "recommendations": [],
    }


@tool
def get_daily_summary(user_id: str = FAKE_USER_ID) -> dict:
    """Comprehensive day overview.

    Args:
        user_id: The authenticated user's ID.

    Returns:
        Summary with goals, tasks, reminders.
    """
    goals = _find("goals", user_id)
    tasks = _find("tasks", user_id)
    reminders = _find("reminders", user_id)
    active_goals = [g for g in goals if not g.get("completed")]
    pending = [t for t in tasks if not t.get("completed")]
    completed = [t for t in tasks if t.get("completed")]

    return {
        "goals": {"active": [{"id": g["id"], "title": g["title"], "progress": g.get("progress", 0),
                               "total": g.get("total", 100)} for g in active_goals]},
        "tasks": {"completed": len(completed), "pending": len(pending),
                  "upcoming": [{"id": t["id"], "title": t["title"], "priority": t.get("priority", "medium")} for t in pending[:5]]},
        "reminders": {"active": [{"id": r["id"], "title": r["title"], "time": r.get("time", "")}
                                  for r in reminders if r.get("active")]},
    }


@tool
def smart_suggest(focus: str = "all", user_id: str = FAKE_USER_ID) -> dict:
    """Generate smart next-step suggestions.

    Args:
        focus: Focus area — goals, tasks, habits, or all.
        user_id: The authenticated user's ID.

    Returns:
        Prioritized suggestions.
    """
    goals = _find("goals", user_id)
    tasks = _find("tasks", user_id)
    suggestions = []
    for g in goals:
        if g.get("completed"):
            continue
        linked = [t for t in tasks if t.get("goalId") == g["id"]]
        if not linked:
            suggestions.append({"type": "missing_tasks", "suggestion": f'"{g["title"]}" has no tasks. Create a plan.', "priority": "high"})
    pending = [t for t in tasks if not t.get("completed")]
    if len(pending) > 10:
        suggestions.append({"type": "task_overload", "suggestion": f"{len(pending)} pending tasks. Focus on top 3.", "priority": "medium"})
    return {"suggestions": suggestions[:8], "focusArea": focus}


# ── Memory ────────────────────────────────────────────────────────────────

@tool
def search_memory(query: str, top_k: int = 5, user_id: str = FAKE_USER_ID) -> list[dict]:
    """Search long-term memory (simple keyword match for local dev).

    Args:
        query: Search query.
        top_k: Max results.
        user_id: The authenticated user's ID.

    Returns:
        Matching memories.
    """
    q = query.lower()
    results = [m for m in _find("memories", user_id) if q in m.get("content", "").lower()]
    return [{"content": m["content"], "category": m.get("category", ""), "createdAt": m.get("createdAt", "")}
            for m in results[:top_k]]


@tool
def remember_fact(
    content: str,
    category: str = "personal_info",
    importance: str = "medium",
    user_id: str = FAKE_USER_ID,
) -> dict:
    """Store an important fact about the user.

    Args:
        content: The fact to remember.
        category: preference, personal_info, goal_context, habit, etc.
        importance: critical, high, medium, low.
        user_id: The authenticated user's ID.

    Returns:
        Confirmation.
    """
    db["memories"].append({
        "id": _id(), "userId": user_id, "content": content,
        "category": category, "importance": importance, "createdAt": _now(),
    })
    return {"stored": True, "content": content, "category": category}


@tool
def recall_memories(query: str, limit: int = 5, user_id: str = FAKE_USER_ID) -> dict:
    """Recall facts from memory.

    Args:
        query: What to remember.
        limit: Max results.
        user_id: The authenticated user's ID.

    Returns:
        Found memories.
    """
    results = search_memory(query=query, top_k=limit, user_id=user_id)
    if not results:
        return {"found": False, "message": "No matching memories"}
    return {"found": True, "count": len(results), "memories": results}


# ── Web ───────────────────────────────────────────────────────────────────

@tool
def web_search(query: str, context: str = "") -> dict:
    """Search the internet via Gemini grounding.

    Args:
        query: Search query.
        context: Why you're searching.

    Returns:
        Answer and sources.
    """
    try:
        import httpx
        prompt = f"Search and answer: {query}"
        if context:
            prompt += f"\nContext: {context}"
        resp = httpx.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            params={"key": GEMINI_API_KEY},
            json={"contents": [{"parts": [{"text": prompt}]}],
                  "tools": [{"google_search": {}}],
                  "generationConfig": {"maxOutputTokens": 2048}},
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        text = ""
        if candidates:
            text = " ".join(p.get("text", "") for p in candidates[0].get("content", {}).get("parts", []))
        return {"answer": text or "No results.", "query": query}
    except Exception as e:
        return {"error": str(e), "query": query}


# ── Utility ───────────────────────────────────────────────────────────────

@tool
def query_user_data(data_type: str = "all", user_id: str = FAKE_USER_ID) -> dict:
    """Query stored data across entity types.

    Args:
        data_type: goals, tasks, reminders, or all.
        user_id: The authenticated user's ID.

    Returns:
        Requested data.
    """
    result = {}
    types = ["goals", "tasks", "reminders"] if data_type == "all" else [data_type]
    for t in types:
        result[t] = _find(t, user_id)
    return result


@tool
def search_data(query: str, user_id: str = FAKE_USER_ID) -> dict:
    """Keyword search across goals, tasks, reminders.

    Args:
        query: Search keyword.
        user_id: The authenticated user's ID.

    Returns:
        Matching items.
    """
    q = query.lower()
    return {
        "goals": [{"id": g["id"], "title": g["title"]} for g in _find("goals", user_id) if q in g.get("title", "").lower()],
        "tasks": [{"id": t["id"], "title": t["title"]} for t in _find("tasks", user_id) if q in t.get("title", "").lower()],
        "reminders": [{"id": r["id"], "title": r["title"]} for r in _find("reminders", user_id) if q in r.get("title", "").lower()],
    }


@tool
def get_current_datetime(timezone_str: str = "UTC") -> str:
    """Get current date and time.

    Args:
        timezone_str: Timezone name.

    Returns:
        Formatted datetime string.
    """
    return datetime.now(timezone.utc).strftime("%A, %B %d, %Y at %I:%M %p UTC")


# ═══════════════════════════════════════════════════════════════════════════
# ALL TOOLS LIST
# ═══════════════════════════════════════════════════════════════════════════

ALL_TOOLS = [
    get_goals, create_goal, update_goal, delete_goal,
    get_tasks, create_task, update_task, complete_task, delete_task,
    get_reminders, create_reminder, update_reminder, snooze_reminder, delete_reminder,
    decompose_goal_into_plan, adapt_plan, reschedule_failed_tasks,
    reschedule_plan, shift_plan, bulk_update_tasks, clear_and_replan,
    get_schedule, assign_task_to_date, analyze_goal_timeline,
    analyze_progress, get_daily_summary, smart_suggest,
    search_memory, remember_fact, recall_memories,
    web_search,
    query_user_data, search_data, get_current_datetime,
    cron_add, cron_list, cron_update, cron_remove, cron_run,
    connect_mcp_server, disconnect_mcp_server, list_mcp_servers,
]

# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════════════════════

def _build_system_prompt() -> str:
    now = datetime.now(timezone.utc)
    settings = _user_settings.get(FAKE_USER_ID, {})
    agent_name = settings.get("agentName", "Jumns")
    agent_behavior = settings.get(
        "agentBehavior",
        "Friendly, supportive, and proactive. You anticipate needs and "
        "take action without being asked. You celebrate wins and gently "
        "nudge when things fall behind.",
    )

    return f"""You are {agent_name}, a personal AI life assistant built into the Jumns app.

## Your Personality
{agent_behavior}

## AUTONOMOUS PLANNING PROTOCOL

You are NOT a passive assistant. You are an autonomous life coach that ACTS.

### When a user states a goal:
1. Call create_goal to create it
2. Call analyze_goal_timeline to classify short/medium/long-term
3. IMMEDIATELY call decompose_goal_into_plan with milestones, tasks, and reminders
4. Confirm naturally: "I've set up your goal with X milestones, Y tasks, and Z reminders."

### When a user reports progress:
1. Call complete_task or update_goal as appropriate
2. Call adapt_plan to check if adjustments are needed
3. Celebrate wins and address setbacks

### When a user asks "how am I doing?":
1. Call analyze_progress for deep analysis
2. Present findings with specific numbers

## RESCHEDULING PROTOCOL

When the user asks to reschedule, change timing, push back, or reorganize their plan:

### "Reschedule to next week" / "Do it in one week" / "Push everything back":
1. First call get_goals to find the relevant goal
2. Call reschedule_plan with the goal_id, start_date (next Monday or tomorrow), and spread_days
3. Confirm: "Done! I've spread your X tasks across [date range]."

### "Push everything back N days":
1. Call shift_plan with the goal_id and days=N
2. Confirm the shift

### "Start over" / "Redo my plan" / "Make a new schedule":
1. Call clear_and_replan to remove pending tasks/reminders
2. IMMEDIATELY call decompose_goal_into_plan with a fresh plan
3. Confirm the new plan

### "Change all tasks to high priority" / bulk changes:
1. Call get_tasks to get task IDs
2. Call bulk_update_tasks with the IDs and new values

### IMPORTANT: When the user says "reschedule" without specifying a goal:
- Call get_goals to list all active goals
- If there's only one active goal, use that
- If multiple, pick the most recently discussed one or ask which goal

## CRON JOBS / SCHEDULED AUTOMATION

You can create recurring automated jobs. Use these when the user says things like:
- "Remind me every morning at 8am to check my tasks"
- "Run a weekly progress check every Sunday"
- "Send me a daily briefing"
- "Check my goals every 30 minutes"

### Creating cron jobs:
- Use cron_add with schedule_type: "once", "daily", "weekly", "interval", or "cron"
- schedule_value format:
  - daily: "HH:MM" (e.g. "08:00")
  - weekly: "DayName HH:MM" (e.g. "Monday 09:00")
  - interval: minutes as string (e.g. "30")
  - once: ISO datetime (e.g. "2026-03-01T08:00:00Z")
  - cron: cron expression (e.g. "0 8 * * *")

### Managing cron jobs:
- cron_list: Show all scheduled jobs
- cron_update: Change schedule, message, or enable/disable
- cron_remove: Delete a job
- cron_run: Trigger a job immediately

## MCP SERVER MANAGEMENT

You can connect external MCP (Model Context Protocol) servers as skills.
When the user says "connect my calendar", "add an MCP server", "link Notion":
1. Call connect_mcp_server with the name, URL, and description
2. Confirm the connection
3. Use list_mcp_servers to show connected servers
4. Use disconnect_mcp_server to remove one

## Card Block Format
When showing structured data, use this format:

:::card{{type="<card_type>"}}
{{"title": "...", "items": [...]}}
:::

Supported card types: daily_briefing, goal_check_in, reminder, journal_prompt,
health_snapshot, plan_created, progress_report, suggestion, schedule_view,
schedule_changed, cron_status

Only use cards for structured data. For normal conversation, reply naturally.

## Important Rules
- Be conversational and warm, not robotic
- Don't ask too many clarifying questions — make reasonable assumptions and act
- Keep responses concise — this is a mobile chat app
- ALWAYS use tools when relevant. Never just describe what you could do — DO IT.
- After creating a goal, ALWAYS plan it immediately with decompose_goal_into_plan
- ALWAYS create reminders when creating plans
- When creating tasks in decompose_goal_into_plan, assign due_date to each task
- When the user says "reschedule", ALWAYS use reschedule_plan or shift_plan — NEVER just talk about it
- When the user asks about scheduling or automation, use cron_add to set it up immediately

## Current Context
- Date/Time: {now.strftime("%A, %B %d, %Y at %I:%M %p UTC")}
- Day of Week: {now.strftime("%A")}
- Tomorrow: {(now + timedelta(days=1)).strftime("%A, %B %d, %Y")}
- Next Monday: {(now + timedelta(days=(7 - now.weekday()) % 7 or 7)).strftime("%Y-%m-%d")}
"""


# ═══════════════════════════════════════════════════════════════════════════
# CARD BLOCK PARSER
# ═══════════════════════════════════════════════════════════════════════════

_CARD_RE = re.compile(r':::card\{type="([^"]+)"\}\s*(.*?)\s*:::', re.DOTALL)


def _parse_cards(text: str) -> tuple[str, str | None, dict | None]:
    """Extract :::card{type="X"} ... ::: from agent output."""
    m = _CARD_RE.search(text)
    if not m:
        return text, None, None
    card_type = m.group(1)
    body = m.group(2).strip()
    try:
        card_data = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        card_data = {"content": body}
    clean = text[:m.start()].strip()
    trail = text[m.end():].strip()
    if trail:
        clean = f"{clean}\n{trail}" if clean else trail
    return clean, card_type, card_data


def _sanitize(data: Any) -> Any:
    """Recursively sanitize card data for JSON serialization."""
    if isinstance(data, dict):
        return {str(k): _sanitize(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [_sanitize(v) for v in data]
    if isinstance(data, (str, int, float, bool)) or data is None:
        return data
    return str(data)


# ═══════════════════════════════════════════════════════════════════════════
# STRANDS AGENT INVOCATION
# ═══════════════════════════════════════════════════════════════════════════

# Conversation history for context
_conversation_history: list[dict] = []


def _invoke_agent(user_message: str, history: list[dict] | None = None) -> dict[str, Any]:
    """Create a Strands Agent and invoke it with the user's message + history."""
    from strands import Agent
    from strands.models.gemini import GeminiModel

    system_prompt = _build_system_prompt()

    model = GeminiModel(
        client_args={"api_key": GEMINI_API_KEY},
        model_id="gemini-2.5-flash",
    )

    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        tools=ALL_TOOLS,
    )

    # Build prompt with conversation context
    prompt_parts = []
    if history:
        # Include recent conversation for context
        prompt_parts.append("## Recent Conversation Context")
        for msg in history[-20:]:  # Cap at 20 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if content:
                label = "User" if role == "user" else "You (Jumns)"
                prompt_parts.append(f"{label}: {content}")
        prompt_parts.append("\n## Current Message")

    prompt_parts.append(user_message)
    full_prompt = "\n".join(prompt_parts)

    logger.info("🤖 Invoking Strands agent with: %s", user_message[:100])

    try:
        result = agent(full_prompt)
        response_text = str(result)
    except Exception as e:
        logger.exception("Agent invocation failed")
        response_text = f"I had trouble processing that. Error: {str(e)[:200]}"

    # Parse card blocks
    clean_text, card_type, card_data = _parse_cards(response_text)
    if card_data:
        card_data = _sanitize(card_data)

    logger.info("🤖 Agent response (card=%s): %s", card_type, (clean_text or response_text)[:200])

    return {
        "content": clean_text or response_text,
        "cardType": card_type,
        "cardData": card_data,
    }


# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI APP + REST ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(title="Jumns Local Dev Server (Strands Agent)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Fake auth middleware ──────────────────────────────────────────────────

@app.middleware("http")
async def fake_auth(request: Request, call_next):
    request.state.user_id = FAKE_USER_ID
    return await call_next(request)


# ── Health ────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "ok", "agent": "strands", "tools": len(ALL_TOOLS)}


@app.get("/api/health")
async def health():
    return {"status": "ok", "tools": len(ALL_TOOLS), "model": "gemini-2.5-flash"}


# ── Chat (Strands Agent) ─────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "").strip()
    history = body.get("history", [])
    uid = request.state.user_id
    if not message:
        return JSONResponse({"error": "Empty message"}, status_code=400)

    # Store user message
    user_msg = {
        "id": _id(), "userId": uid, "role": "user", "type": "text",
        "content": message, "timestamp": _now(), "createdAt": _now(),
    }
    db["messages"].append(user_msg)

    # Invoke Strands agent with conversation history
    try:
        result = _invoke_agent(message, history=history)
    except Exception as e:
        logger.exception("Chat endpoint error")
        result = {"content": f"Sorry, something went wrong: {str(e)[:200]}", "cardType": None, "cardData": None}

    # Store assistant message
    ai_msg = {
        "id": _id(), "userId": uid, "role": "assistant",
        "type": "card" if result.get("cardType") else "text",
        "content": result.get("content", ""),
        "cardType": result.get("cardType"),
        "cardData": result.get("cardData"),
        "timestamp": _now(), "createdAt": _now(),
    }
    db["messages"].append(ai_msg)

    return ai_msg


# ── Messages ──────────────────────────────────────────────────────────────

@app.get("/api/messages")
async def list_messages(request: Request):
    return _find("messages", request.state.user_id)


@app.delete("/api/messages")
async def clear_messages(request: Request):
    uid = request.state.user_id
    db["messages"] = [m for m in db["messages"] if m.get("userId") != uid]
    return JSONResponse(status_code=204, content=None)


# ── Goals ─────────────────────────────────────────────────────────────────

@app.get("/api/goals")
async def list_goals(request: Request):
    return _find("goals", request.state.user_id)


@app.get("/api/goals/{goal_id}")
async def get_goal(goal_id: str, request: Request):
    g = _find_one("goals", request.state.user_id, goal_id)
    if not g:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return g


@app.post("/api/goals")
async def create_goal_endpoint(request: Request):
    body = await request.json()
    uid = request.state.user_id
    goal = {
        "id": _id(), "userId": uid, "title": body.get("title", ""),
        "category": body.get("category", "Personal"), "progress": 0,
        "total": body.get("total", 100), "unit": body.get("unit", "%"),
        "insight": body.get("insight", ""), "completed": False,
        "activeAgent": "", "createdAt": _now(),
    }
    db["goals"].append(goal)
    return goal


@app.patch("/api/goals/{goal_id}")
async def update_goal_endpoint(goal_id: str, request: Request):
    g = _find_one("goals", request.state.user_id, goal_id)
    if not g:
        return JSONResponse({"error": "Not found"}, status_code=404)
    body = await request.json()
    for k, v in body.items():
        if k != "id" and k != "userId":
            g[k] = v
    return g


@app.delete("/api/goals/{goal_id}")
async def delete_goal_endpoint(goal_id: str, request: Request):
    _delete_one("goals", request.state.user_id, goal_id)
    return JSONResponse(status_code=204, content=None)


# ── Tasks ─────────────────────────────────────────────────────────────────

@app.get("/api/tasks")
async def list_tasks(request: Request, goalId: str | None = None):
    tasks = _find("tasks", request.state.user_id)
    if goalId:
        tasks = [t for t in tasks if t.get("goalId") == goalId]
    return tasks


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str, request: Request):
    t = _find_one("tasks", request.state.user_id, task_id)
    if not t:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return t


@app.post("/api/tasks")
async def create_task_endpoint(request: Request):
    body = await request.json()
    uid = request.state.user_id
    task = {
        "id": _id(), "userId": uid, "title": body.get("title", ""),
        "time": body.get("time", ""), "detail": body.get("detail", ""),
        "type": body.get("type", "task"), "completed": False, "active": False,
        "goalId": body.get("goalId"), "priority": body.get("priority", "medium"),
        "dueDate": body.get("dueDate", ""), "requiresProof": body.get("requiresProof", False),
        "proofStatus": "pending", "createdAt": _now(),
    }
    db["tasks"].append(task)
    return task


@app.patch("/api/tasks/{task_id}")
async def update_task_endpoint(task_id: str, request: Request):
    t = _find_one("tasks", request.state.user_id, task_id)
    if not t:
        return JSONResponse({"error": "Not found"}, status_code=404)
    body = await request.json()
    for k, v in body.items():
        if k not in ("id", "userId"):
            t[k] = v
    return t


@app.post("/api/tasks/{task_id}/complete")
async def complete_task_endpoint(task_id: str, request: Request):
    t = _find_one("tasks", request.state.user_id, task_id)
    if not t:
        return JSONResponse({"error": "Not found"}, status_code=404)
    t["completed"] = True
    body = await request.json()
    if body.get("proofUrl"):
        t["proofUrl"] = body["proofUrl"]
        t["proofType"] = body.get("proofType", "image")
        t["proofStatus"] = "submitted"
    return t


@app.delete("/api/tasks/{task_id}")
async def delete_task_endpoint(task_id: str, request: Request):
    _delete_one("tasks", request.state.user_id, task_id)
    return JSONResponse(status_code=204, content=None)


# ── Reminders ─────────────────────────────────────────────────────────────

@app.get("/api/reminders")
async def list_reminders(request: Request):
    return _find("reminders", request.state.user_id)


@app.post("/api/reminders")
async def create_reminder_endpoint(request: Request):
    body = await request.json()
    uid = request.state.user_id
    rem = {
        "id": _id(), "userId": uid, "title": body.get("title", ""),
        "time": body.get("time", ""), "active": True,
        "goalId": body.get("goalId"), "snoozeCount": 0,
        "snoozedUntil": None, "originalTime": body.get("time", ""),
        "createdAt": _now(),
    }
    db["reminders"].append(rem)
    return rem


@app.patch("/api/reminders/{reminder_id}")
async def update_reminder_endpoint(reminder_id: str, request: Request):
    r = _find_one("reminders", request.state.user_id, reminder_id)
    if not r:
        return JSONResponse({"error": "Not found"}, status_code=404)
    body = await request.json()
    for k, v in body.items():
        if k not in ("id", "userId"):
            r[k] = v
    return r


@app.post("/api/reminders/{reminder_id}/snooze")
async def snooze_reminder_endpoint(reminder_id: str, request: Request):
    r = _find_one("reminders", request.state.user_id, reminder_id)
    if not r:
        return JSONResponse({"error": "Not found"}, status_code=404)
    body = await request.json()
    minutes = body.get("minutes", 30)
    r["snoozeCount"] = r.get("snoozeCount", 0) + 1
    r["snoozedUntil"] = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
    return r


@app.delete("/api/reminders/{reminder_id}")
async def delete_reminder_endpoint(reminder_id: str, request: Request):
    _delete_one("reminders", request.state.user_id, reminder_id)
    return JSONResponse(status_code=204, content=None)


# ── Settings ──────────────────────────────────────────────────────────────

@app.get("/api/settings")
async def get_settings(request: Request):
    uid = request.state.user_id
    defaults = {
        "agentName": "Jumns",
        "agentBehavior": "Friendly, supportive, and proactive.",
        "personality": "supportive",
        "timezone": "UTC",
        "theme": "light",
        "notificationsEnabled": True,
    }
    return {**defaults, **_user_settings.get(uid, {})}


@app.patch("/api/settings")
async def update_settings(request: Request):
    uid = request.state.user_id
    body = await request.json()
    if uid not in _user_settings:
        _user_settings[uid] = {}
    _user_settings[uid].update(body)
    return await get_settings(request)


# ── User Settings (alias — Flutter calls /api/user-settings) ─────────────

@app.get("/api/user-settings")
async def get_user_settings(request: Request):
    """Alias for /api/settings — Flutter frontend uses this path."""
    return await get_settings(request)


@app.post("/api/user-settings")
async def post_user_settings(request: Request):
    """Alias for PATCH /api/settings — Flutter POSTs to this path."""
    uid = request.state.user_id
    body = await request.json()
    if uid not in _user_settings:
        _user_settings[uid] = {}
    _user_settings[uid].update(body)
    return await get_settings(request)


# ── Subscription (stub for RevenueCat) ────────────────────────────────────

@app.get("/api/subscription/status")
async def subscription_status():
    return {
        "plan": "free", "status": "active",
        "features": {"chat": True, "goals": True, "tasks": True, "reminders": True,
                      "insights": True, "memory": True, "voice": False, "proofVerification": False},
    }


# ── Insights ──────────────────────────────────────────────────────────────

@app.get("/api/insights")
async def list_insights(request: Request):
    return _find("insights", request.state.user_id)


@app.get("/api/insights/unread")
async def unread_insights(request: Request):
    all_insights = _find("insights", request.state.user_id)
    count = sum(1 for i in all_insights if not i.get("read") and not i.get("dismissed"))
    return {"count": count}


@app.post("/api/insights/{insight_id}/read")
async def mark_insight_read(insight_id: str, request: Request):
    item = _find_one("insights", request.state.user_id, insight_id)
    if not item:
        return JSONResponse({"error": "not found"}, 404)
    item["read"] = True
    return item


@app.post("/api/insights/{insight_id}/dismiss")
async def dismiss_insight(insight_id: str, request: Request):
    item = _find_one("insights", request.state.user_id, insight_id)
    if not item:
        return JSONResponse({"error": "not found"}, 404)
    item["dismissed"] = True
    return item


@app.post("/api/insights/run")
async def run_insights_engine(request: Request):
    """Trigger a manual proactive insights generation run."""
    uid = request.state.user_id
    goals = _find("goals", uid)
    tasks = _find("tasks", uid)
    new_insights = []

    # Simple pattern detection — generate insights based on current state
    pending_tasks = [t for t in tasks if not t.get("completed")]
    completed_tasks = [t for t in tasks if t.get("completed")]

    if len(pending_tasks) > 10:
        new_insights.append({
            "id": _id(), "userId": uid, "type": "task_overload",
            "title": "Task Overload Detected",
            "content": f"You have {len(pending_tasks)} pending tasks. Consider prioritizing the top 3.",
            "priority": "high", "read": False, "dismissed": False,
            "relatedGoalId": None, "createdAt": _now(),
        })

    for g in goals:
        if g.get("completed"):
            continue
        linked = [t for t in tasks if t.get("goalId") == g["id"]]
        if not linked:
            new_insights.append({
                "id": _id(), "userId": uid, "type": "missing_plan",
                "title": f'No plan for "{g["title"]}"',
                "content": f'Your goal "{g["title"]}" has no tasks yet. Ask me to create a plan!',
                "priority": "medium", "read": False, "dismissed": False,
                "relatedGoalId": g["id"], "createdAt": _now(),
            })

    if completed_tasks:
        new_insights.append({
            "id": _id(), "userId": uid, "type": "progress_update",
            "title": "Keep it up!",
            "content": f"You've completed {len(completed_tasks)} tasks so far. Great momentum!",
            "priority": "low", "read": False, "dismissed": False,
            "relatedGoalId": None, "createdAt": _now(),
        })

    db["insights"].extend(new_insights)
    return {"generated": len(new_insights), "total": len(_find("insights", uid))}


# ── Skills ────────────────────────────────────────────────────────────────

@app.get("/api/skills")
async def list_skills(request: Request):
    return _find("skills", request.state.user_id)


@app.post("/api/skills")
async def create_skill(request: Request):
    body = await request.json()
    uid = request.state.user_id
    skill = {
        "id": _id(), "userId": uid,
        "name": body.get("name", ""),
        "type": body.get("type", "mcp"),
        "description": body.get("description", ""),
        "category": body.get("category", "mcp"),
        "enabled": True,
        "createdAt": _now(),
    }
    db["skills"].append(skill)
    return skill


@app.patch("/api/skills/{skill_id}")
async def update_skill(skill_id: str, request: Request):
    s = _find_one("skills", request.state.user_id, skill_id)
    if not s:
        return JSONResponse({"error": "Not found"}, status_code=404)
    body = await request.json()
    for k, v in body.items():
        if k not in ("id", "userId"):
            s[k] = v
    return s


@app.delete("/api/skills/{skill_id}")
async def delete_skill(skill_id: str, request: Request):
    _delete_one("skills", request.state.user_id, skill_id)
    return JSONResponse(status_code=204, content=None)


# ── Cron Jobs REST API ────────────────────────────────────────────────────

@app.get("/api/cron")
async def list_cron_jobs(request: Request, includeDisabled: bool = False):
    uid = request.state.user_id
    jobs = [j for j in _cron_jobs if j.get("userId") == uid]
    if not includeDisabled:
        jobs = [j for j in jobs if j.get("enabled", True)]
    return jobs


@app.post("/api/cron")
async def create_cron_job(request: Request):
    body = await request.json()
    uid = request.state.user_id
    job = {
        "id": _id(), "userId": uid,
        "name": body.get("name", "Untitled Job"),
        "description": body.get("description", ""),
        "enabled": body.get("enabled", True),
        "scheduleType": body.get("scheduleType", "daily"),
        "scheduleValue": body.get("scheduleValue", "08:00"),
        "actionMessage": body.get("actionMessage", ""),
        "createdAt": _now(), "updatedAt": _now(),
        "lastRunAt": None, "nextRunAt": None,
        "runCount": 0, "lastStatus": None,
    }
    job["nextRunAt"] = _compute_next_run(job["scheduleType"], job["scheduleValue"])
    _cron_jobs.append(job)
    return job


@app.patch("/api/cron/{job_id}")
async def update_cron_job(job_id: str, request: Request):
    uid = request.state.user_id
    job = next((j for j in _cron_jobs if j["id"] == job_id and j.get("userId") == uid), None)
    if not job:
        return JSONResponse({"error": "Not found"}, status_code=404)
    body = await request.json()
    for k, v in body.items():
        if k not in ("id", "userId"):
            job[k] = v
    job["updatedAt"] = _now()
    job["nextRunAt"] = _compute_next_run(job["scheduleType"], job["scheduleValue"])
    return job


@app.delete("/api/cron/{job_id}")
async def delete_cron_job(job_id: str, request: Request):
    global _cron_jobs
    uid = request.state.user_id
    _cron_jobs = [j for j in _cron_jobs if not (j["id"] == job_id and j.get("userId") == uid)]
    return JSONResponse(status_code=204, content=None)


@app.post("/api/cron/{job_id}/run")
async def run_cron_job(job_id: str, request: Request):
    uid = request.state.user_id
    job = next((j for j in _cron_jobs if j["id"] == job_id and j.get("userId") == uid), None)
    if not job:
        return JSONResponse({"error": "Not found"}, status_code=404)
    job["lastRunAt"] = _now()
    job["runCount"] = job.get("runCount", 0) + 1
    job["lastStatus"] = "ok"
    job["nextRunAt"] = _compute_next_run(job["scheduleType"], job["scheduleValue"])
    return {"ran": True, "job": job}


# ── Weekly Progress ───────────────────────────────────────────────────────

@app.get("/api/goals/weekly-progress")
async def weekly_progress(request: Request):
    """Return task completion counts per day of the current week (Mon-Sun)."""
    uid = request.state.user_id
    tasks = _find("tasks", uid)
    now = datetime.now(timezone.utc)
    # Monday of this week
    monday = now - timedelta(days=now.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)

    counts = [0] * 7  # Mon=0 .. Sun=6
    for t in tasks:
        if not t.get("completed"):
            continue
        # Check createdAt or dueDate to determine which day
        date_str = t.get("dueDate") or t.get("createdAt", "")
        if not date_str:
            continue
        try:
            if "T" in date_str:
                d = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
        if monday <= d < monday + timedelta(days=7):
            counts[d.weekday()] += 1

    total = sum(counts)
    best_day = counts.index(max(counts)) if total > 0 else -1
    return {
        "counts": counts,
        "total": total,
        "bestDay": best_day,
        "weekStart": monday.strftime("%Y-%m-%d"),
    }


# ── Seed (no-op for local) ───────────────────────────────────────────────

@app.post("/api/seed")
async def seed():
    return {"seeded": True}


# ── File Upload ───────────────────────────────────────────────────────────

import base64
from fastapi import UploadFile, File as FastAPIFile, Form

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    message: str = Form(""),
    request: Request = None,
):
    """Accept a file upload, store metadata, and optionally send to chat agent."""
    uid = getattr(request.state, "user_id", FAKE_USER_ID) if request else FAKE_USER_ID
    contents = await file.read()
    file_id = _id()
    file_record = {
        "id": file_id,
        "userId": uid,
        "filename": file.filename or "upload",
        "contentType": file.content_type or "application/octet-stream",
        "size": len(contents),
        "createdAt": _now(),
    }
    # Store in memory (in production, upload to S3/GCS)
    db.setdefault("files", []).append({**file_record, "_data": contents})

    result = {"file": file_record}

    # If a message was included, send it to the agent with file context
    if message.strip():
        file_context = f"[User attached file: {file.filename} ({file.content_type}, {len(contents)} bytes)]"
        full_message = f"{file_context}\n{message}"
        agent_result = _invoke_agent(full_message)
        ai_msg = {
            "id": _id(), "userId": uid, "role": "assistant",
            "type": "card" if agent_result.get("cardType") else "text",
            "content": agent_result.get("content", ""),
            "cardType": agent_result.get("cardType"),
            "cardData": agent_result.get("cardData"),
            "timestamp": _now(), "createdAt": _now(),
        }
        db["messages"].append(ai_msg)
        result["response"] = ai_msg

    return result


# ── User profile (stub) ──────────────────────────────────────────────────

@app.get("/api/user/profile")
async def user_profile():
    return {
        "id": FAKE_USER_ID, "name": "Local Dev User",
        "email": "dev@jumns.local", "plan": "free",
    }


# ── Access Code (stub) ───────────────────────────────────────────────────

@app.get("/api/access-code/status")
async def access_code_status():
    """Stub — returns not activated. For production, check against a real code store."""
    return {"activated": False}


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Jumns Local Dev Server (Strands Agent)")
    logger.info("   %d tools registered", len(ALL_TOOLS))
    logger.info("   Model: gemini-2.5-flash")
    logger.info("   Port: %d", PORT)
    logger.info("   Flutter: http://10.0.2.2:%d", PORT)
    logger.info("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
