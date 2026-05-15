from __future__ import annotations

from pytest_bdd import scenario, then, when

from api import TinkApi


@scenario("api/root.feature", "Read the root endpoint")
def test_read_root_endpoint() -> None:
    pass


@when("I request the root endpoint")
def request_root_endpoint(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get_root()
    tink_api.assert_status(response, 200)
    scenario_state["root"] = tink_api.json(response)


@then("the root response says hello world")
def root_response_says_hello_world(scenario_state: dict) -> None:
    assert scenario_state["root"] == {"message": "Hello World"}
