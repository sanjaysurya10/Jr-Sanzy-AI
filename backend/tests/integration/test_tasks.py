import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from tests.conftest import AuthHeaders

TASKS_URL = "/api/v1/tasks"


async def create_task(
    client: AsyncClient, headers: dict[str, str], **fields: Any
) -> dict[str, Any]:
    response = await client.post(TASKS_URL, json={"title": "Task", **fields}, headers=headers)
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


def activity_actions(db_session: Session, task_id: str) -> list[str]:
    statement = (
        select(ActivityLog.action)
        .where(ActivityLog.entity_id == uuid.UUID(task_id))
        .order_by(ActivityLog.created_at)
    )
    return list(db_session.scalars(statement))


def iso(moment: datetime) -> str:
    return moment.isoformat()


# --- Create -----------------------------------------------------------------------------


async def test_create_task_applies_defaults(client: AsyncClient, auth_headers: AuthHeaders) -> None:
    task = await create_task(client, auth_headers(), title="Email the recruiter")

    assert task["title"] == "Email the recruiter"
    assert task["priority"] == "normal"
    assert task["status"] == "todo"
    assert task["source"] == "manual"
    assert task["notes"] is None
    assert task["due_at"] is None
    assert task["completed_at"] is None
    assert task["source_ref"] is None
    assert task["is_overdue"] is False


async def test_create_task_stores_all_fields(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    due_at = datetime(2030, 1, 15, 9, 0, tzinfo=UTC)

    task = await create_task(
        client,
        auth_headers(),
        title="  Submit form  ",
        notes="Bring passport",
        priority="critical",
        due_at=iso(due_at),
    )

    assert task["title"] == "Submit form"
    assert task["notes"] == "Bring passport"
    assert task["priority"] == "critical"
    assert datetime.fromisoformat(task["due_at"]) == due_at


async def test_create_task_writes_an_activity_entry(
    client: AsyncClient, auth_headers: AuthHeaders, db_session: Session
) -> None:
    task = await create_task(client, auth_headers(), title="Buy milk", priority="low")

    entry = db_session.scalars(
        select(ActivityLog).where(ActivityLog.entity_id == uuid.UUID(task["id"]))
    ).one()
    assert entry.actor == "user"
    assert entry.action == "task.created"
    assert entry.entity_type == "task"
    assert entry.details == {"title": "Buy milk", "priority": "low"}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": ""},
        {"title": "   "},
        {"title": "x" * 201},
        {"title": "ok", "priority": "urgent"},
        {"title": "ok", "due_at": "2030-01-15T09:00:00"},  # no timezone
        {"title": "ok", "due_at": "tomorrow"},
        {"title": "ok", "user_id": str(uuid.uuid4())},  # never trusted from the body
        {"title": "ok", "status": "done"},
        {"title": "ok", "source": "email"},
    ],
)
async def test_create_task_rejects_invalid_input(
    client: AsyncClient, auth_headers: AuthHeaders, payload: dict[str, Any]
) -> None:
    response = await client.post(TASKS_URL, json=payload, headers=auth_headers())

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_title_of_exactly_200_characters_is_accepted(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    task = await create_task(client, auth_headers(), title="x" * 200)

    assert len(task["title"]) == 200


# --- Read one ---------------------------------------------------------------------------


async def test_get_task_returns_the_task(client: AsyncClient, auth_headers: AuthHeaders) -> None:
    created = await create_task(client, auth_headers(), title="Read me")

    response = await client.get(f"{TASKS_URL}/{created['id']}", headers=auth_headers())

    assert response.status_code == 200
    assert response.json() == created


async def test_get_unknown_task_returns_404(client: AsyncClient, auth_headers: AuthHeaders) -> None:
    response = await client.get(f"{TASKS_URL}/{uuid.uuid4()}", headers=auth_headers())

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "TASK_NOT_FOUND", "message": "Task not found", "details": {}}
    }


async def test_get_task_with_malformed_id_returns_422(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    response = await client.get(f"{TASKS_URL}/not-a-uuid", headers=auth_headers())

    assert response.status_code == 422


# --- Isolation between users ------------------------------------------------------------


async def test_another_users_task_is_not_found_for_read_update_and_delete(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    owner = auth_headers(subject="owner")
    intruder = auth_headers(subject="intruder")
    task = await create_task(client, owner, title="Private")
    task_url = f"{TASKS_URL}/{task['id']}"

    read = await client.get(task_url, headers=intruder)
    update = await client.patch(task_url, json={"title": "Hacked"}, headers=intruder)
    delete = await client.delete(task_url, headers=intruder)

    assert (read.status_code, update.status_code, delete.status_code) == (404, 404, 404)
    untouched = await client.get(task_url, headers=owner)
    assert untouched.json()["title"] == "Private"


async def test_list_returns_only_the_callers_tasks(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    await create_task(client, auth_headers(subject="owner"), title="Mine")
    await create_task(client, auth_headers(subject="other"), title="Theirs")

    response = await client.get(TASKS_URL, headers=auth_headers(subject="owner"))

    assert [task["title"] for task in response.json()["items"]] == ["Mine"]


# --- Update -----------------------------------------------------------------------------


async def test_update_changes_only_the_given_fields(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    task = await create_task(client, auth_headers(), title="Old", notes="Keep", priority="low")

    response = await client.patch(
        f"{TASKS_URL}/{task['id']}", json={"title": "New"}, headers=auth_headers()
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "New"
    assert updated["notes"] == "Keep"
    assert updated["priority"] == "low"
    assert updated["updated_at"] > task["updated_at"]


async def test_update_can_clear_notes_and_due_date(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    task = await create_task(
        client, auth_headers(), notes="Remove me", due_at="2030-01-15T09:00:00Z"
    )

    response = await client.patch(
        f"{TASKS_URL}/{task['id']}", json={"notes": None, "due_at": None}, headers=auth_headers()
    )

    assert response.json()["notes"] is None
    assert response.json()["due_at"] is None


@pytest.mark.parametrize(
    "payload",
    [
        {"title": None},
        {"priority": None},
        {"status": None},
        {"title": ""},
        {"status": "deleted"},
        {"source": "email"},
        {"completed_at": "2030-01-01T00:00:00Z"},
        {"user_id": str(uuid.uuid4())},
    ],
)
async def test_update_rejects_invalid_input(
    client: AsyncClient, auth_headers: AuthHeaders, payload: dict[str, Any]
) -> None:
    task = await create_task(client, auth_headers())

    response = await client.patch(f"{TASKS_URL}/{task['id']}", json=payload, headers=auth_headers())

    assert response.status_code == 422


async def test_completing_a_task_sets_completed_at_and_logs_it(
    client: AsyncClient, auth_headers: AuthHeaders, db_session: Session
) -> None:
    task = await create_task(client, auth_headers())
    before = datetime.now(UTC)

    response = await client.patch(
        f"{TASKS_URL}/{task['id']}", json={"status": "done"}, headers=auth_headers()
    )

    completed = response.json()
    assert completed["status"] == "done"
    assert datetime.fromisoformat(completed["completed_at"]) >= before - timedelta(seconds=1)
    assert activity_actions(db_session, task["id"]) == ["task.created", "task.completed"]


async def test_reopening_a_task_clears_completed_at_and_logs_it(
    client: AsyncClient, auth_headers: AuthHeaders, db_session: Session
) -> None:
    task = await create_task(client, auth_headers())
    task_url = f"{TASKS_URL}/{task['id']}"
    await client.patch(task_url, json={"status": "done"}, headers=auth_headers())

    response = await client.patch(task_url, json={"status": "todo"}, headers=auth_headers())

    assert response.json()["status"] == "todo"
    assert response.json()["completed_at"] is None
    assert activity_actions(db_session, task["id"]) == [
        "task.created",
        "task.completed",
        "task.reopened",
    ]


async def test_marking_a_done_task_done_again_changes_nothing(
    client: AsyncClient, auth_headers: AuthHeaders, db_session: Session
) -> None:
    task = await create_task(client, auth_headers())
    task_url = f"{TASKS_URL}/{task['id']}"
    first = await client.patch(task_url, json={"status": "done"}, headers=auth_headers())

    second = await client.patch(task_url, json={"status": "done"}, headers=auth_headers())

    assert second.json()["completed_at"] == first.json()["completed_at"]
    assert activity_actions(db_session, task["id"]) == ["task.created", "task.completed"]


async def test_archiving_a_done_task_clears_completed_at(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    task = await create_task(client, auth_headers())
    task_url = f"{TASKS_URL}/{task['id']}"
    await client.patch(task_url, json={"status": "done"}, headers=auth_headers())

    response = await client.patch(task_url, json={"status": "archived"}, headers=auth_headers())

    assert response.json()["status"] == "archived"
    assert response.json()["completed_at"] is None


# --- Overdue ----------------------------------------------------------------------------


async def test_open_task_past_its_due_time_is_overdue(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    yesterday = datetime.now(UTC) - timedelta(days=1)
    tomorrow = datetime.now(UTC) + timedelta(days=1)

    late = await create_task(client, auth_headers(), due_at=iso(yesterday))
    on_time = await create_task(client, auth_headers(), due_at=iso(tomorrow))

    assert late["is_overdue"] is True
    assert on_time["is_overdue"] is False


async def test_completed_task_is_never_overdue(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    yesterday = datetime.now(UTC) - timedelta(days=1)
    task = await create_task(client, auth_headers(), due_at=iso(yesterday))

    response = await client.patch(
        f"{TASKS_URL}/{task['id']}", json={"status": "done"}, headers=auth_headers()
    )

    assert response.json()["is_overdue"] is False


# --- Delete -----------------------------------------------------------------------------


async def test_delete_removes_the_task_and_logs_it(
    client: AsyncClient, auth_headers: AuthHeaders, db_session: Session
) -> None:
    task = await create_task(client, auth_headers(), title="Throwaway")
    task_url = f"{TASKS_URL}/{task['id']}"

    response = await client.delete(task_url, headers=auth_headers())

    assert response.status_code == 204
    assert response.content == b""
    assert (await client.get(task_url, headers=auth_headers())).status_code == 404
    assert activity_actions(db_session, task["id"]) == ["task.created", "task.deleted"]


async def test_deleting_twice_returns_404_the_second_time(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    task = await create_task(client, auth_headers())
    task_url = f"{TASKS_URL}/{task['id']}"
    await client.delete(task_url, headers=auth_headers())

    response = await client.delete(task_url, headers=auth_headers())

    assert response.status_code == 404


# --- List: sorting, filters, pagination -------------------------------------------------


async def test_list_sorts_by_priority_then_due_date_then_age(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    await create_task(client, headers, title="normal, no date, older")
    await create_task(
        client, headers, title="low, soon", priority="low", due_at="2030-01-01T00:00:00Z"
    )
    await create_task(client, headers, title="normal, later", due_at="2030-06-01T00:00:00Z")
    await create_task(client, headers, title="critical, no date", priority="critical")
    await create_task(client, headers, title="normal, sooner", due_at="2030-02-01T00:00:00Z")
    await create_task(client, headers, title="high", priority="high")
    await create_task(client, headers, title="normal, no date, newer")

    response = await client.get(TASKS_URL, headers=headers)

    assert [task["title"] for task in response.json()["items"]] == [
        "critical, no date",
        "high",
        "normal, sooner",
        "normal, later",
        "normal, no date, older",
        "normal, no date, newer",
        "low, soon",
    ]
    assert response.json()["next_cursor"] is None


async def test_list_filters_by_status_and_priority(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    await create_task(client, headers, title="open high", priority="high")
    done = await create_task(client, headers, title="done high", priority="high")
    await create_task(client, headers, title="open low", priority="low")
    await client.patch(f"{TASKS_URL}/{done['id']}", json={"status": "done"}, headers=headers)

    by_status = await client.get(TASKS_URL, params={"status": "done"}, headers=headers)
    by_priority = await client.get(TASKS_URL, params={"priority": "high"}, headers=headers)
    by_both = await client.get(
        TASKS_URL, params={"status": "todo", "priority": "high"}, headers=headers
    )

    assert [task["title"] for task in by_status.json()["items"]] == ["done high"]
    assert {task["title"] for task in by_priority.json()["items"]} == {"open high", "done high"}
    assert [task["title"] for task in by_both.json()["items"]] == ["open high"]


async def test_list_filters_by_due_before(client: AsyncClient, auth_headers: AuthHeaders) -> None:
    headers = auth_headers()
    await create_task(client, headers, title="january", due_at="2030-01-10T00:00:00Z")
    await create_task(client, headers, title="march", due_at="2030-03-10T00:00:00Z")
    await create_task(client, headers, title="undated")

    response = await client.get(
        TASKS_URL, params={"due_before": "2030-02-01T00:00:00Z"}, headers=headers
    )

    assert [task["title"] for task in response.json()["items"]] == ["january"]


async def test_list_searches_title_and_notes_case_insensitively(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    await create_task(client, headers, title="Email the Recruiter")
    await create_task(client, headers, title="Call back", notes="recruiter from Dublin")
    await create_task(client, headers, title="Buy milk")

    response = await client.get(TASKS_URL, params={"q": "RECRUITER"}, headers=headers)

    assert {task["title"] for task in response.json()["items"]} == {
        "Email the Recruiter",
        "Call back",
    }


async def test_search_treats_wildcard_characters_literally(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    await create_task(client, headers, title="100% done")
    await create_task(client, headers, title="100 percent")

    response = await client.get(TASKS_URL, params={"q": "100%"}, headers=headers)

    assert [task["title"] for task in response.json()["items"]] == ["100% done"]


async def test_list_pages_through_every_task_exactly_once(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    for number in range(5):
        await create_task(client, headers, title=f"task {number}")

    seen_titles: list[str] = []
    cursor: str | None = None
    page_sizes: list[int] = []
    while True:
        params: dict[str, str | int] = {"limit": 2}
        if cursor is not None:
            params["cursor"] = cursor
        page = (await client.get(TASKS_URL, params=params, headers=headers)).json()
        page_sizes.append(len(page["items"]))
        seen_titles.extend(task["title"] for task in page["items"])
        cursor = page["next_cursor"]
        if cursor is None:
            break

    assert page_sizes == [2, 2, 1]
    assert seen_titles == [f"task {number}" for number in range(5)]


async def test_list_has_no_next_cursor_when_the_page_is_exactly_full(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    for number in range(2):
        await create_task(client, headers, title=f"task {number}")

    response = await client.get(TASKS_URL, params={"limit": 2}, headers=headers)

    assert len(response.json()["items"]) == 2
    assert response.json()["next_cursor"] is None


async def test_list_defaults_to_twenty_items(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    for number in range(21):
        await create_task(client, headers, title=f"task {number}")

    response = await client.get(TASKS_URL, headers=headers)

    assert len(response.json()["items"]) == 20
    assert response.json()["next_cursor"] is not None


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"cursor": "garbage"},
        {"status": "deleted"},
        {"priority": "urgent"},
        {"due_before": "2030-01-01T00:00:00"},
        {"q": "x" * 201},
    ],
)
async def test_list_rejects_invalid_query_parameters(
    client: AsyncClient, auth_headers: AuthHeaders, params: dict[str, Any]
) -> None:
    response = await client.get(TASKS_URL, params=params, headers=auth_headers())

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_list_accepts_the_maximum_limit(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    response = await client.get(TASKS_URL, params={"limit": 100}, headers=auth_headers())

    assert response.status_code == 200
    assert response.json() == {"items": [], "next_cursor": None}
