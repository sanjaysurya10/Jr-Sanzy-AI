import base64
import json

import pytest

from app.core.errors import AppError
from app.services.task_service import decode_cursor, encode_cursor


def encode_raw(payload: object) -> str:
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def test_missing_cursor_starts_at_the_beginning() -> None:
    assert decode_cursor(None) == 0


def test_cursor_round_trips() -> None:
    assert decode_cursor(encode_cursor(40)) == 40


@pytest.mark.parametrize(
    "bad_cursor",
    [
        "not-base64!!",
        encode_raw({"offset": -1}),
        encode_raw({"offset": "10"}),
        encode_raw({"offset": True}),
        encode_raw({"other": 1}),
        encode_raw([1, 2]),
        base64.urlsafe_b64encode(b"not json").decode(),
    ],
)
def test_invalid_cursor_is_a_validation_error(bad_cursor: str) -> None:
    with pytest.raises(AppError) as error:
        decode_cursor(bad_cursor)

    assert error.value.status_code == 422
    assert error.value.code == "VALIDATION_ERROR"
