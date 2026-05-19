from __future__ import annotations

import math

import pytest
from pytest_bdd import given, scenario, then, when

from api import TinkApi
from appium_client import WeightPage


pytestmark = [pytest.mark.android, pytest.mark.e2e]


@pytest.mark.smoke
@scenario("android/weight_e2e.feature", "View an API-created weight in Android history")
def test_view_api_created_weight_in_android_history() -> None:
    pass


@scenario("android/weight_e2e.feature", "Add a weight through Android and verify it through the API")
def test_add_weight_through_android_and_verify_api() -> None:
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


@when("I open the Android weight screen")
def open_android_weight_screen(weight_page: WeightPage) -> None:
    weight_page.open_weight_from_drawer()


@when("I open the Android weight history")
def open_android_weight_history(weight_page: WeightPage) -> None:
    weight_page.open_history()


@when("I add a weight record through Android")
def add_weight_through_android(weight_page: WeightPage, scenario_state: dict) -> None:
    scenario_state["android_created_weight"] = weight_page.add_weight_by_drag()


@then("the Android weight history shows the API-created weight")
def history_shows_api_created_weight(weight_page: WeightPage, scenario_state: dict) -> None:
    weight_page.assert_history_contains_weight(scenario_state["expected_display_weight"])


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
    match = next((row for row in rows if math.isclose(float(row["weight"]), expected, abs_tol=0.05)), None)
    assert match is not None, f"Expected API weight {expected}; rows were {rows}"
    cleanup_weights.append(match["id"])
    scenario_state["android_created_api_row"] = match


@then("the Android weight history shows the Android-created weight")
def history_shows_android_created_weight(weight_page: WeightPage, scenario_state: dict) -> None:
    weight_page.assert_history_contains_weight(scenario_state["android_created_weight"])
