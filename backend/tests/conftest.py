from collections.abc import AsyncIterator, Callable, Iterator
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from alembic import command
from app.api.deps import get_db, get_token_verifier
from app.core.config import Settings
from app.main import create_app
from tests.support import SUPABASE_URL, TokenFactory

BACKEND_DIR = Path(__file__).resolve().parent.parent

AuthHeaders = Callable[..., dict[str, str]]


class TestEnvironment(BaseSettings):
    __test__ = False  # not a test class, despite the name

    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    test_database_url: str = ""


def _build_settings(database_url: str) -> Settings:
    return Settings(
        _env_file=None,
        app_env="local",
        cors_origins="http://localhost:3000",
        database_url=database_url,
        supabase_url=SUPABASE_URL,
    )


@pytest.fixture(scope="session")
def test_database_url() -> str:
    url = TestEnvironment().test_database_url
    if not url:
        pytest.fail(
            "TEST_DATABASE_URL is not set. Add it to backend/.env (see .env.example). "
            "It must point at a throwaway Postgres database."
        )
    return _build_settings(url).database_url


@pytest.fixture(scope="session")
def engine(test_database_url: str) -> Iterator[Engine]:
    """A clean schema built by the real Alembic migrations, once per test run."""
    engine = create_engine(test_database_url)
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
    alembic_config = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_config.attributes["database_url"] = test_database_url
    command.upgrade(alembic_config, "head")
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Iterator[Session]:
    """Each test runs inside one outer transaction that is rolled back afterwards.
    Commits made by the code under test only release savepoints."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
    )
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def settings(test_database_url: str) -> Settings:
    return _build_settings(test_database_url)


@pytest.fixture(scope="session")
def token_factory() -> TokenFactory:
    return TokenFactory()


@pytest.fixture
def app(settings: Settings, db_session: Session, token_factory: TokenFactory) -> FastAPI:
    application = create_app(settings)

    def override_get_db() -> Iterator[Session]:
        yield db_session

    application.dependency_overrides[get_db] = override_get_db
    application.dependency_overrides[get_token_verifier] = token_factory.build_verifier
    return application


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture
def auth_headers(token_factory: TokenFactory) -> AuthHeaders:
    def build(
        subject: str = "auth-user-1", email: str | None = "user1@example.com"
    ) -> dict[str, str]:
        token = token_factory.make_token(subject=subject, email=email)
        return {"Authorization": f"Bearer {token}"}

    return build
