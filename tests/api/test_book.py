from __future__ import annotations

from datetime import date

from pytest_bdd import given, scenario, then, when

from api import TinkApi


@scenario("api/book.feature", "Create, update, move, archive, note, and delete a book")
def test_create_update_move_archive_note_and_delete_book() -> None:
    pass


@given("the Tink dev API is reachable")
def dev_api_is_reachable(tink_api: TinkApi) -> None:
    tink_api.check_dev_weight_available()


@when("I create a wishlist book")
def create_wishlist_book(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_books: list[int],
    unique_suffix: str,
) -> None:
    payload = {
        "title": f"E2E Book {unique_suffix[-8:]}",
        "author": "Tink E2E",
        "publisher": "Tink Test",
        "pages": 128,
        "publish_year": 2026,
    }
    response = tink_api.post("/book/wishlist", payload)
    tink_api.assert_status(response, 200, 201)
    created = tink_api.json(response)
    scenario_state["created_book"] = created
    scenario_state["expected_book"] = payload

    book_id = created.get("id")
    if isinstance(book_id, int):
        cleanup_books.append(book_id)


@then("the wishlist contains the created book")
def wishlist_contains_created_book(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get("/book/wishlist", {"page": 0, "size": 50})
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    created = scenario_state["created_book"]
    assert created["state"] == "wish"
    assert any(row.get("id") == created["id"] for row in rows)


@when("I update the created book")
def update_created_book(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_book"]
    payload = {"rating": 4.5, "description": "Updated by E2E"}
    response = tink_api.patch(f"/book/{created['id']}", payload)
    tink_api.assert_status(response, 200)
    scenario_state["updated_book"] = tink_api.json(response)


@then("reading the book shows the update")
def reading_book_shows_update(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_book"]
    response = tink_api.get(f"/book/{created['id']}")
    tink_api.assert_status(response, 200)
    loaded = tink_api.json(response)
    assert loaded["rating"] == 4.5
    assert loaded["description"] == "Updated by E2E"


@when("I start reading the created book")
def start_reading_created_book(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_book"]
    payload = {"platform": "Kindle", "current_page": 12, "progress_percentage": 9.5}
    response = tink_api.post(f"/book/{created['id']}/reading", payload)
    tink_api.assert_status(response, 200)
    scenario_state["reading_book"] = tink_api.json(response)


@then("the reading list contains the created book")
def reading_list_contains_created_book(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get("/book/reading", {"page": 0, "size": 50})
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    created = scenario_state["created_book"]
    assert any(row.get("id") == created["id"] for row in rows)


@when("I add a note to the created book")
def add_note_to_created_book(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_book"]
    payload = {"content": "Initial E2E note", "page": 12}
    response = tink_api.post(f"/book/{created['id']}/notes", payload)
    tink_api.assert_status(response, 200, 201)
    scenario_state["created_note"] = tink_api.json(response)


@then("I can read and update the created note")
def can_read_and_update_created_note(tink_api: TinkApi, scenario_state: dict) -> None:
    book = scenario_state["created_book"]
    note = scenario_state["created_note"]

    response = tink_api.get(f"/book/{book['id']}/notes/{note['id']}")
    tink_api.assert_status(response, 200)
    loaded = tink_api.json(response)
    assert loaded["content"] == "Initial E2E note"

    response = tink_api.patch(
        f"/book/{book['id']}/notes/{note['id']}",
        {"content": "Updated E2E note", "progress_percentage": 10.0},
    )
    tink_api.assert_status(response, 200)
    updated = tink_api.json(response)
    assert updated["content"] == "Updated E2E note"

    response = tink_api.get(f"/book/{book['id']}/notes", {"page": 0, "size": 50})
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    assert any(row.get("id") == note["id"] for row in rows)


@when("I archive the created book")
def archive_created_book(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_book"]
    payload = {"status": "done", "archived_date": date.today().isoformat()}
    response = tink_api.post(f"/book/{created['id']}/archive", payload)
    tink_api.assert_status(response, 200)
    scenario_state["archived_book"] = tink_api.json(response)


@then("the archive list contains the created book")
def archive_list_contains_created_book(tink_api: TinkApi, scenario_state: dict) -> None:
    response = tink_api.get("/book/archived", {"page": 0, "size": 50, "status": "done"})
    tink_api.assert_status(response, 200)
    rows = tink_api.json(response)
    created = scenario_state["created_book"]
    assert any(row.get("id") == created["id"] for row in rows)


@when("I delete the created book")
def delete_created_book(
    tink_api: TinkApi,
    scenario_state: dict,
    cleanup_books: list[int],
) -> None:
    created = scenario_state["created_book"]
    note = scenario_state.get("created_note")
    if note:
        response = tink_api.delete(f"/book/{created['id']}/notes/{note['id']}")
        tink_api.assert_status(response, 204, 404)

    response = tink_api.delete(f"/book/{created['id']}")
    tink_api.assert_status(response, 204)
    if created["id"] in cleanup_books:
        cleanup_books.remove(created["id"])


@then("reading the deleted book returns not found")
def reading_deleted_book_returns_not_found(tink_api: TinkApi, scenario_state: dict) -> None:
    created = scenario_state["created_book"]
    response = tink_api.get(f"/book/{created['id']}")
    tink_api.assert_status(response, 404)
