import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.tasks import TaskRead


class Greeting(BaseModel):
    period: Literal["morning", "afternoon", "evening"]
    text: str


class PriorityGroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[TaskRead]
    total: int


class TasksByPriority(BaseModel):
    critical: PriorityGroupRead
    high: PriorityGroupRead
    normal: PriorityGroupRead
    low: PriorityGroupRead


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor: str
    action: str
    entity_type: str | None
    entity_id: uuid.UUID | None
    details: dict[str, Any]
    created_at: datetime


class DashboardRead(BaseModel):
    greeting: Greeting
    tasks_by_priority: TasksByPriority
    activity: list[ActivityRead]
