import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog

ACTOR_USER = "user"
ACTOR_SYSTEM = "system"


def record(
    db: Session,
    *,
    user_id: uuid.UUID,
    actor: str,
    action: str,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    details: dict[str, Any] | None = None,
) -> ActivityLog:
    """Append one entry. `details` must never hold secrets or email content (FR-ACT-1)."""
    entry = ActivityLog(
        user_id=user_id,
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
    )
    db.add(entry)
    db.flush()
    return entry


def list_latest(db: Session, *, user_id: uuid.UUID, limit: int) -> list[ActivityLog]:
    statement = (
        select(ActivityLog)
        .where(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
        .limit(limit)
    )
    return list(db.scalars(statement))
