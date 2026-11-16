import json
import logging

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from app.core.errors import AppError, ErrorCode, register_error_handlers
from app.core.logging import JsonFormatter, request_id_var


class EchoRequest(BaseModel):
    count: int


def build_app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/budget")
    async def raise_budget() -> None:
        raise AppError(ErrorCode.BUDGET_EXCEEDED, "Daily budget reached", details={"task": "x"})

    @app.get("/task")
    async def raise_task_not_found() -> None:
        raise AppError("TASK_NOT_FOUND", "Task not found", status_code=404)

    @app.get("/boom")
    async def raise_unexpected() -> None:
        raise RuntimeError("secret internal detail")

    @app.post("/echo")
    async def echo(body: EchoRequest) -> EchoRequest:
        return body

    return app


@pytest.fixture
async def error_client() -> AsyncClient:
    transport = ASGITransport(app=build_app(), raise_app_exceptions=False)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_app_error_maps_code_to_status(error_client: AsyncClient) -> None:
    response = await error_client.get("/budget")

    assert response.status_code == 402
    assert response.json() == {
        "error": {
            "code": "BUDGET_EXCEEDED",
            "message": "Daily budget reached",
            "details": {"task": "x"},
        }
    }


async def test_app_error_accepts_specific_code_with_status(error_client: AsyncClient) -> None:
    response = await error_client.get("/task")

    assert response.status_code == 404
    assert response.json()["error"] == {
        "code": "TASK_NOT_FOUND",
        "message": "Task not found",
        "details": {},
    }


async def test_unexpected_error_hides_internal_detail(error_client: AsyncClient) -> None:
    response = await error_client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "INTERNAL", "message": "Internal server error", "details": {}}
    }


async def test_validation_error_does_not_echo_input(error_client: AsyncClient) -> None:
    response = await error_client.post("/echo", json={"count": "not-a-number-secret"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"]["fields"][0]["loc"] == ["body", "count"]
    assert "not-a-number-secret" not in response.text


def test_json_formatter_includes_request_id_and_extra_fields() -> None:
    record = logging.makeLogRecord(
        {"name": "app.test", "levelname": "INFO", "msg": "request", "status_code": 200}
    )
    context_token = request_id_var.set("abc123")
    try:
        payload = json.loads(JsonFormatter().format(record))
    finally:
        request_id_var.reset(context_token)

    assert payload["message"] == "request"
    assert payload["request_id"] == "abc123"
    assert payload["status_code"] == 200
    assert payload["level"] == "INFO"
