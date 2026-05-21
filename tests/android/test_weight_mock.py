from __future__ import annotations

from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from appium_client import WeightPage
from mock_server import WeightMockServer


pytestmark = [pytest.mark.android, pytest.mark.mock]


@pytest.mark.smoke
@scenario("android/weight_mock.feature", "Capture empty weight control visual baseline")
def test_capture_empty_weight_control_visual_baseline() -> None:
    pass


@scenario("android/weight_mock.feature", "Capture latest weight control visual baseline")
def test_capture_latest_weight_control_visual_baseline() -> None:
    pass


@scenario("android/weight_mock.feature", "Capture empty weight trend visual baseline")
def test_capture_empty_weight_trend_visual_baseline() -> None:
    pass


@scenario("android/weight_mock.feature", "Capture populated weight trend visual baseline")
def test_capture_populated_weight_trend_visual_baseline() -> None:
    pass


@scenario("android/weight_mock.feature", "Capture empty weight history visual baseline")
def test_capture_empty_weight_history_visual_baseline() -> None:
    pass


@scenario("android/weight_mock.feature", "Capture populated weight history visual baseline")
def test_capture_populated_weight_history_visual_baseline() -> None:
    pass


@scenario("android/weight_mock.feature", "Delete a mocked weight record from Android history")
def test_delete_mocked_weight_record_from_android_history() -> None:
    pass


@scenario("android/weight_mock.feature", "Show an API failure from the mock server")
def test_show_api_failure_from_mock_server() -> None:
    pass


@given("the weight mock API uses the empty history fixture")
def mock_uses_empty_history(weight_mock_server: WeightMockServer) -> None:
    weight_mock_server.reset(Path("fixtures/android/weight/empty.json"))


@given("the weight mock API uses the populated history fixture")
def mock_uses_populated_history(weight_mock_server: WeightMockServer) -> None:
    weight_mock_server.reset(Path("fixtures/android/weight/history.json"))


@given("the weight mock API uses the latest weight fixture")
def mock_uses_latest_weight(weight_mock_server: WeightMockServer) -> None:
    weight_mock_server.reset(Path("fixtures/android/weight/latest.json"))


@given("the weight mock API uses the fixed trend fixture")
def mock_uses_fixed_trend(weight_mock_server: WeightMockServer) -> None:
    weight_mock_server.reset(Path("fixtures/android/weight/trend.json"))


@given("the weight mock API returns an error")
def mock_returns_error(weight_mock_server: WeightMockServer) -> None:
    weight_mock_server.force_error = True


@when("I open the Android weight screen")
def open_android_weight_screen(weight_page: WeightPage) -> None:
    weight_page.open_weight_from_drawer()


@when("I open the Android weight history")
def open_android_weight_history(weight_page: WeightPage) -> None:
    weight_page.open_history()


@when(parsers.parse("I delete mocked weight id {weight_id:d} from Android"))
def delete_mocked_weight(weight_page: WeightPage, weight_id: int) -> None:
    weight_page.delete_weight(weight_id)


@then("the Android weight history is empty")
def android_weight_history_is_empty(weight_page: WeightPage) -> None:
    weight_page.assert_history_empty()


@then("the Android weight control shows no current weight visual baseline")
def android_weight_control_shows_no_current_weight(weight_page: WeightPage) -> None:
    weight_page.assert_current_weight_blank()


@then(parsers.parse("the Android weight control shows latest weight {weight:g} on {date} visual baseline"))
def android_weight_control_shows_latest_weight(
    weight_page: WeightPage,
    weight: float,
    date: str,
) -> None:
    weight_page.assert_current_weight_is(weight)
    weight_page.assert_status_shows_last_date(date)


@when("I select the Android month weight trend")
def select_android_month_weight_trend(weight_page: WeightPage) -> None:
    weight_page.select_month_trend()


@when("I select the Android all-time weight trend")
def select_android_all_time_weight_trend(weight_page: WeightPage) -> None:
    weight_page.select_all_trend()


@then("the Android month trend is empty visual baseline")
def android_month_trend_is_empty(weight_page: WeightPage) -> None:
    weight_page.select_month_trend()
    weight_page.assert_trend_empty()


@then("the Android all-time trend is empty visual baseline")
def android_all_time_trend_is_empty(weight_page: WeightPage) -> None:
    weight_page.assert_trend_empty()


@then("the Android month trend has data visual baseline")
def android_month_trend_has_data(weight_page: WeightPage) -> None:
    weight_page.select_month_trend()
    weight_page.assert_trend_has_data()


@then("the Android all-time trend has data visual baseline")
def android_all_time_trend_has_data(weight_page: WeightPage) -> None:
    weight_page.assert_trend_has_data()


@then(parsers.parse("the Android weight history shows mocked weight {weight:g}"))
def android_weight_history_shows_mocked_weight(weight_page: WeightPage, weight: float) -> None:
    weight_page.assert_history_contains_weight(weight)


@then(parsers.parse("the Android weight history no longer shows mocked weight {weight:g}"))
def android_weight_history_no_longer_shows_mocked_weight(
    weight_page: WeightPage,
    weight: float,
) -> None:
    weight_page.assert_history_does_not_contain_weight(weight)


@then("Android shows the API failure message")
def android_shows_api_failure_message(weight_page: WeightPage) -> None:
    weight_page.assert_api_failure_visible()
