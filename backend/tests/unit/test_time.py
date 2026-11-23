from datetime import UTC, datetime, time

import pytest

from app.core.time import greeting_period, to_user_local
from app.models.user import User
from app.services.dashboard_service import build_greeting


@pytest.mark.parametrize(
    ("local_time", "expected_period"),
    [
        (time(4, 59), "evening"),
        (time(5, 0), "morning"),
        (time(11, 59), "morning"),
        (time(12, 0), "afternoon"),
        (time(16, 59), "afternoon"),
        (time(17, 0), "evening"),
        (time(23, 59), "evening"),
        (time(0, 0), "evening"),
    ],
)
def test_greeting_period_boundaries(local_time: time, expected_period: str) -> None:
    assert greeting_period(local_time) == expected_period


def test_to_user_local_applies_dublin_summer_time() -> None:
    summer_moment = datetime(2026, 7, 1, 11, 30, tzinfo=UTC)

    local = to_user_local(summer_moment, "Europe/Dublin")

    assert (local.hour, local.minute) == (12, 30)


def test_to_user_local_matches_utc_in_dublin_winter() -> None:
    winter_moment = datetime(2026, 12, 1, 11, 30, tzinfo=UTC)

    assert to_user_local(winter_moment, "Europe/Dublin").hour == 11


def test_greeting_uses_the_users_local_time_not_utc() -> None:
    user = User(auth_user_id="a", display_name="Sanjay", timezone="Europe/Dublin")
    # 11:30 UTC is 12:30 in Dublin during summer time: afternoon, not morning.
    greeting = build_greeting(user, now=datetime(2026, 7, 1, 11, 30, tzinfo=UTC))

    assert greeting.period == "afternoon"
    assert greeting.text == "Good afternoon, Sanjay."


def test_greeting_without_display_name_has_no_trailing_comma() -> None:
    user = User(auth_user_id="a", display_name=None, timezone="Europe/Dublin")

    greeting = build_greeting(user, now=datetime(2026, 12, 1, 8, 0, tzinfo=UTC))

    assert greeting.text == "Good morning."
