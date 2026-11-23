from sqlalchemy import create_engine, pool

import app.models  # noqa: F401  (registers every table on Base.metadata)
from alembic import context
from app.core.config import get_settings
from app.db.base import Base

config = context.config
target_metadata = Base.metadata


def _database_url() -> str:
    # Tests pass their own URL through config.attributes; everything else uses settings.
    override = config.attributes.get("database_url")
    return str(override) if override else get_settings().database_url


def run_migrations_online() -> None:
    engine = create_engine(_database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    raise RuntimeError("Offline migrations are not supported; run against a database.")

run_migrations_online()
