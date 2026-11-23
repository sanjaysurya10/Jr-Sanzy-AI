from collections.abc import Iterator

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import __version__
from app.api.deps import get_db


async def test_health_reports_status_database_and_version(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok", "version": __version__}
    assert response.headers["X-Request-ID"]


async def test_health_stays_200_and_reports_degraded_when_the_database_is_down(
    app: FastAPI, client: AsyncClient
) -> None:
    unreachable_engine = create_engine(
        "postgresql+psycopg://nobody:nothing@127.0.0.1:1/none",
        connect_args={"connect_timeout": 2},
    )

    def override_get_db() -> Iterator[Session]:
        with Session(unreachable_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "degraded", "db": "error", "version": __version__}


async def test_openapi_lists_health_under_api_v1(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/health" in response.json()["paths"]


async def test_docs_page_is_served(client: AsyncClient) -> None:
    response = await client.get("/docs")

    assert response.status_code == 200


async def test_unknown_route_uses_standard_error_body(client: AsyncClient) -> None:
    response = await client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "NOT_FOUND", "message": "Not Found", "details": {}}
    }


async def test_wrong_method_uses_standard_error_body(client: AsyncClient) -> None:
    response = await client.post("/api/v1/health")

    assert response.status_code == 405
    assert response.json()["error"]["code"] == "METHOD_NOT_ALLOWED"
