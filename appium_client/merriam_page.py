from __future__ import annotations

import os
import re
import subprocess
import time
from collections.abc import Iterable
from pathlib import Path

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class MerriamPage:
    def __init__(self, driver: WebDriver, timeout: float = 20.0) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_merriam_from_drawer(self) -> None:
        self._adb_shell(["am", "force-stop", "app.tinks.tink"])
        if os.environ.get("TINK_ANDROID_API_BASE_URL_OVERRIDE"):
            self._adb_shell(
                [
                    "am",
                    "broadcast",
                    "-n",
                    "app.tinks.tink/.debug.ApiBaseUrlOverrideReceiver",
                    "-a",
                    "app.tinks.tink.debug.SET_API_BASE_URL",
                    "--es",
                    "base_url",
                    os.environ["TINK_ANDROID_API_BASE_URL_OVERRIDE"],
                ]
            )
        self._adb_shell(
            [
                "am",
                "start",
                "-W",
                "-n",
                "app.tinks.tink/.MainActivity",
                "-a",
                "android.intent.action.MAIN",
                "-c",
                "android.intent.category.LAUNCHER",
            ]
        )
        self._dismiss_system_dialogs()
        menu_button_locators = [
            (AppiumBy.ID, "app.tinks.tink:id/top_bar_menu_button"),
            (AppiumBy.ID, "top_bar_menu_button"),
            (AppiumBy.ACCESSIBILITY_ID, "打开抽屉"),
        ]
        self.return_to_top_level_if_needed(menu_button_locators)
        self.tap_first(menu_button_locators)
        self.tap_first(
            [
                (AppiumBy.ID, "app.tinks.tink:id/drawer_destination_merriam"),
                (AppiumBy.ID, "drawer_destination_merriam"),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("M-W Builder")'),
            ]
        )
        self.wait_for_text("Latest root")

    def assert_summary_latest(self, latest: int) -> None:
        self._bring_summary_into_view()
        if "Latest root" in self.driver.page_source:
            self.wait_for_text("Latest root")
            self.wait_for_text(str(latest))
            return

        if latest > 0:
            self.wait_for_text(f"Unit {max(1, latest // 10)}")
            return

        self.wait_for_text("Latest root")

    def assert_progress_position_for_latest(self, latest: int) -> None:
        if latest <= 0:
            self.assert_summary_latest(latest)
            return
        self.wait_for_text(f"Unit {max(1, latest // 10)}")

    def assert_builder_content_visible(self) -> None:
        self.wait_for_text("M-W Builder")
        self.wait_for_any_text(["Units", "Unit 1", "Unit 2", "BENE", "AM", "Unit 20"])

    def complete_root(self, root_id: int) -> None:
        tag = f"merriam_root_{root_id}"
        unit_id = max(1, root_id // 10)
        self.scroll_to_test_tag(f"merriam_unit_{unit_id}")
        if not self._find_by_test_tag_now(tag):
            self.tap_first(
                [
                    (AppiumBy.ACCESSIBILITY_ID, f"Toggle unit {unit_id}"),
                    (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().description("Toggle unit {unit_id}")'),
                ]
            )
        self.scroll_to_test_tag(tag)
        element = self.find_by_test_tag(tag)
        rect = element.rect
        self.driver.execute_script(
            "mobile: longClickGesture",
            {
                "x": rect["x"] + rect["width"] // 2,
                "y": rect["y"] + rect["height"] // 2,
                "duration": 1000,
            },
        )

    def scroll_to_test_tag(self, tag: str) -> None:
        if self._find_by_test_tag_now(tag):
            return
        for _ in range(8):
            self._swipe_page_down()
            time.sleep(0.3)
            if self._find_by_test_tag_now(tag):
                return
        for _ in range(8):
            self._swipe_page_up()
            time.sleep(0.4)
            if self._find_by_test_tag_now(tag):
                return
        self._capture_diagnostics(f"tag-missing-{tag}")

    def find_by_test_tag(self, tag: str) -> WebElement:
        return self.find_first_present(
            [
                (AppiumBy.ID, f"app.tinks.tink:id/{tag}"),
                (AppiumBy.ID, tag),
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().resourceId("{tag}")'),
            ]
        )

    def wait_for_text(self, text: str) -> WebElement:
        try:
            return self.wait.until(
                EC.presence_of_element_located(
                    (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
                )
            )
        except TimeoutException:
            self._capture_diagnostics(f"text-missing-{self._safe_name(text)}")
            raise

    def wait_for_any_text(self, texts: Iterable[str]) -> WebElement:
        def find_any(_: WebDriver) -> WebElement | bool:
            for text in texts:
                try:
                    return self.driver.find_element(
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        f'new UiSelector().textContains("{text}")',
                    )
                except NoSuchElementException:
                    continue
            return False

        return self.wait.until(find_any)

    def tap_first(self, locators: Iterable[tuple[str, str]]) -> None:
        locator_list = list(locators)
        element = self._find_first_present(locator_list)
        if element:
            element.click()
            return

        last_error: Exception | None = None
        for locator in locator_list:
            try:
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(locator)).click()
                return
            except (NoSuchElementException, TimeoutException) as exc:
                last_error = exc
        self._capture_diagnostics("tap-first-failed")
        raise AssertionError(f"Unable to tap any locator: {locator_list}") from last_error

    def find_first_present(self, locators: Iterable[tuple[str, str]]) -> WebElement:
        element = self._find_first_present(list(locators))
        if not element:
            raise AssertionError(f"Unable to find any locator: {locators}")
        return element

    def return_to_top_level_if_needed(self, menu_button_locators: Iterable[tuple[str, str]]) -> None:
        locator_list = list(menu_button_locators)
        back_button_locators = [
            (AppiumBy.ID, "app.tinks.tink:id/top_bar_back_button"),
            (AppiumBy.ID, "top_bar_back_button"),
            (AppiumBy.ACCESSIBILITY_ID, "返回上级"),
        ]

        for _ in range(3):
            if self._find_first_present(locator_list):
                return
            back_button = self._find_first_present(back_button_locators)
            if back_button:
                back_button.click()
            else:
                self.driver.back()
            time.sleep(0.5)

    def _find_first_present(self, locators: Iterable[tuple[str, str]]) -> WebElement | bool:
        for locator in locators:
            try:
                return self.driver.find_element(*locator)
            except NoSuchElementException:
                continue
        return False

    def _find_by_test_tag_now(self, tag: str) -> list[WebElement]:
        elements = self.driver.find_elements(AppiumBy.ID, f"app.tinks.tink:id/{tag}")
        if elements:
            return elements
        elements = self.driver.find_elements(AppiumBy.ID, tag)
        if elements:
            return elements
        return self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().resourceId("{tag}")',
        )

    def _swipe_page_up(self) -> None:
        rect = self.driver.get_window_rect()
        x = rect["x"] + rect["width"] // 2
        start_y = rect["y"] + int(rect["height"] * 0.82)
        end_y = rect["y"] + int(rect["height"] * 0.28)
        self.driver.swipe(x, start_y, x, end_y, 500)

    def _swipe_page_down(self) -> None:
        rect = self.driver.get_window_rect()
        x = rect["x"] + rect["width"] // 2
        start_y = rect["y"] + int(rect["height"] * 0.28)
        end_y = rect["y"] + int(rect["height"] * 0.82)
        self.driver.swipe(x, start_y, x, end_y, 500)

    def _bring_summary_into_view(self) -> None:
        if "Latest root" in self.driver.page_source:
            return
        for _ in range(8):
            self._swipe_page_down()
            time.sleep(0.3)
            if "Latest root" in self.driver.page_source:
                return

    def _capture_diagnostics(self, name: str) -> None:
        report_dir = os.environ.get("TINK_ANDROID_REPORT_DIR")
        if not report_dir:
            return

        output_dir = Path(report_dir) / "diagnostics"
        output_dir.mkdir(parents=True, exist_ok=True)
        stamp = f"{int(time.time() * 1000)}-{name}"

        try:
            (output_dir / f"{stamp}.xml").write_text(self.driver.page_source, encoding="utf-8")
        except Exception:
            pass

        try:
            self.driver.save_screenshot(str(output_dir / f"{stamp}.png"))
        except Exception:
            pass

    def _safe_name(self, text: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", text).strip("-")
        return safe[:60] or "text"

    def _dismiss_system_dialogs(self) -> None:
        for text in ["Wait", "等待"]:
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable(
                        (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
                    )
                ).click()
                time.sleep(1)
                return
            except (NoSuchElementException, TimeoutException):
                continue

    def _adb_shell(self, args: list[str]) -> None:
        command = ["adb"]
        if os.environ.get("ANDROID_SERIAL"):
            command.extend(["-s", os.environ["ANDROID_SERIAL"]])
        command.extend(["shell", *args])
        subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
