import uuid
from datetime import datetime
from typing import Annotated, Self

from pydantic import AwareDatetime, BaseModel, ConfigDict, StringConstraints, model_validator

from app.models.task import TaskPriority, TaskSource, TaskStatus

TaskTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
TaskNotes = Annotated[str, StringConstraints(max_length=5000)]


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: TaskTitle
    notes: TaskNotes | None = None
    priority: TaskPriority = TaskPriority.NORMAL
    due_at: AwareDatetime | None = None


class TaskUpdate(BaseModel):
    """Only the fields present in the request are changed. `notes` and `due_at` may be
    set to null to clear them; the other fields may be omitted but not null."""

    model_config = ConfigDict(extra="forbid")

    title: TaskTitle | None = None
    notes: TaskNotes | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    due_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def reject_null_for_required_fields(self) -> Self:
        for field_name in ("title", "priority", "status"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    notes: str | None
    priority: TaskPriority
    status: TaskStatus
    due_at: datetime | None
    completed_at: datetime | None
    source: TaskSource
    source_ref: uuid.UUID | None
    is_overdue: bool
    created_at: datetime
    updated_at: datetime


class TaskList(BaseModel):
    items: list[TaskRead]
    next_cursor: str | None
