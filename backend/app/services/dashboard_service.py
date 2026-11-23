from datetime import datetime

from sqlalchemy.orm import Session

from app.core.time import greeting_period, to_user_local
from app.models.task import TaskPriority
from app.models.user import User
from app.schemas.dashboard import (
    ActivityRead,
    DashboardRead,
    Greeting,
    PriorityGroupRead,
    TasksByPriority,
)
from app.services import activity_service, task_service

DASHBOARD_ACTIVITY_LIMIT = 10


def build_greeting(user: User, *, now: datetime) -> Greeting:
    period = greeting_period(to_user_local(now, user.timezone).time())
    name_suffix = f", {user.display_name}" if user.display_name else ""
    return Greeting(period=period, text=f"Good {period}{name_suffix}.")


def get_dashboard(db: Session, *, user: User, now: datetime) -> DashboardRead:
    """Everything the home page needs in one call (FR-DASH-1).

    Briefing, decisions, food totals and AI spend are added in the phases that build them.
    """
    groups = task_service.group_open_tasks_by_priority(db, user_id=user.id)
    activity = activity_service.list_latest(db, user_id=user.id, limit=DASHBOARD_ACTIVITY_LIMIT)
    return DashboardRead(
        greeting=build_greeting(user, now=now),
        tasks_by_priority=TasksByPriority(
            critical=PriorityGroupRead.model_validate(groups[TaskPriority.CRITICAL]),
            high=PriorityGroupRead.model_validate(groups[TaskPriority.HIGH]),
            normal=PriorityGroupRead.model_validate(groups[TaskPriority.NORMAL]),
            low=PriorityGroupRead.model_validate(groups[TaskPriority.LOW]),
        ),
        activity=[ActivityRead.model_validate(entry) for entry in activity],
    )
