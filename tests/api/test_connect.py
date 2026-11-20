from __future__ import annotations

from base64 import b64encode
from urllib.parse import urljoin

import pytest
import requests
from pytest_bdd import given, scenario, then, when

from api import TinkApi


@scenario("api/connect.feature", "Resume an upload and exchange text between two clients")
def test_connect_transfer_and_text() -> None:
    pass


@given("the Connect development hub is available")
def connect_available(tink_api: TinkApi, scenario_state: dict) -> None:
    assert tink_api.base_url.endswith("/dev"), "Connect E2E requires the development hub"
    response = tink_api.get("/connect")
    tink_api.assert_status(response, 200)
    scenario_state["prior_text"] = response.json()["text"]


@pytest.fixture
def connect_cleanup(tink_api: TinkApi, scenario_state: dict):
    yield
    if file_id := scenario_state.get("file_id"):
        tink_api.delete(f"/connect/files/{file_id}")
    if "published_text" in scenario_state:
        latest = tink_api.get("/connect")
        if latest.ok and latest.json()["text"] == scenario_state["published_text"]:
            tink_api.put("/connect/text", {"text": scenario_state["prior_text"]})


@when("the first client completes a multi-chunk file upload and shares text")
def upload_connect_file(tink_api: TinkApi, scenario_state: dict, unique_suffix: str, connect_cleanup) -> None:
    chunk_size = 6 * 1024 * 1024
    contents = b"connect" * ((chunk_size // 7) + 2)
    name = f"connect-{unique_suffix}.unknown"
    created = tink_api.post("/connect/files", {"name": name, "content_type": "application/octet-stream", "size": len(contents)})
    tink_api.assert_status(created, 201)
    ticket = created.json()
    scenario_state["file_id"] = ticket["id"]
    headers = {
        "Tus-Resumable": "1.0.0",
        "x-signature": ticket["token"],
        "apikey": ticket["publishable_key"],
    }
    metadata = {
        "bucketName": ticket["bucket"],
        "objectName": ticket["object_path"],
        "contentType": "application/octet-stream",
    }
    new_upload = requests.post(ticket["upload_url"], headers={
        **headers,
        "Upload-Length": str(len(contents)),
        "Upload-Metadata": ",".join(f"{key} {b64encode(value.encode()).decode()}" for key, value in metadata.items()),
    }, allow_redirects=False, timeout=40)
    assert new_upload.status_code == 201, f"Could not start storage upload: HTTP {new_upload.status_code}"
    destination = urljoin(ticket["upload_url"], new_upload.headers["Location"])

    def patch(offset: int, chunk: bytes) -> requests.Response:
        response = requests.patch(destination, headers={
            **headers, "Upload-Offset": str(offset), "Content-Type": "application/offset+octet-stream",
        }, data=chunk, allow_redirects=False, timeout=40)
        assert response.status_code == 204, f"Could not upload chunk: HTTP {response.status_code}"
        return response

    patch(0, contents[:chunk_size])
    offset = requests.head(destination, headers=headers, allow_redirects=False, timeout=20)
    assert offset.ok
    assert int(offset.headers["Upload-Offset"]) == chunk_size
    last = patch(chunk_size, contents[chunk_size:])
    assert int(last.headers["Upload-Offset"]) == len(contents)

    complete = tink_api.post(f"/connect/files/{ticket['id']}/complete", None)
    tink_api.assert_status(complete, 200)
    assert complete.json()["name"] == name and complete.json()["size"] == len(contents)
    scenario_state["contents"] = contents
    scenario_state["published_text"] = f"Connect development test {unique_suffix}"
    tink_api.assert_status(tink_api.put("/connect/text", {"text": scenario_state["published_text"]}), 200)


@then("the second client can download the same bytes and read the text")
def check_connect_transfer(tink_api: TinkApi, scenario_state: dict) -> None:
    reader = TinkApi(tink_api.base_url)
    hub = reader.get("/connect")
    reader.assert_status(hub, 200)
    assert hub.json()["text"] == scenario_state["published_text"]
    assert any(file["id"] == scenario_state["file_id"] for file in hub.json()["files"])
    download = reader.get(f"/connect/files/{scenario_state['file_id']}/download")
    reader.assert_status(download, 200)
    received = requests.get(download.json()["url"], timeout=40)
    assert received.ok and received.content == scenario_state["contents"]


@then("deleting the file removes it from the shared list")
def delete_connect_file(tink_api: TinkApi, scenario_state: dict) -> None:
    file_id = scenario_state["file_id"]
    tink_api.assert_status(tink_api.delete(f"/connect/files/{file_id}"), 204)
    hub = tink_api.get("/connect")
    tink_api.assert_status(hub, 200)
    assert all(file["id"] != file_id for file in hub.json()["files"])
