from __future__ import annotations

from pathlib import Path

import pytest
from pytest_bdd import given, scenario, then, when

from appium_client import HaircutPage
from mock_server import HaircutMockServer


pytestmark = [pytest.mark.android, pytest.mark.mock]


@pytest.mark.smoke
@scenario("android/haircut_mock.feature", "Capture empty haircut history visual baseline")
def test_capture_empty_haircut_history_visual_baseline() -> None:
    pass


@scenario("android/haircut_mock.feature", "Capture haircut history visual baseline")
def test_capture_haircut_history_visual_baseline() -> None:
    pass


@given("the haircut mock API uses the empty haircut fixture")
def mock_uses_empty_haircut(haircut_mock_server: HaircutMockServer) -> None:
    haircut_mock_server.reset(Path("fixtures/android/haircut/empty.json"))


@given("the haircut mock API uses the haircut history fixture")
def mock_uses_haircut_history(haircut_mock_server: HaircutMockServer) -> None:
    haircut_mock_server.reset(Path("fixtures/android/haircut/history.json"))


@when("I open the Android haircut screen")
def open_android_haircut_screen(haircut_page: HaircutPage) -> None:
    haircut_page.open_haircut_from_drawer()


@then("the Android haircut history is empty")
def android_haircut_history_is_empty(haircut_page: HaircutPage) -> None:
    haircut_page.assert_empty_history()
    haircut_page.assert_days_text_visible()


@then("the Android haircut screen shows multiple mocked haircut records")
def android_haircut_screen_shows_multiple_mocked_records(haircut_page: HaircutPage) -> None:
    haircut_page.assert_history_contains("Material Barber", 88, "2026-05-10")
    haircut_page.assert_history_contains_any(["Tink Hair Studio", "Weekend Cuts"])
