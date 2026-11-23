"""Checks on the schema the migrations produce: RLS, drift from the models, cascades."""

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Engine, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.activity_log import ActivityLog
from app.models.task import Task
from app.models.user import User
from app.models.user_settings import UserSettings

EXPECTED_TABLES = {
    "alembic_version",
    "users",
    "user_settings",
    "api_keys",
    "tasks",
    "activity_logs",
}


def test_every_table_has_row_level_security_enabled(engine: Engine) -> None:
    with engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT c.relname, c.relrowsecurity FROM pg_class c "
                "JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE n.nspname = 'public' AND c.relkind = 'r'"
            )
        ).all()

    rls_by_table = {table_name: is_enabled for table_name, is_enabled in rows}
    assert set(rls_by_table) >= EXPECTED_TABLES
    tables_without_rls = sorted(name for name, is_enabled in rls_by_table.items() if not is_enabled)
    assert tables_without_rls == []


def test_no_table_has_an_rls_policy(engine: Engine) -> None:
    """RLS with no policies means anon and authenticated roles can touch nothing."""
    with engine.connect() as connection:
        policy_count = connection.scalar(
            text("SELECT count(*) FROM pg_policies WHERE schemaname = 'public'")
        )

    assert policy_count == 0


def test_every_model_table_is_covered_by_the_rls_check() -> None:
    assert set(Base.metadata.tables) | {"alembic_version"} == EXPECTED_TABLES


def test_migrations_match_the_models(engine: Engine) -> None:
    with engine.connect() as connection:
        migration_context = MigrationContext.configure(connection, opts={"compare_type": True})
        differences = compare_metadata(migration_context, Base.metadata)

    assert differences == []


def test_every_user_owned_table_cascades_from_users(engine: Engine) -> None:
    with engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT c.conrelid::regclass::text, c.confdeltype FROM pg_constraint c "
                "WHERE c.contype = 'f' AND c.confrelid = 'users'::regclass"
            )
        ).all()

    delete_rule_by_table = {table_name: rule for table_name, rule in rows}
    assert set(delete_rule_by_table) == EXPECTED_TABLES - {"alembic_version", "users"}
    assert set(delete_rule_by_table.values()) == {"c"}  # "c" is ON DELETE CASCADE


def test_deleting_a_user_removes_everything_they_own(db_session: Session) -> None:
    user = User(auth_user_id="to-delete")
    db_session.add(user)
    db_session.flush()
    db_session.add_all(
        [
            UserSettings(user_id=user.id),
            Task(user_id=user.id, title="Doomed"),
            ActivityLog(user_id=user.id, actor="user", action="task.created"),
        ]
    )
    db_session.flush()

    db_session.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user.id})

    for model in (UserSettings, Task, ActivityLog):
        assert db_session.scalar(select(func.count()).select_from(model)) == 0


def test_auth_user_id_is_unique(db_session: Session) -> None:
    db_session.add(User(auth_user_id="duplicate"))
    db_session.flush()
    db_session.add(User(auth_user_id="duplicate"))

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_a_user_can_have_only_one_settings_row(db_session: Session) -> None:
    user = User(auth_user_id="one-settings-row")
    db_session.add(user)
    db_session.flush()
    db_session.add(UserSettings(user_id=user.id))
    db_session.flush()
    db_session.add(UserSettings(user_id=user.id))

    with pytest.raises(IntegrityError):
        db_session.flush()
