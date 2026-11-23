import uuid
from typing import Annotated

from fastapi import APIRouter, Query, Response
from pydantic import AwareDatetime

from app.api.deps import CurrentUser, DbSession
from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.tasks import TaskCreate, TaskList, TaskRead, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskList)
def list_tasks(
    db: DbSession,
    user: CurrentUser,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    due_before: AwareDatetime | None = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    cursor: str | None = None,
) -> task_service.TaskPage:
    return task_service.list_tasks(
        db,
        user_id=user.id,
        status=status,
        priority=priority,
        due_before=due_before,
        query=q,
        limit=limit,
        cursor=cursor,
    )


@router.post("", response_model=TaskRead, status_code=201)
def create_task(db: DbSession, user: CurrentUser, data: TaskCreate) -> Task:
    task = task_service.create_task(db, user_id=user.id, data=data)
    db.commit()
    return task


@router.get("/{task_id}", response_model=TaskRead)
def get_task(db: DbSession, user: CurrentUser, task_id: uuid.UUID) -> Task:
    return task_service.get_task(db, user_id=user.id, task_id=task_id)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(db: DbSession, user: CurrentUser, task_id: uuid.UUID, data: TaskUpdate) -> Task:
    task = task_service.update_task(db, user_id=user.id, task_id=task_id, data=data)
    db.commit()
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(db: DbSession, user: CurrentUser, task_id: uuid.UUID) -> Response:
    task_service.delete_task(db, user_id=user.id, task_id=task_id)
    db.commit()
    return Response(status_code=204)
