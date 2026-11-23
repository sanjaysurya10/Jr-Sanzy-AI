from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import __version__
from app.api.deps import DbSession

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    db: Literal["ok", "error"]
    version: str


@router.get("/health", response_model=HealthResponse)
def get_health(db: DbSession) -> HealthResponse:
    """Liveness plus a database check. Always 200 while the process is up, so callers
    waiting for a cold start (FR-FOOD-10) see it as soon as the server answers."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return HealthResponse(status="degraded", db="error", version=__version__)
    return HealthResponse(status="ok", db="ok", version=__version__)
