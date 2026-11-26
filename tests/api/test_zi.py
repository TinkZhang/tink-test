from __future__ import annotations

from uuid import uuid4

from pytest_bdd import given, scenario, then, when

from api import TinkApi


@scenario("api/zi.feature", "Upsert and read zi records")
def test_upsert_and_read_zi_records() -> None:
    pass


@given("the Tink dev API is reachable")
def dev_api_is_reachable(tink_api: TinkApi) -> None:
    tink_api.check_dev_weight_available()


@when("I upsert zi records")
def upsert_zi_records(tink_api: TinkApi, scenario_state: dict) -> None:
    base = uuid4().int % 60000
    chars = "".join(chr(0xF0000 + ((base + offset) % 60000)) for offset in range(2))
    payload = {"zis": chars, "proficiency": 4}
    response = tink_api.put("/zi/", payload)
    tink_api.assert_status(response, 200)
    scenario_state["zi_chars"] = chars
    scenario_state["zi_response"] = tink_api.json(response)


@then("the zi response contains the upserted characters")
def zi_response_contains_upserted_characters(scenario_state: dict) -> None:
    chars = set(scenario_state["zi_chars"])
    rows = scenario_state["zi_response"]
    assert {row["zi"] for row in rows} == chars
    assert all(row["proficiency"] == 4 for row in rows)


@then("the zi list includes the upserted characters")
def zi_list_includes_upserted_characters(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get("/zi/", {"proficiency": 4, "size": 50})
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    listed = {row["zi"] for row in rows}
    assert set(scenario_state["zi_chars"]).issubset(listed)


@scenario("api/zi.feature", "Written characters can be listed and invalid input is rejected")
def test_list_written_zi_and_reject_invalid_record() -> None:
    pass


@when("I list the written zi records")
def list_written_zi(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get("/zi/written")
    tink_api.assert_status(response, 200)
    scenario_state["written_zis"] = tink_api.json(response)


@then("the written zi list contains distinct single characters")
def written_zi_list_has_distinct_characters(scenario_state: dict) -> None:
    rows = scenario_state["written_zis"]
    assert isinstance(rows, list)
    assert all(isinstance(char, str) and len(char) == 1 for char in rows)
    assert rows == sorted(set(rows))


@then("an invalid written zi record is rejected")
def invalid_written_zi_is_rejected(tink_api: TinkApi) -> None:
    tink_api.assert_status(tink_api.put("/zi/written", {"zi": "AB"}), 422)
