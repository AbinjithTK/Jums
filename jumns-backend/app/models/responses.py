"""Pydantic response models — camelCase JSON for Flutter."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )


class MessageResponse(CamelModel):
    id: str
    user_id: str
    role: str
    type: str
    content: str | None = None
    card_type: str | None = None
    card_data: dict | None = None
    timestamp: str
    created_at: str | None = None


class GoalResponse(CamelModel):
    id: str
    user_id: str
    title: str
    category: str
    progress: int = 0
    total: int = 100
    unit: str = ""
    insight: str = ""
    active_agent: str = ""
    completed: bool = False
    created_at: str | None = None


class TaskResponse(CamelModel):
    id: str
    user_id: str
    title: str
    time: str = ""
    detail: str = ""
    type: str = "task"
    completed: bool = False
    active: bool = False
    goal_id: str | None = None
    priority: str = "medium"
    requires_proof: bool = False
    due_date: str | None = None
    proof_url: str | None = None
    proof_type: str | None = None
    proof_status: str = "pending"
    completed_at: str | None = None
    created_at: str | None = None


class ReminderResponse(CamelModel):
    id: str
    user_id: str
    title: str
    time: str = ""
    active: bool = True
    goal_id: str | None = None
    snooze_count: int = 0
    snoozed_until: str | None = None
    original_time: str | None = None
    created_at: str | None = None


class SkillResponse(CamelModel):
    id: str
    user_id: str
    name: str
    type: str = "mcp"
    description: str = ""
    status: str = "inactive"
    category: str = "mcp"
    created_at: str | None = None


class UserSettingsResponse(CamelModel):
    agent_name: str = "Jumns"
    agent_behavior: str = "Friendly & Supportive"
    onboarding_completed: bool = False
    timezone: str = "UTC"
    morning_time: str = "07:00"
    evening_time: str = "21:00"


class SubscriptionStatusResponse(CamelModel):
    plan: str = "free"
    is_pro: bool = False
    expires_at: str | None = None


class AccessCodeStatusResponse(CamelModel):
    activated: bool = False


class InsightResponse(CamelModel):
    id: str
    user_id: str
    type: str
    title: str
    content: str
    related_goal_id: str | None = None
    created_at: str | None = None


class MemoryResponse(CamelModel):
    id: str
    user_id: str
    content: str
    metadata: dict | None = None
    created_at: str | None = None


class ErrorResponse(BaseModel):
    error: str
