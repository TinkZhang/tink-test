from __future__ import annotations

from pytest_bdd import given, scenario, then, when

from api import TinkApi


@scenario("api/story.feature", "Create, list, read, and delete a story")
def test_create_list_read_and_delete_story() -> None:
    pass


@given("the Tink dev API is reachable")
def dev_api_is_reachable(tink_api: TinkApi) -> None:
    tink_api.check_dev_weight_available()


@when("I create a story")
def create_story(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_stories: list[str],
    unique_suffix: str,
) -> None:
    payload = {
        "title": f"E2E Story {unique_suffix[-8:]}",
        "content": f"This is an E2E story created at {unique_suffix}.",
    }
    response = tink_api.post("/story/", payload)
    tink_api.assert_status(response, 200, 201)
    created = tink_api.json(response)
    scenario_state["created_story"] = created
    scenario_state["expected_story"] = payload

    story_id = created.get("id")
    if isinstance(story_id, str):
        cleanup_stories.append(story_id)


@then("the story create response contains the created story")
def story_response_contains_created_story(scenario_state: dict) -> None:
    created = scenario_state["created_story"]
    expected = scenario_state["expected_story"]
    assert isinstance(created.get("id"), str)
    assert created["title"] == expected["title"]
    assert created["content"] == expected["content"]
    assert created["length"] == len(expected["content"])


@then("the story list includes the created story")
def story_list_includes_created_story(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get("/story/story_list", {"page": 0, "size": 50})
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    created = scenario_state["created_story"]
    assert any(row.get("id") == created["id"] for row in rows)


@then("I can read the created story")
def can_read_created_story(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_story"]
    response = tink_api.get(f"/story/{created['id']}")
    tink_api.assert_status(response, 200)
    loaded = tink_api.json(response)
    assert loaded["id"] == created["id"]
    assert loaded["content"] == scenario_state["expected_story"]["content"]


@when("I delete the created story")
def delete_created_story(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_stories: list[str],
) -> None:
    created = scenario_state["created_story"]
    response = tink_api.delete(f"/story/{created['id']}")
    tink_api.assert_status(response, 204)
    if created["id"] in cleanup_stories:
        cleanup_stories.remove(created["id"])


@then("reading the deleted story returns not found")
def reading_deleted_story_returns_not_found(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_story"]
    response = tink_api.get(f"/story/{created['id']}")
    tink_api.assert_status(response, 404)
