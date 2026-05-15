from __future__ import annotations

from pytest_bdd import given, scenario, then, when

from api import TinkApi


@scenario("api/merriam.feature", "Read Merriam statistics")
def test_read_merriam_statistics() -> None:
    pass


@given("the Tink dev API is reachable")
def dev_api_is_reachable(tink_api: TinkApi) -> None:
    tink_api.check_dev_weight_available()


@when("I request Merriam statistics")
def request_merriam_statistics(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get("/merriam/stat")
    tink_api.assert_status(response, 200)
    scenario_state["merriam_statistics"] = tink_api.json(response)


@then("the Merriam statistics response has week stats")
def merriam_statistics_response_has_week_stats(scenario_state: dict) -> None:
    payload = scenario_state["merriam_statistics"]
    assert isinstance(payload["week_stats"], list)
    assert len(payload["week_stats"]) == 7
    assert "latest" in payload
