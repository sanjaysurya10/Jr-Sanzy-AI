from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.core.time import utc_now
from app.schemas.dashboard import DashboardRead
from app.services import dashboard_service

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardRead)
def get_dashboard(db: DbSession, user: CurrentUser) -> DashboardRead:
    return dashboard_service.get_dashboard(db, user=user, now=utc_now())
