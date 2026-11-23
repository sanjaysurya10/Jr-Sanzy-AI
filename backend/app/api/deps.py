from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import AppError, ErrorCode
from app.core.security import TokenVerifier
from app.models.user import User
from app.services import user_service

_bearer_scheme = HTTPBearer(auto_error=False)


def get_db(request: Request) -> Iterator[Session]:
    """One session per request. Endpoints that change data commit explicitly."""
    session: Session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()


def get_token_verifier(request: Request) -> TokenVerifier:
    verifier: TokenVerifier = request.app.state.token_verifier
    return verifier


DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    verifier: Annotated[TokenVerifier, Depends(get_token_verifier)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> User:
    """Verify the bearer token and return its user, creating the row on first sight.

    The user always comes from the verified token, never from the request body (SEC-3).
    """
    if credentials is None:
        raise AppError(ErrorCode.UNAUTHENTICATED, "Missing bearer token")
    claims = verifier.verify(credentials.credentials)
    email = claims.get("email")
    user = user_service.get_or_create_user(
        db, auth_user_id=claims["sub"], email=email if isinstance(email, str) else None
    )
    db.commit()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
