from datetime import time
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, Integer, Numeric, Time, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UserOwnedMixin, UUIDPrimaryKeyMixin


class UserSettings(UUIDPrimaryKeyMixin, TimestampMixin, UserOwnedMixin, Base):
    __tablename__ = "user_settings"
    __table_args__ = (UniqueConstraint("user_id"),)

    calorie_target: Mapped[int | None] = mapped_column(Integer)
    protein_target_g: Mapped[int | None] = mapped_column(Integer)
    career_profile: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default=text("'{}'"))
    email_filters: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default=text("'{}'"))
    earliest_wake_time: Mapped[time] = mapped_column(Time, server_default=text("'05:30'"))
    min_sleep_hours: Mapped[Decimal] = mapped_column(Numeric(4, 2), server_default=text("4"))
    briefing_fallback_time: Mapped[time] = mapped_column(Time, server_default=text("'10:00'"))
    quiet_start: Mapped[time] = mapped_column(Time, server_default=text("'23:00'"))
    quiet_end: Mapped[time] = mapped_column(Time, server_default=text("'07:00'"))
    daily_limit_eur: Mapped[Decimal] = mapped_column(Numeric(10, 4), server_default=text("0"))
    monthly_limit_eur: Mapped[Decimal] = mapped_column(Numeric(10, 4), server_default=text("0"))
    relevance_threshold: Mapped[int] = mapped_column(Integer, server_default=text("70"))
    laptop_greeting_enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
