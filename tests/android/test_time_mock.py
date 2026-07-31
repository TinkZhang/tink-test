from __future__ import annotations

from pathlib import Path

import pytest
from pytest_bdd import given, scenario, then, when

from appium_client import TimePage
from mock_server import TimeMockServer


pytestmark = [pytest.mark.android, pytest.mark.mock]


@pytest.mark.smoke
@scenario("android/time_mock.feature", "Capture empty time dashboard visual baseline")
def test_capture_empty_time_dashboard_visual_baseline() -> None:
    pass


@scenario("android/time_mock.feature", "Capture mixed time dashboard visual baseline")
def test_capture_mixed_time_dashboard_visual_baseline() -> None:
    pass


@given("the time mock API uses the empty time fixture")
def mock_uses_empty_time(time_mock_server: TimeMockServer) -> None:
    time_mock_server.reset(Path("fixtures/android/time/empty.json"))


@given("the time mock API uses the mixed time fixture")
def mock_uses_mixed_time(time_mock_server: TimeMockServer) -> None:
    time_mock_server.reset(Path("fixtures/android/time/mixed.json"))


@when("I open the Android time screen")
def open_android_time_screen(time_page: TimePage) -> None:
    time_page.open_time_from_drawer()


@then("the Android time dashboard is empty")
def android_time_dashboard_is_empty(time_page: TimePage) -> None:
    time_page.assert_empty_dashboard()


@then("the Android time dashboard shows multiple mocked time entries")
def android_time_dashboard_shows_multiple_mocked_time_entries(time_page: TimePage) -> None:
    time_page.assert_entries_visible(
        [
            "Planning: Roadmap",
            "Coding: Android Appium",
            "Reading: Material 3",
        ]
    )


@then("the Android time statistics show multiple mocked types")
def android_time_statistics_show_multiple_mocked_types(time_page: TimePage) -> None:
    time_page.assert_type_duration_visible("Working", "1h 30m")
    time_page.assert_type_duration_visible("Deep Thinking, Coding", "1h 0m")
    time_page.assert_type_duration_visible("Reading, Study", "45m")
