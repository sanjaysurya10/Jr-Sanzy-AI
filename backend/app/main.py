import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging, request_id_var
from app.core.security import TokenVerifier
from app.db.session import build_session_factory

logger = logging.getLogger("app.request")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging()
    app = FastAPI(title="Jr Sanzy API", version=__version__)
    app.state.session_factory = build_session_factory(settings.database_url)
    app.state.token_verifier = TokenVerifier(
        supabase_url=settings.supabase_url, jwt_secret=settings.supabase_jwt_secret
    )

    @app.middleware("http")
    async def log_request(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = uuid.uuid4().hex
        context_token = request_id_var.set(request_id)
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            logger.info(
                "request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                },
            )
            request_id_var.reset(context_token)

    # Added last so it is the outermost layer: error responses carry CORS headers too.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
        expose_headers=["X-Request-ID"],
    )

    register_error_handlers(app)
    app.include_router(api_router, prefix="/api/v1")
    return app


_app: FastAPI | None = None


def __getattr__(name: str) -> FastAPI:
    """Build `app` on first access (`uvicorn app.main:app`), not on import, so importing
    create_app in tests does not require production settings in the environment."""
    global _app
    if name == "app":
        if _app is None:
            _app = create_app()
        return _app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
