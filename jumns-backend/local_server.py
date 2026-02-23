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
    get_schedule, assign_task_to_date, analyze_goal_timeline,
    analyze_progress, get_daily_summary, smart_suggest,
    search_memory, remember_fact, recall_memories,
    web_search,
    query_user_data, search_data, get_current_datetime,
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

### Card Block Format
When showing structured data, use this format:

:::card{{type="<card_type>"}}
{{"title": "...", "items": [...]}}
:::

Supported card types: daily_briefing, goal_check_in, reminder, journal_prompt,
health_snapshot, plan_created, progress_report, suggestion, schedule_view

Only use cards for structured data. For normal conversation, reply naturally.

## Important Rules
- Be conversational and warm, not robotic
- Don't ask too many clarifying questions — make reasonable assumptions and act
- Keep responses concise — this is a mobile chat app
- ALWAYS use tools when relevant. Never just describe what you could do — DO IT.
- After creating a goal, ALWAYS plan it immediately with decompose_goal_into_plan
- ALWAYS create reminders when creating plans
- When creating tasks in decompose_goal_into_plan, assign due_date to each task

## Current Context
- Date/Time: {now.strftime("%A, %B %d, %Y at %I:%M %p UTC")}
- Day of Week: {now.strftime("%A")}
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


def _invoke_agent(user_message: str) -> dict[str, Any]:
    """Create a Strands Agent and invoke it with the user's message."""
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

    logger.info("🤖 Invoking Strands agent with: %s", user_message[:100])

    try:
        result = agent(user_message)
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
    uid = request.state.user_id
    if not message:
        return JSONResponse({"error": "Empty message"}, status_code=400)

    # Store user message
    user_msg = {
        "id": _id(), "userId": uid, "role": "user", "type": "text",
        "content": message, "timestamp": _now(), "createdAt": _now(),
    }
    db["messages"].append(user_msg)

    # Invoke Strands agent
    try:
        result = _invoke_agent(message)
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


# ── Skills ────────────────────────────────────────────────────────────────

@app.get("/api/skills")
async def list_skills(request: Request):
    return _find("skills", request.state.user_id)


# ── Seed (no-op for local) ───────────────────────────────────────────────

@app.post("/api/seed")
async def seed():
    return {"seeded": True}


# ── User profile (stub) ──────────────────────────────────────────────────

@app.get("/api/user/profile")
async def user_profile():
    return {
        "id": FAKE_USER_ID, "name": "Local Dev User",
        "email": "dev@jumns.local", "plan": "free",
    }


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
