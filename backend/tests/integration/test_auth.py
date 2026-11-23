import re
import time
import uuid

import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_settings import UserSettings
from tests.conftest import AuthHeaders
from tests.support import TokenFactory

PUBLIC_PATHS = {"/api/v1/health"}


def _protected_routes(app: FastAPI) -> list[tuple[str, str]]:
    """Every operation in the OpenAPI spec except the public ones, with ids filled in."""
    routes: list[tuple[str, str]] = []
    for path, operations in app.openapi()["paths"].items():
        if path in PUBLIC_PATHS:
            continue
        concrete_path = re.sub(r"\{[^}]+\}", str(uuid.uuid4()), path)
        routes.extend((method.upper(), concrete_path) for method in sorted(operations))
    return routes


async def test_every_non_public_route_returns_401_without_a_token(
    app: FastAPI, client: AsyncClient
) -> None:
    protected_routes = _protected_routes(app)
    assert len(protected_routes) >= 7  # /me, /dashboard and five task operations

    for method, path in protected_routes:
        response = await client.request(method, path)

        assert response.status_code == 401, f"{method} {path} is reachable without a token"
        assert response.json()["error"]["code"] == "UNAUTHENTICATED"


async def test_missing_token_uses_the_standard_error_body(client: AsyncClient) -> None:
    response = await client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.json() == {
        "error": {"code": "UNAUTHENTICATED", "message": "Missing bearer token", "details": {}}
    }


@pytest.mark.parametrize(
    "authorization",
    ["Bearer not-a-jwt", "Basic dXNlcjpwYXNz", "Bearer", "token-without-scheme"],
)
async def test_bad_authorization_header_is_rejected(
    client: AsyncClient, authorization: str
) -> None:
    response = await client.get("/api/v1/me", headers={"Authorization": authorization})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


async def test_expired_token_is_rejected(client: AsyncClient, token_factory: TokenFactory) -> None:
    token = token_factory.make_token(exp=int(time.time()) - 10)

    response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


async def test_token_signed_by_another_key_is_rejected(
    client: AsyncClient, token_factory: TokenFactory
) -> None:
    forged = token_factory.make_token(signing_key=ec.generate_private_key(ec.SECP256R1()))

    response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {forged}"})

    assert response.status_code == 401


async def test_rejected_token_creates_no_user(
    client: AsyncClient, token_factory: TokenFactory, db_session: Session
) -> None:
    token = token_factory.make_token(subject="never-created", exp=int(time.time()) - 10)

    await client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})

    assert db_session.scalar(select(func.count()).select_from(User)) == 0


async def test_first_request_creates_the_user_and_default_settings(
    client: AsyncClient, auth_headers: AuthHeaders, db_session: Session
) -> None:
    response = await client.get(
        "/api/v1/me", headers=auth_headers(subject="new-user", email="new@example.com")
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "new@example.com"
    assert body["display_name"] is None
    assert body["timezone"] == "Europe/Dublin"

    user = db_session.scalars(select(User).where(User.auth_user_id == "new-user")).one()
    assert str(user.id) == body["id"]
    user_settings = db_session.scalars(
        select(UserSettings).where(UserSettings.user_id == user.id)
    ).one()
    assert user_settings.daily_limit_eur == 0
    assert user_settings.monthly_limit_eur == 0
    assert user_settings.relevance_threshold == 70
    assert user_settings.laptop_greeting_enabled is True


async def test_repeat_requests_reuse_the_same_user(
    client: AsyncClient, auth_headers: AuthHeaders, db_session: Session
) -> None:
    first = await client.get("/api/v1/me", headers=auth_headers())
    second = await client.get("/api/v1/me", headers=auth_headers())

    assert first.json()["id"] == second.json()["id"]
    assert db_session.scalar(select(func.count()).select_from(User)) == 1
    assert db_session.scalar(select(func.count()).select_from(UserSettings)) == 1


async def test_different_subjects_get_different_users(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    first = await client.get("/api/v1/me", headers=auth_headers(subject="user-a"))
    second = await client.get("/api/v1/me", headers=auth_headers(subject="user-b"))

    assert first.json()["id"] != second.json()["id"]


async def test_token_without_email_still_creates_a_user(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    response = await client.get("/api/v1/me", headers=auth_headers(email=None))

    assert response.status_code == 200
    assert response.json()["email"] is None
