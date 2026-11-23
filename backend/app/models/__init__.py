"""Importing this package registers every table on Base.metadata."""

from app.models.activity_log import ActivityLog
from app.models.api_key import ApiKey
from app.models.task import Task, TaskPriority, TaskSource, TaskStatus
from app.models.user import User
from app.models.user_settings import UserSettings

__all__ = [
    "ActivityLog",
    "ApiKey",
    "Task",
    "TaskPriority",
    "TaskSource",
    "TaskStatus",
    "User",
    "UserSettings",
]
