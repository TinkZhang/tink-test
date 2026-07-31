from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pytest_bdd import given, scenario, then, when

from api import TinkApi
from appium_client import TimePage


pytestmark = [pytest.mark.android, pytest.mark.e2e]


@pytest.mark.smoke
@scenario("android/time_e2e.feature", "View an API-created time entry on Android")
def test_view_api_created_time_entry_on_android() -> None:
    pass


@scenario("android/time_e2e.feature", "Add and delete a time label through Android")
def test_add_and_delete_time_label_through_android() -> None:
    pass


@given("the Tink dev API is reachable")
def dev_api_is_reachable(tink_api: TinkApi) -> None:
    tink_api.check_dev_weight_available()


@given("the API has a unique time entry for Android")
def api_has_unique_time_entry(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_times: list[int],
    unique_suffix: str,
) -> None:
    now = datetime.now(UTC).replace(microsecond=0)
    start = now + timedelta(minutes=5)
    end = start + timedelta(minutes=30)
    title = f"Appium Time {unique_suffix[-8:]}"
    payload = {
        "type": 5,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "title": title,
        "description": "Created by Android Appium E2E",
    }
    response = tink_api.post("/time/", payload)
    tink_api.assert_status(response, 200, 201)
    created = tink_api.json(response)
    cleanup_times.append(created["id"])
    scenario_state["api_created_time"] = created
    scenario_state["api_created_time_title"] = title


@when("I open the Android time screen")
def open_android_time_screen(time_page: TimePage) -> None:
    time_page.open_time_from_drawer()


@when("I add a unique Android time label")
def add_unique_android_time_label(
    time_page: TimePage,
    scenario_state: dict,
    unique_suffix: str,
) -> None:
    label_name = f"TINK-{unique_suffix[-6:]}"
    scenario_state["android_created_time_label"] = label_name
    time_page.add_label(label_name)


@when("I delete the Android-created time label")
def delete_android_created_time_label(time_page: TimePage, scenario_state: dict) -> None:
    time_page.delete_label(scenario_state["android_created_time_label"])


@then("the Android time screen shows the API-created time entry")
def android_time_screen_shows_api_created_entry(time_page: TimePage, scenario_state: dict) -> None:
    time_page.assert_entry_visible(scenario_state["api_created_time_title"])


@then("the Android time label manager shows the created label")
def android_time_label_manager_shows_created_label(
    time_page: TimePage,
    scenario_state: dict,
    tink_api: TinkApi,
    cleanup_time_labels: list[int],
) -> None:
    label_name = scenario_state["android_created_time_label"]
    time_page.wait_for_text(label_name)

    response = tink_api.get("/time/labels", {"type": 5})
    tink_api.assert_status(response, 200)
    matching = [row for row in tink_api.json(response) if row["name"] == label_name]
    assert matching, f"Expected API label {label_name}"
    cleanup_time_labels.append(matching[0]["id"])
    scenario_state["android_created_time_label_id"] = matching[0]["id"]


@then("the Android time label manager no longer shows the created label")
def android_time_label_manager_no_longer_shows_created_label(
    time_page: TimePage,
    scenario_state: dict,
    cleanup_time_labels: list[int],
) -> None:
    label_name = scenario_state["android_created_time_label"]
    assert label_name not in time_page.driver.page_source
    label_id = scenario_state.get("android_created_time_label_id")
    if label_id in cleanup_time_labels:
        cleanup_time_labels.remove(label_id)
