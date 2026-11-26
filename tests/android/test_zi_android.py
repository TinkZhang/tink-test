from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pytest_bdd import given, scenario, then, when

from appium_client import WeightPage

pytestmark = pytest.mark.android


@pytest.mark.mock
@scenario("android/zi.feature", "Reading and writing cards open separate flows")
def test_zi_separate_flows():
    pass


@pytest.mark.e2e
@scenario("android/zi.feature", "The written character list loads from the development API")
def test_zi_development_list():
    pass


@pytest.fixture
def zi_destination():
    return {}


@given("the Android Zi app is using the local mock API")
def zi_mock(zi_destination):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/zi/written", "/dev/zi/written"):
                rows = ["土"]
            elif self.path in ("/zi/", "/dev/zi/"):
                rows = [
                    {"zi": "读", "proficiency": 5, "last_date": "2026-11-26"},
                    {"zi": "习", "proficiency": 3, "last_date": "2026-11-26"},
                ]
            else:
                self.send_error(404)
                return
            data = json.dumps(rows).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    with ThreadingHTTPServer(("0.0.0.0", 8765), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        zi_destination["url"] = "http://10.0.2.2:8765/"
        try:
            yield
        finally:
            server.shutdown()
            thread.join()


@given("the Android Zi app is using the deployed development API")
def zi_live(tink_api, zi_destination):
    assert tink_api.base_url.endswith("/dev")
    response = tink_api.get("/zi/written")
    tink_api.assert_status(response, 200)
    zi_destination["written"] = tink_api.json(response)
    zi_destination["url"] = tink_api.base_url + "/"


@when("I open the Zi dashboard")
def open_zi(android_driver, zi_destination):
    page = WeightPage(android_driver)
    page.launch_app(zi_destination["url"])
    page.tap_first([
        (AppiumBy.ID, "app.tinks.tink:id/top_bar_menu_button"),
        (AppiumBy.ID, "top_bar_menu_button"),
        (AppiumBy.ACCESSIBILITY_ID, "打开抽屉"),
    ])
    page.tap_drawer_destination("drawer_destination_zi")
    page.find_by_test_tag("zi_dashboard")


@then("the Zi reading and writing cards open their own lists")
def check_lists(android_driver):
    page = WeightPage(android_driver)
    page.find_by_test_tag("zi_read_card").click()
    page.find_by_test_tag("zi_read_list")
    page.wait_for_text("读")
    assert not android_driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("习")')
    page.find_by_test_tag("top_bar_back_button").click()
    page.find_by_test_tag("zi_written_card").click()
    page.find_by_test_tag("zi_written_list")
    page.wait_for_text("土")
    page.find_by_test_tag("top_bar_back_button").click()


@then("the Zi plus icons open the reading dialog and handwriting board")
def check_add_flows(android_driver):
    page = WeightPage(android_driver)
    page.find_by_test_tag("zi_add_read").click()
    page.wait_for_text("添加会读的字")
    page.wait_for_text("取消").click()
    page.find_by_test_tag("zi_add_written").click()
    page.find_by_test_tag("zi_handwriting_board")
    assert not page.find_by_test_tag("zi_confirm_written").is_enabled()


@then("the written character list matches the development API")
def check_development_list(android_driver, zi_destination):
    page = WeightPage(android_driver)
    page.find_by_test_tag("zi_written_card").click()
    page.find_by_test_tag("zi_written_list")
    characters = zi_destination["written"]
    page.wait_for_text(characters[0] if characters else "还没有会写的汉字")
