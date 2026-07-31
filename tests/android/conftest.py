from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from appium_client import HaircutPage, WeightPage, create_android_driver
from appium_client.step_screenshots import StepScreenshotRecorder
from mock_server import HaircutMockServer, WeightMockServer


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("TINK_RUN_APPIUM") == "1":
        return
    skip = pytest.mark.skip(reason="Set TINK_RUN_APPIUM=1 to run Android Appium tests")
    for item in items:
        if "android" in item.keywords:
            item.add_marker(skip)


def pytest_bdd_after_step(
    request: pytest.FixtureRequest,
    feature: Any,
    scenario: Any,
    step: Any,
    step_func_args: dict[str, Any],
) -> None:
    _capture_step_screenshot(request, feature, scenario, step, step_func_args, "passed")


def pytest_bdd_step_error(
    request: pytest.FixtureRequest,
    feature: Any,
    scenario: Any,
    step: Any,
    step_func_args: dict[str, Any],
    exception: Exception,
) -> None:
    _capture_step_screenshot(request, feature, scenario, step, step_func_args, "failed")


@pytest.fixture
def android_driver() -> Generator:
    driver = create_android_driver()
    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture
def weight_page(android_driver) -> WeightPage:
    return WeightPage(android_driver)


@pytest.fixture
def haircut_page(android_driver) -> HaircutPage:
    return HaircutPage(android_driver)


@pytest.fixture
def weight_mock_server() -> Generator[WeightMockServer, None, None]:
    fixture_path = Path("fixtures/android/weight/empty.json")
    server = WeightMockServer(fixture_path=fixture_path, host="0.0.0.0")
    server.start()
    try:
        yield server
    finally:
        server.stop()


@pytest.fixture
def haircut_mock_server() -> Generator[HaircutMockServer, None, None]:
    fixture_path = Path("fixtures/android/haircut/empty.json")
    server = HaircutMockServer(fixture_path=fixture_path, host="0.0.0.0")
    server.start()
    try:
        yield server
    finally:
        server.stop()


def _capture_step_screenshot(
    request: pytest.FixtureRequest,
    feature: Any,
    scenario: Any,
    step: Any,
    step_func_args: dict[str, Any],
    status: str,
) -> None:
    if "android" not in request.node.keywords:
        return

    report_dir = os.environ.get("TINK_ANDROID_REPORT_DIR")
    if not report_dir:
        return

    driver = step_func_args.get("android_driver")
    if driver is None:
        weight_page = step_func_args.get("weight_page")
        driver = getattr(weight_page, "driver", None)
    if driver is None:
        haircut_page = step_func_args.get("haircut_page")
        driver = getattr(haircut_page, "driver", None)
    if driver is None:
        driver = request.node.funcargs.get("android_driver")
    if driver is None:
        weight_page = request.node.funcargs.get("weight_page")
        driver = getattr(weight_page, "driver", None)
    if driver is None:
        haircut_page = request.node.funcargs.get("haircut_page")
        driver = getattr(haircut_page, "driver", None)
    if driver is None:
        return

    recorder = request.config.stash.setdefault(
        _step_screenshot_key,
        StepScreenshotRecorder(report_dir),
    )
    try:
        recorder.capture(driver, feature=feature, scenario=scenario, step=step, status=status)
    except Exception as exc:
        print(f"Unable to capture Android step screenshot: {exc}")


_step_screenshot_key = pytest.StashKey[StepScreenshotRecorder]()
