import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time import utc_now
from app.db.base import Base, TimestampMixin, UserOwnedMixin, UUIDPrimaryKeyMixin


class TaskPriority(StrEnum):
    # Declaration order is the sort order: critical first.
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class TaskStatus(StrEnum):
    TODO = "todo"
    DONE = "done"
    ARCHIVED = "archived"


class TaskSource(StrEnum):
    MANUAL = "manual"
    EMAIL = "email"
    AI_SUGGESTION = "ai_suggestion"


def _enum_values(enum_class: type[StrEnum]) -> list[str]:
    return [member.value for member in enum_class]


class Task(UUIDPrimaryKeyMixin, TimestampMixin, UserOwnedMixin, Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_user_status_priority_due", "user_id", "status", "priority", "due_at"),
    )

    title: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, name="task_priority", values_callable=_enum_values),
        server_default=TaskPriority.NORMAL.value,
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status", values_callable=_enum_values),
        server_default=TaskStatus.TODO.value,
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[TaskSource] = mapped_column(
        Enum(TaskSource, name="task_source", values_callable=_enum_values),
        server_default=TaskSource.MANUAL.value,
    )
    source_ref: Mapped[uuid.UUID | None] = mapped_column(Uuid)

    @property
    def is_overdue(self) -> bool:
        """Still to do and past its due time (FR-TASK-4)."""
        return (
            self.status == TaskStatus.TODO and self.due_at is not None and self.due_at < utc_now()
        )
