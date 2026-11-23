from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PSYCOPG_SCHEME = "postgresql+psycopg://"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["local", "production"] = "local"
    cors_origins: str = "http://localhost:3000"
    database_url: str
    supabase_url: str
    supabase_jwt_secret: str = ""

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        # Supabase hands out postgresql:// URLs; SQLAlchemy needs the driver named.
        for scheme in ("postgresql://", "postgres://"):
            if value.startswith(scheme):
                return _PSYCOPG_SCHEME + value[len(scheme) :]
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
