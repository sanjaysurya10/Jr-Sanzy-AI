from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_settings import UserSettings


def get_or_create_user(db: Session, *, auth_user_id: str, email: str | None) -> User:
    """Return the user for a verified token, creating the user and settings on first sight.

    Inserts use ON CONFLICT DO NOTHING so two first requests arriving together cannot
    create duplicates or fail (FR-AUTH-3).
    """
    existing_user = db.scalars(select(User).where(User.auth_user_id == auth_user_id)).first()
    if existing_user is not None:
        return existing_user

    db.execute(
        insert(User)
        .values(auth_user_id=auth_user_id, email=email)
        .on_conflict_do_nothing(index_elements=[User.auth_user_id])
    )
    user = db.scalars(select(User).where(User.auth_user_id == auth_user_id)).one()
    db.execute(
        insert(UserSettings)
        .values(user_id=user.id)
        .on_conflict_do_nothing(index_elements=[UserSettings.user_id])
    )
    db.flush()
    return user
