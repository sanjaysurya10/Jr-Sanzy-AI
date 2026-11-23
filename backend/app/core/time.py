"""User-local time helpers. The database stores UTC; users think in their own timezone."""

from datetime import UTC, datetime, time
from typing import Literal
from zoneinfo import ZoneInfo

GreetingPeriod = Literal["morning", "afternoon", "evening"]

_MORNING_START = time(5, 0)
_AFTERNOON_START = time(12, 0)
_EVENING_START = time(17, 0)


def utc_now() -> datetime:
    return datetime.now(UTC)


def to_user_local(moment: datetime, timezone: str) -> datetime:
    return moment.astimezone(ZoneInfo(timezone))


def greeting_period(local_time: time) -> GreetingPeriod:
    """Morning 05:00-11:59, afternoon 12:00-16:59, evening 17:00-04:59 (FR-DASH-2)."""
    if _MORNING_START <= local_time < _AFTERNOON_START:
        return "morning"
    if _AFTERNOON_START <= local_time < _EVENING_START:
        return "afternoon"
    return "evening"
