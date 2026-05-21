from __future__ import annotations

import os
import re
import time
from collections.abc import Iterable
from pathlib import Path

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class WeightPage:
    def __init__(self, driver: WebDriver, timeout: float = 20.0) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_weight_from_drawer(self) -> None:
        self.driver.terminate_app("app.tinks.tink")
        self.driver.activate_app("app.tinks.tink")
        menu_button_locators = [
            (AppiumBy.ID, "app.tinks.tink:id/top_bar_menu_button"),
            (AppiumBy.ID, "top_bar_menu_button"),
            (AppiumBy.ACCESSIBILITY_ID, "打开抽屉"),
        ]
        self.return_to_top_level_if_needed(menu_button_locators)
        self.tap_first(menu_button_locators)
        self.tap_first(
            [
                (AppiumBy.ID, "app.tinks.tink:id/drawer_destination_weight"),
                (AppiumBy.ID, "drawer_destination_weight"),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("体重 C")'),
            ]
        )
        self.wait_for_text("体重趋势")

    def assert_current_weight_blank(self) -> None:
        self.wait_for_text("体重趋势")
        elements = self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            r'new UiSelector().textMatches("\\d+\\.\\d")',
        )
        assert not elements, "Expected current weight value to be blank"

    def assert_current_weight_is(self, weight: float) -> None:
        self.wait.until(lambda _: abs(self.current_weight_value() - weight) <= 0.05)

    def assert_status_shows_last_date(self, date_text: str) -> None:
        self.wait_for_text(f"上次记录: {date_text}")

    def assert_status_shows_today_recorded(self) -> None:
        self.wait_for_text("今日已记录")

    def open_history(self) -> None:
        history_button_locators = [
            (AppiumBy.ID, "app.tinks.tink:id/weight_history_button"),
            (AppiumBy.ID, "weight_history_button"),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("查看所有历史记录")'),
        ]
        self.scroll_weight_dashboard_to(history_button_locators)
        self.tap_first(history_button_locators)
        self.wait_for_any_text(["体重历史", "暂无体重记录", "斤"])

    def go_back(self) -> None:
        try:
            self.tap_accessibility("返回上级")
        except TimeoutException:
            self.driver.back()

    def adjust_weight_to(self, target_weight: float) -> None:
        drag_area = self.find_by_test_tag("weight_drag_area")
        rect = drag_area.rect
        x = rect["x"] + rect["width"] // 2
        center_y = rect["y"] + rect["height"] // 2
        min_y = rect["y"] + int(rect["height"] * 0.15)
        max_y = rect["y"] + int(rect["height"] * 0.85)

        for _ in range(20):
            current = self.current_weight_value()
            diff = target_weight - current
            if abs(diff) <= 0.05:
                return

            drag_pixels = max(-120, min(120, int(-diff * 300)))
            if drag_pixels == 0:
                drag_pixels = -1 if diff > 0 else 1
            end_y = max(min_y, min(max_y, center_y + drag_pixels))
            self.driver.swipe(x, center_y, x, end_y, 450)
            self.wait.until(lambda _: abs(self.current_weight_value() - current) >= 0.05)

        raise AssertionError(
            f"Unable to adjust current weight from {self.current_weight_value():.1f} "
            f"to {target_weight:.1f}"
        )

    def add_current_weight(self) -> float:
        button = self.find_first_present(
            [
                (AppiumBy.ID, "app.tinks.tink:id/weight_add_record_button"),
                (AppiumBy.ID, "weight_add_record_button"),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("添加新记录")'),
            ]
        )
        added_weight = self._parse_first_float(button.text)
        button.click()
        self.wait_for_text(f"{added_weight:.1f} 斤")
        return added_weight

    def add_weight_by_drag(self) -> float:
        drag_area = self.find_by_test_tag("weight_drag_area")
        rect = drag_area.rect
        start_x = rect["x"] + rect["width"] // 2
        start_y = rect["y"] + int(rect["height"] * 0.75)
        end_y = rect["y"] + int(rect["height"] * 0.2)
        self.driver.swipe(start_x, start_y, start_x, end_y, 700)
        return self.add_current_weight()

    def current_weight_value(self) -> float:
        elements = self._find_by_test_tag_now("weight_current_value")
        if not elements:
            elements = self.driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR,
                r'new UiSelector().textMatches("\\d+\\.\\d")',
            )

        for element in elements:
            try:
                return float(element.text)
            except ValueError:
                continue

        raise AssertionError("Unable to read current weight value from the Android UI")

    def assert_history_contains_weight(self, weight: float) -> None:
        self.wait_for_text(f"{weight:.1f} 斤")

    def assert_history_empty(self) -> None:
        self.wait_for_text("暂无体重记录")

    def assert_history_does_not_contain_weight(self, weight: float) -> None:
        text = f"{weight:.1f} 斤"
        self.wait.until(
            lambda _: not self.driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().text("{text}")',
            )
        )

    def assert_history_does_not_contain_weight_id(self, weight_id: int) -> None:
        tags = [
            f"app.tinks.tink:id/weight_history_item_{weight_id}",
            f"weight_history_item_{weight_id}",
            f"app.tinks.tink:id/weight_delete_button_{weight_id}",
            f"weight_delete_button_{weight_id}",
        ]
        self.wait.until(
            lambda _: not any(self.driver.find_elements(AppiumBy.ID, tag) for tag in tags)
        )

    def assert_api_failure_visible(self) -> None:
        self.wait_for_text("Request failed")

    def assert_trend_empty(self) -> None:
        self.wait_for_text("暂无趋势数据")

    def assert_trend_has_data(self) -> None:
        self.wait.until(
            lambda _: not self.driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("暂无趋势数据")',
            )
        )

    def select_month_trend(self) -> None:
        self.tap_first(
            [
                (AppiumBy.ID, "app.tinks.tink:id/weight_trend_month"),
                (AppiumBy.ID, "weight_trend_month"),
                (AppiumBy.ACCESSIBILITY_ID, "本月"),
            ]
        )

    def select_all_trend(self) -> None:
        self.tap_first(
            [
                (AppiumBy.ID, "app.tinks.tink:id/weight_trend_all"),
                (AppiumBy.ID, "weight_trend_all"),
                (AppiumBy.ACCESSIBILITY_ID, "全部"),
            ]
        )

    def scroll_to_test_tag(self, tag: str) -> None:
        locators = [
            (AppiumBy.ID, f"app.tinks.tink:id/{tag}"),
            (AppiumBy.ID, tag),
        ]
        self.scroll_weight_dashboard_to(locators)

    def delete_weight(self, weight_id: int) -> None:
        self.tap_first(
            [
                (AppiumBy.ID, f"app.tinks.tink:id/weight_delete_button_{weight_id}"),
                (AppiumBy.ID, f"weight_delete_button_{weight_id}"),
            ]
        )

    def wait_for_text(self, text: str) -> WebElement:
        return self.wait.until(
            EC.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
            )
        )

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

    def wait_until_weight_changes(self, previous: float) -> None:
        self.wait.until(lambda _: abs(self.current_weight_value() - previous) >= 0.05)

    def find_by_test_tag(self, tag: str) -> WebElement:
        return self.find_first_present(
            [
                (AppiumBy.ID, f"app.tinks.tink:id/{tag}"),
                (AppiumBy.ID, tag),
            ]
        )

    def _find_by_test_tag_now(self, tag: str) -> list[WebElement]:
        elements = self.driver.find_elements(AppiumBy.ID, f"app.tinks.tink:id/{tag}")
        return elements or self.driver.find_elements(AppiumBy.ID, tag)

    def find_first_present(self, locators: Iterable[tuple[str, str]]) -> WebElement:
        return self.wait.until(lambda _: self._find_first_present(locators))

    def tap_accessibility(self, label: str) -> None:
        self.wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, label))).click()

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

    def scroll_weight_dashboard_to(self, locators: Iterable[tuple[str, str]]) -> None:
        locator_list = list(locators)
        if self._find_first_present(locator_list):
            return

        for _ in range(4):
            if self._scroll_weight_dashboard_once():
                time.sleep(0.5)
            else:
                self._swipe_page_up()
            if self._find_first_present(locator_list):
                return

        self._capture_diagnostics("scroll-target-missing")

    def tap_first(self, locators: Iterable[tuple[str, str]]) -> None:
        locator_list = list(locators)
        last_error: Exception | None = None
        for locator in locator_list:
            try:
                self.wait.until(EC.element_to_be_clickable(locator)).click()
                return
            except (NoSuchElementException, TimeoutException) as exc:
                last_error = exc
        self._capture_diagnostics("tap-first-failed")
        raise AssertionError(f"Unable to tap any locator: {locator_list}") from last_error

    def _find_first_present(self, locators: Iterable[tuple[str, str]]) -> WebElement | bool:
        for locator in locators:
            try:
                return self.driver.find_element(*locator)
            except NoSuchElementException:
                continue
        return False

    def _scroll_weight_dashboard_once(self) -> bool:
        try:
            dashboard = self.find_by_test_tag("weight_dashboard_list")
            rect = dashboard.rect
            return bool(
                self.driver.execute_script(
                    "mobile: scrollGesture",
                    {
                        "left": rect["x"],
                        "top": rect["y"],
                        "width": rect["width"],
                        "height": rect["height"],
                        "direction": "down",
                        "percent": 0.8,
                    },
                )
            )
        except Exception:
            return False

    def _swipe_page_up(self) -> None:
        rect = self.driver.get_window_rect()
        x = rect["x"] + rect["width"] // 2
        start_y = rect["y"] + int(rect["height"] * 0.82)
        end_y = rect["y"] + int(rect["height"] * 0.28)
        self.driver.swipe(x, start_y, x, end_y, 500)

    def _parse_first_float(self, text: str) -> float:
        match = re.search(r"\d+(?:\.\d+)?", text)
        if not match:
            raise AssertionError(f"Unable to parse weight from text: {text}")
        return float(match.group())

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
