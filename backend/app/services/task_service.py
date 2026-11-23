import base64
import binascii
import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import AppError, ErrorCode
from app.core.time import utc_now
from app.models.task import Task, TaskPriority, TaskSource, TaskStatus
from app.schemas.tasks import TaskCreate, TaskUpdate
from app.services import activity_service

ENTITY_TYPE = "task"
DASHBOARD_TASKS_PER_PRIORITY = 5

# Priority (critical first), then due date (soonest first, no date last), then age.
# The id makes the order total, so pages never overlap (FR-TASK-3).
DEFAULT_ORDER: tuple[ColumnElement[Any], ...] = (
    Task.priority.asc(),
    Task.due_at.asc().nulls_last(),
    Task.created_at.asc(),
    Task.id.asc(),
)


@dataclass(frozen=True)
class TaskPage:
    items: list[Task]
    next_cursor: str | None


@dataclass(frozen=True)
class PriorityGroup:
    items: list[Task]
    total: int


def encode_cursor(offset: int) -> str:
    return base64.urlsafe_b64encode(json.dumps({"offset": offset}).encode()).decode()


def decode_cursor(cursor: str | None) -> int:
    if cursor is None:
        return 0
    try:
        offset = json.loads(base64.urlsafe_b64decode(cursor.encode()))["offset"]
    except (binascii.Error, ValueError, KeyError, TypeError) as exc:
        raise AppError(ErrorCode.VALIDATION_ERROR, "Invalid cursor") from exc
    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise AppError(ErrorCode.VALIDATION_ERROR, "Invalid cursor")
    return offset


def create_task(
    db: Session,
    *,
    user_id: uuid.UUID,
    data: TaskCreate,
    actor: str = activity_service.ACTOR_USER,
) -> Task:
    task = Task(
        user_id=user_id,
        title=data.title,
        notes=data.notes,
        priority=data.priority,
        status=TaskStatus.TODO,
        due_at=data.due_at,
        source=TaskSource.MANUAL,
    )
    db.add(task)
    db.flush()
    activity_service.record(
        db,
        user_id=user_id,
        actor=actor,
        action="task.created",
        entity_type=ENTITY_TYPE,
        entity_id=task.id,
        details={"title": task.title, "priority": task.priority.value},
    )
    return task


def get_task(db: Session, *, user_id: uuid.UUID, task_id: uuid.UUID) -> Task:
    """Another user's task is reported as not found, never as forbidden."""
    task = db.scalars(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if task is None:
        raise AppError("TASK_NOT_FOUND", "Task not found", status_code=404)
    return task


def list_tasks(
    db: Session,
    *,
    user_id: uuid.UUID,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    due_before: datetime | None = None,
    query: str | None = None,
    limit: int = 20,
    cursor: str | None = None,
) -> TaskPage:
    offset = decode_cursor(cursor)
    statement = select(Task).where(Task.user_id == user_id)
    if status is not None:
        statement = statement.where(Task.status == status)
    if priority is not None:
        statement = statement.where(Task.priority == priority)
    if due_before is not None:
        statement = statement.where(Task.due_at < due_before)
    if query:
        statement = statement.where(
            or_(
                Task.title.icontains(query, autoescape=True),
                Task.notes.icontains(query, autoescape=True),
            )
        )
    # One extra row tells us whether another page exists.
    rows = list(db.scalars(statement.order_by(*DEFAULT_ORDER).offset(offset).limit(limit + 1)))
    has_more = len(rows) > limit
    return TaskPage(
        items=rows[:limit],
        next_cursor=encode_cursor(offset + limit) if has_more else None,
    )


def update_task(
    db: Session,
    *,
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskUpdate,
    actor: str = activity_service.ACTOR_USER,
) -> Task:
    task = get_task(db, user_id=user_id, task_id=task_id)
    changes = data.model_dump(exclude_unset=True)
    previous_status = task.status

    for field_name in ("title", "notes", "priority", "due_at"):
        if field_name in changes:
            setattr(task, field_name, changes[field_name])

    new_status: TaskStatus = changes.get("status", previous_status)
    if new_status != previous_status:
        task.status = new_status
        action: str | None = None
        if new_status == TaskStatus.DONE:
            task.completed_at = utc_now()
            action = "task.completed"
        elif previous_status == TaskStatus.DONE:
            # Leaving "done" for any other status clears the completion time (FR-TASK-2).
            task.completed_at = None
            if new_status == TaskStatus.TODO:
                action = "task.reopened"
        if action is not None:
            activity_service.record(
                db,
                user_id=user_id,
                actor=actor,
                action=action,
                entity_type=ENTITY_TYPE,
                entity_id=task.id,
                details={"title": task.title},
            )

    db.flush()
    return task


def delete_task(
    db: Session,
    *,
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    actor: str = activity_service.ACTOR_USER,
) -> None:
    task = get_task(db, user_id=user_id, task_id=task_id)
    activity_service.record(
        db,
        user_id=user_id,
        actor=actor,
        action="task.deleted",
        entity_type=ENTITY_TYPE,
        entity_id=task.id,
        details={"title": task.title},
    )
    db.delete(task)
    db.flush()


def group_open_tasks_by_priority(
    db: Session, *, user_id: uuid.UUID, per_priority: int = DASHBOARD_TASKS_PER_PRIORITY
) -> dict[TaskPriority, PriorityGroup]:
    """The first few open tasks of each priority plus the total per priority (FR-DASH-3)."""
    position = (
        func.row_number()
        .over(
            partition_by=Task.priority,
            order_by=(Task.due_at.asc().nulls_last(), Task.created_at.asc(), Task.id.asc()),
        )
        .label("position")
    )
    total = func.count().over(partition_by=Task.priority).label("total")
    ranked = (
        select(Task.id.label("task_id"), position, total)
        .where(Task.user_id == user_id, Task.status == TaskStatus.TODO)
        .subquery()
    )
    rows = db.execute(
        select(Task, ranked.c.total)
        .join(ranked, Task.id == ranked.c.task_id)
        .where(ranked.c.position <= per_priority)
        .order_by(Task.priority.asc(), ranked.c.position.asc())
    ).all()

    items_by_priority: dict[TaskPriority, list[Task]] = {priority: [] for priority in TaskPriority}
    totals: dict[TaskPriority, int] = dict.fromkeys(TaskPriority, 0)
    for task, priority_total in rows:
        items_by_priority[task.priority].append(task)
        totals[task.priority] = priority_total
    return {
        priority: PriorityGroup(items=items_by_priority[priority], total=totals[priority])
        for priority in TaskPriority
    }
