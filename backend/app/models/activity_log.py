import uuid
from typing import Any

from sqlalchemy import Index, Text, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UserOwnedMixin, UUIDPrimaryKeyMixin


class ActivityLog(UUIDPrimaryKeyMixin, TimestampMixin, UserOwnedMixin, Base):
    """Append-only: rows are inserted by activity_service and never updated or deleted."""

    __tablename__ = "activity_logs"

    actor: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    entity_type: Mapped[str | None] = mapped_column(Text)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default=text("'{}'"))


Index(
    "ix_activity_logs_user_id_created_at",
    ActivityLog.user_id,
    ActivityLog.created_at.desc(),
)
