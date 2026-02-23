"""Agent tools — callable by the Strands Agent during conversation.

Organized by domain, mirroring OpenClaw's skill-based tool registry.
Each tool is a @tool-decorated function that receives user_id from
the agent context and interacts with the appropriate repository.

Tool categories (borrowed from OpenClaw's tool policy system):
  - goal_tools: CRUD + planning decomposition
  - task_tools: CRUD + completion + rescheduling
  - reminder_tools: CRUD + pause/resume
  - planning_tools: autonomous goal decomposition, adaptation, rescheduling
  - analysis_tools: progress analysis, smart suggestions, daily summary
  - memory_tools: vector search, fact storage, recall
  - web_tools: internet search via Google grounding
  - utility_tools: data queries, datetime, search across entities
"""

from app.agent.tools.goal_tools import (
    create_goal,
    delete_goal,
    get_goals,
    update_goal,
)
from app.agent.tools.task_tools import (
    complete_task,
    create_task,
    delete_task,
    get_tasks,
    update_task,
)
from app.agent.tools.reminder_tools import (
    create_reminder,
    delete_reminder,
    get_reminders,
    snooze_reminder,
    update_reminder,
)
from app.agent.tools.planning_tools import (
    decompose_goal_into_plan,
    adapt_plan,
    reschedule_failed_tasks,
)
from app.agent.tools.calendar_tools import (
    analyze_goal_timeline,
    assign_task_to_date,
    get_schedule,
)
from app.agent.tools.analysis_tools import (
    analyze_progress,
    get_daily_summary,
    smart_suggest,
)
from app.agent.tools.memory_tools import (
    recall_memories,
    remember_fact,
    search_memory,
)
from app.agent.tools.web_tools import web_search
from app.agent.tools.utility_tools import (
    get_current_datetime,
    query_user_data,
    search_data,
)

ALL_TOOLS = [
    # Goals
    get_goals,
    create_goal,
    update_goal,
    delete_goal,
    # Tasks
    get_tasks,
    create_task,
    update_task,
    complete_task,
    delete_task,
    # Reminders
    get_reminders,
    create_reminder,
    update_reminder,
    snooze_reminder,
    delete_reminder,
    # Planning (autonomous)
    decompose_goal_into_plan,
    adapt_plan,
    reschedule_failed_tasks,
    # Calendar & Scheduling
    get_schedule,
    assign_task_to_date,
    analyze_goal_timeline,
    # Analysis
    analyze_progress,
    get_daily_summary,
    smart_suggest,
    # Memory
    search_memory,
    remember_fact,
    recall_memories,
    # Web
    web_search,
    # Utility
    query_user_data,
    search_data,
    get_current_datetime,
]
