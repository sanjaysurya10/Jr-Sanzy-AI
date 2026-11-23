from typing import Any

from httpx import AsyncClient

from tests.conftest import AuthHeaders

DASHBOARD_URL = "/api/v1/dashboard"
TASKS_URL = "/api/v1/tasks"
PRIORITIES = ("critical", "high", "normal", "low")


async def create_task(
    client: AsyncClient, headers: dict[str, str], **fields: Any
) -> dict[str, Any]:
    response = await client.post(TASKS_URL, json={"title": "Task", **fields}, headers=headers)
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


async def test_empty_dashboard_has_all_four_priorities_and_a_greeting(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    response = await client.get(DASHBOARD_URL, headers=auth_headers())

    assert response.status_code == 200
    body = response.json()
    assert body["greeting"]["period"] in {"morning", "afternoon", "evening"}
    assert body["greeting"]["text"] == f"Good {body['greeting']['period']}."
    assert set(body["tasks_by_priority"]) == set(PRIORITIES)
    for priority in PRIORITIES:
        assert body["tasks_by_priority"][priority] == {"items": [], "total": 0}
    assert body["activity"] == []


async def test_dashboard_groups_open_tasks_by_priority(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    await create_task(client, headers, title="urgent", priority="critical")
    await create_task(client, headers, title="soon", priority="high")
    await create_task(client, headers, title="later", priority="high")

    groups = (await client.get(DASHBOARD_URL, headers=headers)).json()["tasks_by_priority"]

    assert [task["title"] for task in groups["critical"]["items"]] == ["urgent"]
    assert [task["title"] for task in groups["high"]["items"]] == ["soon", "later"]
    assert groups["high"]["total"] == 2
    assert groups["normal"] == {"items": [], "total": 0}
    assert groups["low"] == {"items": [], "total": 0}


async def test_dashboard_shows_five_tasks_per_priority_and_the_full_total(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    for number in range(7):
        await create_task(client, headers, title=f"normal {number}")

    normal_group = (await client.get(DASHBOARD_URL, headers=headers)).json()["tasks_by_priority"][
        "normal"
    ]

    assert [task["title"] for task in normal_group["items"]] == [
        f"normal {number}" for number in range(5)
    ]
    assert normal_group["total"] == 7


async def test_dashboard_orders_a_column_by_due_date_with_undated_last(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    await create_task(client, headers, title="undated")
    await create_task(client, headers, title="later", due_at="2030-06-01T00:00:00Z")
    await create_task(client, headers, title="sooner", due_at="2030-02-01T00:00:00Z")

    normal_group = (await client.get(DASHBOARD_URL, headers=headers)).json()["tasks_by_priority"][
        "normal"
    ]

    assert [task["title"] for task in normal_group["items"]] == ["sooner", "later", "undated"]


async def test_dashboard_leaves_out_done_and_archived_tasks(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    await create_task(client, headers, title="open")
    done = await create_task(client, headers, title="done")
    archived = await create_task(client, headers, title="archived")
    await client.patch(f"{TASKS_URL}/{done['id']}", json={"status": "done"}, headers=headers)
    await client.patch(
        f"{TASKS_URL}/{archived['id']}", json={"status": "archived"}, headers=headers
    )

    normal_group = (await client.get(DASHBOARD_URL, headers=headers)).json()["tasks_by_priority"][
        "normal"
    ]

    assert [task["title"] for task in normal_group["items"]] == ["open"]
    assert normal_group["total"] == 1


async def test_dashboard_shows_the_ten_latest_activity_entries_newest_first(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    headers = auth_headers()
    for number in range(12):
        await create_task(client, headers, title=f"task {number}")

    activity = (await client.get(DASHBOARD_URL, headers=headers)).json()["activity"]

    assert len(activity) == 10
    assert [entry["details"]["title"] for entry in activity] == [
        f"task {number}" for number in range(11, 1, -1)
    ]
    assert activity[0]["actor"] == "user"
    assert activity[0]["action"] == "task.created"
    assert activity[0]["entity_type"] == "task"


async def test_dashboard_never_shows_another_users_data(
    client: AsyncClient, auth_headers: AuthHeaders
) -> None:
    await create_task(client, auth_headers(subject="other"), title="theirs", priority="critical")

    body = (await client.get(DASHBOARD_URL, headers=auth_headers(subject="me"))).json()

    assert all(body["tasks_by_priority"][priority]["total"] == 0 for priority in PRIORITIES)
    assert body["activity"] == []
