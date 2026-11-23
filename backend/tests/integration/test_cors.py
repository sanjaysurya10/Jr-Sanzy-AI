from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import create_app

ALLOWED_ORIGIN = "http://localhost:3000"


async def test_allowed_origin_gets_cors_header(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health", headers={"Origin": ALLOWED_ORIGIN})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN


async def test_unknown_origin_gets_no_cors_header(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health", headers={"Origin": "https://evil.example"})

    assert "access-control-allow-origin" not in response.headers


async def test_preflight_allows_authorization_header(client: AsyncClient) -> None:
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert "authorization" in response.headers["access-control-allow-headers"].lower()


async def test_preflight_from_unknown_origin_is_rejected(client: AsyncClient) -> None:
    response = await client.options(
        "/api/v1/health",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"},
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


async def test_error_responses_carry_cors_header(client: AsyncClient) -> None:
    response = await client.get("/api/v1/does-not-exist", headers={"Origin": ALLOWED_ORIGIN})

    assert response.status_code == 404
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN


async def test_every_configured_origin_is_allowed(settings: Settings) -> None:
    multi_origin_settings = settings.model_copy(
        update={"cors_origins": "http://localhost:3000, https://jr-sanzy.example"}
    )
    transport = ASGITransport(app=create_app(multi_origin_settings))

    async with AsyncClient(transport=transport, base_url="http://test") as multi_origin_client:
        response = await multi_origin_client.options(
            "/api/v1/health",
            headers={
                "Origin": "https://jr-sanzy.example",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.headers["access-control-allow-origin"] == "https://jr-sanzy.example"
