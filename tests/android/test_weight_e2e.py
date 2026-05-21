from __future__ import annotations

import math

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from api import TinkApi
from appium_client import WeightPage


pytestmark = [pytest.mark.android, pytest.mark.e2e]


@pytest.mark.smoke
@scenario("android/weight_e2e.feature", "View an API-created weight in Android history")
def test_view_api_created_weight_in_android_history() -> None:
    pass


@scenario("android/weight_e2e.feature", "Add and delete a weight through Android without changing dev state")
def test_add_and_delete_weight_through_android_without_changing_dev_state() -> None:
    pass


@given("the Tink dev API is reachable")
def dev_api_is_reachable(tink_api: TinkApi) -> None:
    tink_api.check_dev_weight_available()


@given("the API has a unique weight record for Android")
def api_has_unique_weight(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_weights: list[int],
    generated_weight: float,
) -> None:
    response = tink_api.create_weight(generated_weight)
    tink_api.assert_status(response, 200, 201)
    payload = tink_api.json(response)
    cleanup_weights.append(payload["id"])
    scenario_state["api_created_weight"] = payload
    scenario_state["expected_display_weight"] = round(float(payload["weight"]), 1)


@given("the API has a seed weight record for Android")
def api_has_seed_weight(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_weights: list[int],
    generated_weight: float,
) -> None:
    response = tink_api.create_weight(generated_weight)
    tink_api.assert_status(response, 200, 201)
    payload = tink_api.json(response)
    cleanup_weights.append(payload["id"])
    scenario_state["seed_weight"] = payload


@given(parsers.parse("the API has a temporary baseline weight {weight:g} for Android"))
def api_has_temporary_baseline_weight(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_weights: list[int],
    weight: float,
) -> None:
    existing_response = tink_api.get_weights()
    tink_api.assert_status(existing_response, 200)
    scenario_state["known_weight_ids"] = {
        row["id"] for row in tink_api.json(existing_response)
    }

    response = tink_api.create_weight(weight)
    tink_api.assert_status(response, 200, 201)
    payload = tink_api.json(response)
    cleanup_weights.append(payload["id"])
    scenario_state["baseline_weight"] = round(float(payload["weight"]), 1)
    scenario_state["baseline_weight_id"] = payload["id"]
    scenario_state["known_weight_ids"].add(payload["id"])


@when("I open the Android weight screen")
def open_android_weight_screen(weight_page: WeightPage) -> None:
    weight_page.open_weight_from_drawer()


@when("I open the Android weight history")
def open_android_weight_history(weight_page: WeightPage) -> None:
    weight_page.open_history()


@when("I add a weight record through Android")
def add_weight_through_android(weight_page: WeightPage, scenario_state: dict) -> None:
    scenario_state["android_created_weight"] = weight_page.add_weight_by_drag()


@when(parsers.parse("I adjust Android weight to {weight:g} and add it"))
def adjust_android_weight_to_target_and_add(
    weight_page: WeightPage,
    scenario_state: dict,
    weight: float,
) -> None:
    weight_page.adjust_weight_to(weight)
    scenario_state["android_created_weight"] = weight_page.add_current_weight()


@when("I delete the Android-created weight from history")
def delete_android_created_weight_from_history(weight_page: WeightPage, scenario_state: dict) -> None:
    weight_page.delete_weight(scenario_state["android_created_weight_id"])
    weight_page.assert_history_does_not_contain_weight_id(scenario_state["android_created_weight_id"])


@when("I return to the Android weight screen")
def return_to_android_weight_screen(weight_page: WeightPage) -> None:
    weight_page.go_back()
    weight_page.wait_for_text("体重趋势")


@then("the Android weight history shows the API-created weight")
def history_shows_api_created_weight(weight_page: WeightPage, scenario_state: dict) -> None:
    weight_page.assert_history_contains_weight(scenario_state["expected_display_weight"])


@then(parsers.parse("the Android current weight is {weight:g}"))
def android_current_weight_is(weight_page: WeightPage, weight: float) -> None:
    weight_page.assert_current_weight_is(weight)


@then("Android shows the weight as recorded today")
def android_shows_weight_recorded_today(weight_page: WeightPage) -> None:
    weight_page.assert_status_shows_today_recorded()


@then("the API includes the Android-created weight")
def api_includes_android_created_weight(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_weights: list[int],
) -> None:
    expected = scenario_state["android_created_weight"]
    response = tink_api.get_weights()
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    known_weight_ids = scenario_state.get("known_weight_ids", set())
    match = next(
        (
            row
            for row in rows
            if row["id"] not in known_weight_ids
            and math.isclose(float(row["weight"]), expected, abs_tol=0.05)
        ),
        None,
    )
    assert match is not None, f"Expected API weight {expected}; rows were {rows}"
    cleanup_weights.append(match["id"])
    scenario_state["android_created_api_row"] = match
    scenario_state["android_created_weight_id"] = match["id"]


@then("the Android weight history shows the Android-created weight")
def history_shows_android_created_weight(weight_page: WeightPage, scenario_state: dict) -> None:
    weight_page.assert_history_contains_weight(scenario_state["android_created_weight"])


@then(parsers.parse("the Android current weight returns to {weight:g}"))
def android_current_weight_returns_to(weight_page: WeightPage, weight: float) -> None:
    weight_page.assert_current_weight_is(weight)
