"""DynamoDB table names and key schemas — read from environment variables."""

import os

# Table names (set by CDK via Lambda env vars, defaults for local dev)
USERS_TABLE = os.getenv("USERS_TABLE", "jumns-users")
MESSAGES_TABLE = os.getenv("MESSAGES_TABLE", "jumns-messages")
GOALS_TABLE = os.getenv("GOALS_TABLE", "jumns-goals")
TASKS_TABLE = os.getenv("TASKS_TABLE", "jumns-tasks")
REMINDERS_TABLE = os.getenv("REMINDERS_TABLE", "jumns-reminders")
SKILLS_TABLE = os.getenv("SKILLS_TABLE", "jumns-skills")
INSIGHTS_TABLE = os.getenv("INSIGHTS_TABLE", "jumns-insights")
ACCESS_CODES_TABLE = os.getenv("ACCESS_CODES_TABLE", "jumns-access-codes")

# GSI names
TASKS_BY_GOAL_GSI = "TasksByGoal"
ACTIVE_REMINDERS_GSI = "ActiveReminders"
MESSAGES_BY_TYPE_GSI = "MessagesByType"
