from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.models.user import User
from app.schemas.me import MeRead

router = APIRouter(tags=["me"])


@router.get("/me", response_model=MeRead)
def get_me(user: CurrentUser) -> User:
    return user
