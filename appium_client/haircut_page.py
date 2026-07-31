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


class HaircutPage:
    def __init__(self, driver: WebDriver, timeout: float = 20.0) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_haircut_from_drawer(self) -> None:
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
        menu_button_locators = [
            (AppiumBy.ID, "app.tinks.tink:id/top_bar_menu_button"),
            (AppiumBy.ID, "top_bar_menu_button"),
            (AppiumBy.ACCESSIBILITY_ID, "打开抽屉"),
        ]
        self.return_to_top_level_if_needed(menu_button_locators)
        self.tap_first(menu_button_locators)
        self.tap_first(
            [
                (AppiumBy.ID, "app.tinks.tink:id/drawer_destination_hair"),
                (AppiumBy.ID, "drawer_destination_hair"),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("理发")'),
            ]
        )
        self.wait_for_text("理发历史")

    def assert_empty_history(self) -> None:
        self.wait_for_text("理发历史")
        assert "¥" not in self.driver.page_source

    def assert_history_contains(self, shop_name: str, price: int, date_text: str) -> None:
        self._scroll_until_text(shop_name)
        self.wait_for_text(shop_name)
        self.wait_for_text(f"¥{price}")
        self.wait_for_text(date_text)

    def assert_history_contains_any(self, shop_names: Iterable[str]) -> None:
        for shop_name in shop_names:
            self._scroll_until_text(shop_name)
            self.wait_for_text(shop_name)

    def assert_days_text_visible(self) -> None:
        self.wait_for_text("天没理发了")

    def add_haircut(self, shop_name: str, price: int) -> None:
        self.tap_first(
            [
                (AppiumBy.ACCESSIBILITY_ID, "添加记录"),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("添加记录")'),
            ]
        )
        self.wait_for_text("添加理发记录")
        fields = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
        if len(fields) < 2:
            self._capture_diagnostics("haircut-dialog-fields-missing")
            raise AssertionError("Expected shop and price text fields in haircut dialog")
        fields[0].click()
        fields[0].send_keys(shop_name)
        fields[1].click()
        fields[1].send_keys(str(price))
        self.tap_text("确定")
        self.wait_for_text(shop_name)

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

    def tap_text(self, text: str) -> None:
        self.tap_first([(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')])

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

    def _scroll_until_text(self, text: str) -> None:
        if text in self.driver.page_source:
            return
        for _ in range(6):
            self._swipe_page_up()
            time.sleep(0.4)
            if text in self.driver.page_source:
                return

    def _swipe_page_up(self) -> None:
        rect = self.driver.get_window_rect()
        x = rect["x"] + rect["width"] // 2
        start_y = rect["y"] + int(rect["height"] * 0.82)
        end_y = rect["y"] + int(rect["height"] * 0.28)
        self.driver.swipe(x, start_y, x, end_y, 500)

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

    def _adb_shell(self, args: list[str]) -> None:
        command = ["adb"]
        if os.environ.get("ANDROID_SERIAL"):
            command.extend(["-s", os.environ["ANDROID_SERIAL"]])
        command.extend(["shell", *args])
        subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
