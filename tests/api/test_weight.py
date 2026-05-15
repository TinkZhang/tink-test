from __future__ import annotations

from pytest_bdd import given, scenario, then, when

from api import TinkApi


@scenario("api/weight.feature", "Create, list, and delete a weight record")
def test_create_list_and_delete_weight_record() -> None:
    pass


@given("the Tink dev API is reachable")
def dev_api_is_reachable(tink_api: TinkApi) -> None:
    tink_api.check_dev_weight_available()


@when("I create a weight record")
def create_weight_record(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_weights: list[int],
    generated_weight: float,
) -> None:
    response = tink_api.create_weight(generated_weight)
    tink_api.assert_status(response, 200, 201)
    payload = tink_api.json(response)

    scenario_state["created_weight"] = payload
    scenario_state["expected_weight"] = generated_weight

    weight_id = payload.get("id")
    if isinstance(weight_id, int):
        cleanup_weights.append(weight_id)


@then("the weight create response contains the created weight")
def create_response_contains_weight(scenario_state: dict) -> None:
    payload = scenario_state["created_weight"]
    expected_weight = scenario_state["expected_weight"]

    assert isinstance(payload.get("id"), int)
    assert payload.get("created_at")
    assert payload.get("weight") == expected_weight


@then("the weight list includes the created weight")
def list_includes_created_weight(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get_weights()
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)

    created = scenario_state["created_weight"]
    assert any(row.get("id") == created["id"] for row in rows)


@when("I delete the created weight record")
def delete_created_weight(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_weights: list[int],
) -> None:
    created = scenario_state["created_weight"]
    response = tink_api.delete_weight(created["id"])
    tink_api.assert_status(response, 204)

    if created["id"] in cleanup_weights:
        cleanup_weights.remove(created["id"])


@then("the weight list does not include the created weight")
def list_does_not_include_created_weight(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get_weights()
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)

    created = scenario_state["created_weight"]
    assert all(row.get("id") != created["id"] for row in rows)
