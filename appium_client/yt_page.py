from __future__ import annotations

import subprocess

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from appium_client.weight_page import WeightPage


class YtPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    def by_tag(self, tag):
        return self.wait.until(lambda d: d.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().resourceId("{tag}")'))

    def open(self):
        self.driver.activate_app("app.tinks.tink")
        self.by_tag("top_bar_menu_button").click()
        WeightPage(self.driver).tap_drawer_destination("drawer_destination_yt")
        self.by_tag("yt_library")

    def open_add(self):
        if not self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("yt_add_url")'):
            self.by_tag("yt_add_link").click()

    def submit(self, url, kind):
        self.open_add()
        field = self.by_tag("yt_add_url")
        field.clear()
        field.send_keys(url)
        try:
            self.driver.hide_keyboard()
        except Exception:
            pass
        self.by_tag(f"yt_kind_{kind}").click()
        self.by_tag("yt_add_confirm").click()
        allow = self.driver.find_elements(AppiumBy.ID, "com.android.permissioncontroller:id/permission_allow_button")
        if allow:
            allow[0].click()

    def wait_for_download(self, video_id, kind):
        self.by_tag("yt_tab_2").click()
        self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView('
            f'new UiSelector().resourceId("yt_download_{video_id}_{kind}"))')

        def completed(driver):
            card = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().resourceId("yt_download_{video_id}_{kind}")')
            text = " ".join(e.text for e in card.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView"))
            assert "Failed" not in text, text
            return "Ready" in text

        WebDriverWait(self.driver, 900, poll_frequency=2).until(completed)

    def media_paths(self, kind):
        extension = "m4a" if kind == "audio" else "mp4"
        # Debug-only readback verifies the actual output, not just a completion label.
        result = subprocess.run(["adb", "shell", "run-as", "app.tinks.tink", "find", "files/yt",
            "-name", f"media.{extension}"], text=True, capture_output=True, check=True)
        paths = result.stdout.strip().splitlines()
        assert paths, f"No {extension} output file exists"
        return paths
