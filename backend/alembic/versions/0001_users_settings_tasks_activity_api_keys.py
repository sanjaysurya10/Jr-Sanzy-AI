"""users, user_settings, api_keys, tasks, activity_logs

Revision ID: 0001
Revises:
Create Date: 2026-11-16

RLS is enabled on every table with no policies, so the Supabase anon and authenticated
roles can read and write nothing directly (PRD 5.2). The backend connects as the table
owner, which bypasses RLS.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_TABLES = ("users", "user_settings", "api_keys", "tasks", "activity_logs")


def _id_column() -> sa.Column[sa.Uuid]:
    return sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False)


def _timestamp_columns() -> list[sa.Column[sa.DateTime]]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("clock_timestamp()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("clock_timestamp()"),
            nullable=False,
        ),
    ]


def _user_id_column() -> sa.Column[sa.Uuid]:
    return sa.Column("user_id", sa.Uuid(), nullable=False)


def _user_foreign_key(table_name: str) -> sa.ForeignKeyConstraint:
    return sa.ForeignKeyConstraint(
        ["user_id"],
        ["users.id"],
        name=op.f(f"fk_{table_name}_user_id_users"),
        ondelete="CASCADE",
    )


def upgrade() -> None:
    op.create_table(
        "users",
        _id_column(),
        sa.Column("auth_user_id", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column("timezone", sa.Text(), server_default="Europe/Dublin", nullable=False),
        *_timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("auth_user_id", name=op.f("uq_users_auth_user_id")),
    )

    op.create_table(
        "user_settings",
        _id_column(),
        _user_id_column(),
        sa.Column("calorie_target", sa.Integer(), nullable=True),
        sa.Column("protein_target_g", sa.Integer(), nullable=True),
        sa.Column(
            "career_profile", postgresql.JSONB(), server_default=sa.text("'{}'"), nullable=False
        ),
        sa.Column(
            "email_filters", postgresql.JSONB(), server_default=sa.text("'{}'"), nullable=False
        ),
        sa.Column(
            "earliest_wake_time", sa.Time(), server_default=sa.text("'05:30'"), nullable=False
        ),
        sa.Column("min_sleep_hours", sa.Numeric(4, 2), server_default=sa.text("4"), nullable=False),
        sa.Column(
            "briefing_fallback_time", sa.Time(), server_default=sa.text("'10:00'"), nullable=False
        ),
        sa.Column("quiet_start", sa.Time(), server_default=sa.text("'23:00'"), nullable=False),
        sa.Column("quiet_end", sa.Time(), server_default=sa.text("'07:00'"), nullable=False),
        sa.Column(
            "daily_limit_eur", sa.Numeric(10, 4), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "monthly_limit_eur", sa.Numeric(10, 4), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "relevance_threshold", sa.Integer(), server_default=sa.text("70"), nullable=False
        ),
        sa.Column(
            "laptop_greeting_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        *_timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_settings")),
        _user_foreign_key("user_settings"),
        sa.UniqueConstraint("user_id", name=op.f("uq_user_settings_user_id")),
    )
    op.create_index(op.f("ix_user_settings_user_id"), "user_settings", ["user_id"])

    op.create_table(
        "api_keys",
        _id_column(),
        _user_id_column(),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("key_prefix", sa.String(length=8), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "scopes", postgresql.ARRAY(sa.Text()), server_default=sa.text("'{}'"), nullable=False
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_api_keys")),
        _user_foreign_key("api_keys"),
        sa.UniqueConstraint("key_hash", name=op.f("uq_api_keys_key_hash")),
    )
    op.create_index(op.f("ix_api_keys_user_id"), "api_keys", ["user_id"])

    op.create_table(
        "tasks",
        _id_column(),
        _user_id_column(),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "priority",
            sa.Enum("critical", "high", "normal", "low", name="task_priority"),
            server_default="normal",
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("todo", "done", "archived", name="task_status"),
            server_default="todo",
            nullable=False,
        ),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "source",
            sa.Enum("manual", "email", "ai_suggestion", name="task_source"),
            server_default="manual",
            nullable=False,
        ),
        sa.Column("source_ref", sa.Uuid(), nullable=True),
        *_timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tasks")),
        _user_foreign_key("tasks"),
    )
    op.create_index(op.f("ix_tasks_user_id"), "tasks", ["user_id"])
    op.create_index(
        "ix_tasks_user_status_priority_due", "tasks", ["user_id", "status", "priority", "due_at"]
    )

    op.create_table(
        "activity_logs",
        _id_column(),
        _user_id_column(),
        sa.Column("actor", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.Text(), nullable=True),
        sa.Column("entity_id", sa.Uuid(), nullable=True),
        sa.Column("details", postgresql.JSONB(), server_default=sa.text("'{}'"), nullable=False),
        *_timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_activity_logs")),
        _user_foreign_key("activity_logs"),
    )
    op.create_index(op.f("ix_activity_logs_user_id"), "activity_logs", ["user_id"])
    op.create_index(
        "ix_activity_logs_user_id_created_at",
        "activity_logs",
        ["user_id", sa.text("created_at DESC")],
    )

    # Supabase exposes every table in the public schema, including Alembic's own.
    for table_name in ("alembic_version", *NEW_TABLES):
        op.execute(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    for table_name in reversed(NEW_TABLES):
        op.drop_table(table_name)
    for enum_name in ("task_source", "task_status", "task_priority"):
        op.execute(f"DROP TYPE {enum_name}")
