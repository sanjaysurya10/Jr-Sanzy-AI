from typing import Any

import pytest
from pydantic import ValidationError

from app.core.config import Settings

REQUIRED: dict[str, Any] = {
    "database_url": "postgresql+psycopg://user:pw@localhost:5432/db",
    "supabase_url": "https://example.supabase.co",
}


def build_settings(**overrides: Any) -> Settings:
    return Settings(_env_file=None, **{**REQUIRED, **overrides})


def test_settings_default_to_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)

    assert build_settings().app_env == "local"


def test_settings_read_app_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")

    assert build_settings().app_env == "production"


def test_settings_reject_unknown_app_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "staging")

    with pytest.raises(ValidationError):
        build_settings()


def test_settings_require_database_and_supabase_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)

    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None)

    missing_fields = {failure["loc"][0] for failure in error.value.errors()}
    assert missing_fields == {"database_url", "supabase_url"}


def test_cors_origin_list_splits_and_trims() -> None:
    settings = build_settings(cors_origins=" http://localhost:3000 ,https://a.example,, ")

    assert settings.cors_origin_list == ["http://localhost:3000", "https://a.example"]


@pytest.mark.parametrize("scheme", ["postgresql://", "postgres://"])
def test_database_url_gets_the_psycopg_driver(scheme: str) -> None:
    settings = build_settings(database_url=f"{scheme}user:pw@host:5432/db?sslmode=require")

    assert settings.database_url == "postgresql+psycopg://user:pw@host:5432/db?sslmode=require"


def test_database_url_with_driver_is_left_alone() -> None:
    assert build_settings().database_url == REQUIRED["database_url"]
