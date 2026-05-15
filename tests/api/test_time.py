from __future__ import annotations

from pytest_bdd import given, scenario, then, when

from api import TinkApi


@scenario("api/time.feature", "Create, update, list, summarize, and delete a time entry")
def test_create_update_list_summarize_and_delete_time_entry() -> None:
    pass


@given("the Tink dev API is reachable")
def dev_api_is_reachable(tink_api: TinkApi) -> None:
    tink_api.check_dev_weight_available()


@when("I create a time entry")
def create_time_entry(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_times: list[int],
    future_time_window: tuple[str, str],
    unique_suffix: str,
) -> None:
    start, end = future_time_window
    payload = {
        "type": 4,
        "start": start,
        "end": end,
        "title": f"E2E Time {unique_suffix[-8:]}",
        "description": "Created by tink-test",
    }
    response = tink_api.post("/time/", payload)
    tink_api.assert_status(response, 200, 201)
    created = tink_api.json(response)
    scenario_state["created_time"] = created
    scenario_state["expected_time"] = payload

    time_id = created.get("id")
    if isinstance(time_id, int):
        cleanup_times.append(time_id)


@then("the time create response contains the created time entry")
def time_response_contains_created_entry(scenario_state: dict) -> None:
    created = scenario_state["created_time"]
    expected = scenario_state["expected_time"]
    assert isinstance(created.get("id"), int)
    assert created["type"] == expected["type"]
    assert created["title"] == expected["title"]
    assert created["duration"] == 30
    assert created.get("google_calendar_event_id")


@then("the time list includes the created time entry")
def time_list_includes_created_entry(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_time"]
    response = tink_api.get(
        "/time/",
        {
            "from": scenario_state["expected_time"]["start"],
            "to": scenario_state["expected_time"]["end"],
        },
    )
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    assert any(row.get("id") == created["id"] for row in rows)


@when("I update the created time entry")
def update_created_time_entry(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_time"]
    payload = {"title": "Updated E2E Time", "description": "Updated by tink-test"}
    response = tink_api.patch(f"/time/{created['id']}", payload)
    tink_api.assert_status(response, 200)
    scenario_state["updated_time"] = tink_api.json(response)


@then("the time list shows the updated time entry")
def time_list_shows_updated_entry(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_time"]
    response = tink_api.get(
        "/time/",
        {
            "from": scenario_state["expected_time"]["start"],
            "to": scenario_state["expected_time"]["end"],
        },
    )
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    matching = [row for row in rows if row.get("id") == created["id"]]
    assert matching
    assert matching[0]["title"] == "Updated E2E Time"


@then("the time statistics endpoint returns type durations")
def time_statistics_returns_type_durations(tink_api: TinkApi, scenario_state: dict) -> None:
    start_date = scenario_state["expected_time"]["start"][:10]
    response = tink_api.get("/time/statistics", {"start_date": start_date, "end_date": start_date})
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    assert isinstance(rows, list)
    assert any(row.get("type") == 4 for row in rows)


@when("I delete the created time entry")
def delete_created_time_entry(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_times: list[int],
) -> None:
    created = scenario_state["created_time"]
    response = tink_api.delete(f"/time/{created['id']}")
    tink_api.assert_status(response, 204)
    if created["id"] in cleanup_times:
        cleanup_times.remove(created["id"])


@then("the time list does not include the created time entry")
def time_list_does_not_include_created_entry(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_time"]
    response = tink_api.get(
        "/time/",
        {
            "from": scenario_state["expected_time"]["start"],
            "to": scenario_state["expected_time"]["end"],
        },
    )
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    assert all(row.get("id") != created["id"] for row in rows)
