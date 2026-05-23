from __future__ import annotations

import pytest
from pytest_bdd import given, scenario, then, when

from api import TinkApi
from appium_client import MerriamPage


pytestmark = [pytest.mark.android, pytest.mark.e2e]


@pytest.mark.smoke
@scenario("android/merriam_e2e.feature", "View M-W Builder progress from dev API")
def test_view_merriam_progress_from_dev_api() -> None:
    pass


@given("the Tink dev API is reachable")
def dev_api_is_reachable(tink_api: TinkApi) -> None:
    tink_api.check_dev_weight_available()


@given("the dev API has Merriam statistics")
def dev_api_has_merriam_statistics(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get("/merriam/stat")
    tink_api.assert_status(response, 200)
    payload = tink_api.json(response)
    assert isinstance(payload["latest"], int)
    assert isinstance(payload["week_stats"], list)
    assert len(payload["week_stats"]) == 7
    scenario_state["merriam_latest"] = payload["latest"]


@when("I open the Android M-W Builder screen")
def open_android_merriam_screen(merriam_page: MerriamPage) -> None:
    merriam_page.open_merriam_from_drawer()


@then("the Android M-W Builder screen shows the dev API latest root")
def android_merriam_shows_dev_api_latest(merriam_page: MerriamPage, scenario_state: dict) -> None:
    merriam_page.assert_progress_position_for_latest(scenario_state["merriam_latest"])


@then("the Android M-W Builder content is visible")
def android_merriam_content_is_visible(merriam_page: MerriamPage) -> None:
    merriam_page.assert_builder_content_visible()
