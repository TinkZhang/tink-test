from __future__ import annotations

from datetime import date

from pytest_bdd import given, scenario, then, when

from api import TinkApi


@scenario("api/haircut.feature", "Create, list, and delete a haircut record")
def test_create_list_and_delete_haircut_record() -> None:
    pass


@given("the Tink dev API is reachable")
def dev_api_is_reachable(tink_api: TinkApi) -> None:
    tink_api.check_dev_weight_available()


@when("I create a haircut record")
def create_haircut_record(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_haircuts: list[int],
    unique_suffix: str,
) -> None:
    payload = {
        "shop_name": f"E2E Haircut {unique_suffix}",
        "price": 88,
        "created_at": date.today().isoformat(),
    }
    response = tink_api.post("/haircut", payload)
    tink_api.assert_status(response, 200, 201)
    created = tink_api.json(response)
    scenario_state["created_haircut"] = created
    scenario_state["expected_haircut"] = payload

    haircut_id = created.get("id")
    if isinstance(haircut_id, int):
        cleanup_haircuts.append(haircut_id)


@then("the haircut create response contains the created haircut")
def haircut_response_contains_created_haircut(scenario_state: dict) -> None:
    created = scenario_state["created_haircut"]
    expected = scenario_state["expected_haircut"]
    assert isinstance(created.get("id"), int)
    assert created["shop_name"] == expected["shop_name"]
    assert created["price"] == expected["price"]
    assert created["created_at"] == expected["created_at"]


@then("the haircut list includes the created haircut")
def haircut_list_includes_created_haircut(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get("/haircut")
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    created = scenario_state["created_haircut"]
    assert any(row.get("id") == created["id"] for row in rows)


@when("I delete the created haircut record")
def delete_created_haircut(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_haircuts: list[int],
) -> None:
    created = scenario_state["created_haircut"]
    response = tink_api.delete(f"/haircut/{created['id']}")
    tink_api.assert_status(response, 204)
    if created["id"] in cleanup_haircuts:
        cleanup_haircuts.remove(created["id"])


@then("the haircut list does not include the created haircut")
def haircut_list_excludes_created_haircut(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get("/haircut")
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    created = scenario_state["created_haircut"]
    assert all(row.get("id") != created["id"] for row in rows)
