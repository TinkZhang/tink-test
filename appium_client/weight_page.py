from __future__ import annotations

import re
from collections.abc import Iterable

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
        self.tap_accessibility("打开抽屉")
        self.tap_first(
            [
                (AppiumBy.ID, "app.tinks.tink:id/drawer_destination_weight"),
                (AppiumBy.ID, "drawer_destination_weight"),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("体重 C")'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("设置 B")'),
            ]
        )
        self.wait_for_text("体重趋势")

    def open_history(self) -> None:
        self.tap_first(
            [
                (AppiumBy.ID, "app.tinks.tink:id/weight_history_button"),
                (AppiumBy.ID, "weight_history_button"),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("查看所有历史记录")'),
            ]
        )
        self.wait_for_any_text(["体重历史", "暂无体重记录", "斤"])

    def go_back(self) -> None:
        try:
            self.tap_accessibility("返回上级")
        except TimeoutException:
            self.driver.back()

    def add_weight_by_drag(self) -> float:
        drag_area = self.find_by_test_tag("weight_drag_area")
        rect = drag_area.rect
        start_x = rect["x"] + rect["width"] // 2
        start_y = rect["y"] + int(rect["height"] * 0.75)
        end_y = rect["y"] + int(rect["height"] * 0.2)
        self.driver.swipe(start_x, start_y, start_x, end_y, 700)
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

    def current_weight_value(self) -> float:
        element = self.find_by_test_tag("weight_current_value")
        return float(element.text)

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

    def assert_api_failure_visible(self) -> None:
        self.wait_for_text("Request failed")

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

    def find_first_present(self, locators: Iterable[tuple[str, str]]) -> WebElement:
        return self.wait.until(lambda _: self._find_first_present(locators))

    def tap_accessibility(self, label: str) -> None:
        self.wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, label))).click()

    def tap_first(self, locators: Iterable[tuple[str, str]]) -> None:
        last_error: Exception | None = None
        for locator in locators:
            try:
                self.wait.until(EC.element_to_be_clickable(locator)).click()
                return
            except (NoSuchElementException, TimeoutException) as exc:
                last_error = exc
        raise AssertionError(f"Unable to tap any locator: {list(locators)}") from last_error

    def _find_first_present(self, locators: Iterable[tuple[str, str]]) -> WebElement | bool:
        for locator in locators:
            try:
                return self.driver.find_element(*locator)
            except NoSuchElementException:
                continue
        return False

    def _parse_first_float(self, text: str) -> float:
        match = re.search(r"\d+(?:\.\d+)?", text)
        if not match:
            raise AssertionError(f"Unable to parse weight from text: {text}")
        return float(match.group())
