from __future__ import annotations

from pathlib import Path

import pytest
from pytest_bdd import given, scenario, then, when

from appium_client import MerriamPage
from mock_server import MerriamMockServer


pytestmark = [pytest.mark.android, pytest.mark.mock]


@pytest.mark.smoke
@scenario("android/merriam_mock.feature", "Capture M-W Builder progress visual baseline")
def test_capture_merriam_progress_visual_baseline() -> None:
    pass


@scenario("android/merriam_mock.feature", "Complete the next M-W root through Android")
def test_complete_next_merriam_root_through_android() -> None:
    pass


@given("the Merriam mock API uses the progress fixture")
def mock_uses_progress(merriam_mock_server: MerriamMockServer) -> None:
    merriam_mock_server.reset(Path("fixtures/android/merriam/progress.json"))


@when("I open the Android M-W Builder screen")
def open_android_merriam_screen(merriam_page: MerriamPage) -> None:
    merriam_page.open_merriam_from_drawer()


@when("I complete Merriam root 11 from Android")
def complete_merriam_root_11(merriam_page: MerriamPage) -> None:
    merriam_page.complete_root(11)


@then("the Android M-W Builder screen shows the mocked latest root")
def android_merriam_shows_mocked_latest(merriam_page: MerriamPage) -> None:
    merriam_page.assert_summary_latest(10)


@then("the Android M-W Builder content is visible")
def android_merriam_content_is_visible(merriam_page: MerriamPage) -> None:
    merriam_page.assert_builder_content_visible()


@then("the Merriam mock API receives root 11")
def merriam_mock_api_receives_root_11(merriam_mock_server: MerriamMockServer) -> None:
    assert any(row.get("root_id") == 11 for row in merriam_mock_server.posted_records)
