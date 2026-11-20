from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pytest_bdd import given, scenario, then, when
from selenium.webdriver.support.ui import WebDriverWait

from appium_client import WeightPage


pytestmark = pytest.mark.android


@pytest.mark.mock
@scenario("android/connect.feature", "Confirm clearing the shared hub")
def test_clear_connect_hub() -> None:
    pass


@pytest.mark.e2e
@scenario("android/connect.feature", "Open Connect against the development API")
def test_open_deployed_connect_hub() -> None:
    pass


@pytest.fixture
def connect_mock():
    data = {
        "files": [{
            "id": "30276e91-8d6e-4208-8080-616f22a6cfd6",
            "name": "Mock Connect file.pdf",
            "content_type": "application/pdf",
            "size": 1024,
            "created_at": "2026-11-20T10:00:00Z",
        }],
        "text": "Mock shared text",
    }

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ("/connect", "/dev/connect"):
                self.send_error(404)
                return
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_DELETE(self):
            if self.path not in ("/connect", "/dev/connect"):
                self.send_error(404)
                return
            data.update(files=[], text="")
            self.send_response(204)
            self.end_headers()

    with ThreadingHTTPServer(("0.0.0.0", 8765), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield data
        finally:
            server.shutdown()
            thread.join()


@pytest.fixture
def connect_destination():
    return {}


@given("a mock Connect hub with a file and shared text")
def configure_mock_hub(connect_mock, connect_destination):
    connect_destination["url"] = "http://10.0.2.2:8765/"


@given("the Connect development API is available for Android")
def configure_dev_hub(tink_api, connect_destination):
    assert tink_api.base_url.endswith("/dev")
    tink_api.assert_status(tink_api.get("/connect"), 200)
    connect_destination["url"] = tink_api.base_url + "/"


@when("I open Connect in the Android drawer")
def open_connect(android_driver, connect_destination):
    page = WeightPage(android_driver)
    page.launch_app(connect_destination["url"])
    page.tap_first([
        (AppiumBy.ID, "app.tinks.tink:id/top_bar_menu_button"),
        (AppiumBy.ID, "top_bar_menu_button"),
        (AppiumBy.ACCESSIBILITY_ID, "打开抽屉"),
    ])
    page.find_by_test_tag("drawer_destination_home")

    viewport = android_driver.get_window_size()
    locator = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*drawer_destination_connect$")')
    for _ in range(5):
        buttons = android_driver.find_elements(*locator)
        visible = next((button for button in buttons if button.is_displayed()), None)
        if visible is not None:
            visible.click()
            break
        android_driver.execute_script("mobile: scrollGesture", {
            "left": 12,
            "top": 40,
            "width": int(viewport["width"] * 0.6),
            "height": viewport["height"] - 100,
            "direction": "down",
            "percent": 0.9,
        })
    else:
        page.find_by_test_tag("drawer_destination_connect").click()
    page.find_by_test_tag("connect_hub")


@then("Connect shows the mocked file")
def check_mock_file(android_driver):
    WeightPage(android_driver).wait_for_text("Mock Connect file.pdf")


@when("I confirm Delete all content")
def clear_hub(android_driver):
    page = WeightPage(android_driver)
    page.find_by_test_tag("connect_delete_all").click()
    page.wait_for_text("Delete all content?")
    page.find_by_test_tag("connect_confirm_clear").click()


@then("Connect shows an empty hub")
def check_empty_hub(android_driver, connect_mock):
    WeightPage(android_driver).wait_for_text("No files yet")
    assert connect_mock == {"files": [], "text": ""}


@then("Connect shows the loaded file hub")
def check_live_hub(android_driver):
    WebDriverWait(android_driver, 20).until(lambda driver: driver.find_elements(
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("[0-9]+ files?")'
    ))
