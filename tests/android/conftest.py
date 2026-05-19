from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest

from appium_client import WeightPage, create_android_driver
from mock_server import WeightMockServer


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("TINK_RUN_APPIUM") == "1":
        return
    skip = pytest.mark.skip(reason="Set TINK_RUN_APPIUM=1 to run Android Appium tests")
    for item in items:
        if "android" in item.keywords:
            item.add_marker(skip)


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
def weight_mock_server() -> Generator[WeightMockServer, None, None]:
    fixture_path = Path("fixtures/android/weight/empty.json")
    server = WeightMockServer(fixture_path=fixture_path, host="0.0.0.0")
    server.start()
    try:
        yield server
    finally:
        server.stop()
