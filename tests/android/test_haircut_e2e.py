from __future__ import annotations

from datetime import date

import pytest
from pytest_bdd import given, scenario, then, when

from api import TinkApi
from appium_client import HaircutPage


pytestmark = [pytest.mark.android, pytest.mark.e2e]


@pytest.mark.smoke
@scenario("android/haircut_e2e.feature", "Add a haircut record through Android")
def test_add_haircut_record_through_android() -> None:
    pass


@given("the Tink dev API is reachable")
def dev_api_is_reachable(tink_api: TinkApi) -> None:
    tink_api.check_dev_weight_available()


@when("I open the Android haircut screen")
def open_android_haircut_screen(haircut_page: HaircutPage) -> None:
    haircut_page.open_haircut_from_drawer()


@when("I add a unique Android haircut record")
def add_unique_android_haircut_record(
    haircut_page: HaircutPage,
    scenario_state: dict,
    unique_suffix: str,
) -> None:
    shop_name = f"Android Cuts {unique_suffix[-8:]}"
    price = 77
    haircut_page.add_haircut(shop_name, price)
    scenario_state["android_created_haircut"] = {
        "shop_name": shop_name,
        "price": price,
        "created_at": date.today().isoformat(),
    }


@then("the haircut API contains the Android-created haircut record")
def haircut_api_contains_android_created_record(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_haircuts: list[int],
) -> None:
    expected = scenario_state["android_created_haircut"]
    response = tink_api.get("/haircut")
    tink_api.assert_status(response, 200)
    matching = [
        row for row in tink_api.json(response)
        if row.get("shop_name") == expected["shop_name"] and int(row.get("price")) == expected["price"]
    ]
    assert matching, f"Expected API haircut {expected}"
    cleanup_haircuts.append(matching[0]["id"])
    scenario_state["android_created_haircut"]["id"] = matching[0]["id"]


@then("the Android haircut screen shows the Android-created haircut record")
def android_haircut_screen_shows_android_created_record(
    haircut_page: HaircutPage,
    scenario_state: dict,
) -> None:
    haircut = scenario_state["android_created_haircut"]
    haircut_page.assert_history_contains(
        haircut["shop_name"],
        int(haircut["price"]),
        haircut["created_at"],
    )
