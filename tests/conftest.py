from __future__ import annotations

import os
import time
from datetime import UTC, datetime, timedelta
from collections.abc import Generator

import pytest

from api import TinkApi


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return os.environ.get("TINK_API_BASE_URL", "https://api.tinks.app/dev")


@pytest.fixture(scope="session")
def api_timeout_seconds() -> float:
    return float(os.environ.get("TINK_API_TIMEOUT_SECONDS", "10"))


@pytest.fixture(scope="session")
def tink_api(api_base_url: str, api_timeout_seconds: float) -> TinkApi:
    return TinkApi(base_url=api_base_url, timeout=api_timeout_seconds)


@pytest.fixture
def scenario_state() -> dict:
    return {}


@pytest.fixture
def cleanup_weights(tink_api: TinkApi) -> Generator[list[int], None, None]:
    weight_ids: list[int] = []
    yield weight_ids
    for weight_id in reversed(weight_ids):
        response = tink_api.delete_weight(weight_id)
        if response.status_code not in {204, 404}:
            raise AssertionError(
                f"Failed to clean up weight {weight_id}: HTTP {response.status_code} {response.text}"
            )


@pytest.fixture
def cleanup_haircuts(tink_api: TinkApi) -> Generator[list[int], None, None]:
    haircut_ids: list[int] = []
    yield haircut_ids
    for haircut_id in reversed(haircut_ids):
        response = tink_api.delete(f"/haircut/{haircut_id}")
        if response.status_code not in {204, 404}:
            raise AssertionError(
                f"Failed to clean up haircut {haircut_id}: HTTP {response.status_code} {response.text}"
            )


@pytest.fixture
def cleanup_books(tink_api: TinkApi) -> Generator[list[int], None, None]:
    book_ids: list[int] = []
    yield book_ids
    for book_id in reversed(book_ids):
        response = tink_api.delete(f"/book/{book_id}")
        if response.status_code not in {204, 404}:
            raise AssertionError(
                f"Failed to clean up book {book_id}: HTTP {response.status_code} {response.text}"
            )


@pytest.fixture
def cleanup_stories(tink_api: TinkApi) -> Generator[list[str], None, None]:
    story_ids: list[str] = []
    yield story_ids
    for story_id in reversed(story_ids):
        response = tink_api.delete(f"/story/{story_id}")
        if response.status_code not in {204, 404}:
            raise AssertionError(
                f"Failed to clean up story {story_id}: HTTP {response.status_code} {response.text}"
            )


@pytest.fixture
def cleanup_times(tink_api: TinkApi) -> Generator[list[int], None, None]:
    time_ids: list[int] = []
    yield time_ids
    for time_id in reversed(time_ids):
        response = tink_api.delete(f"/time/{time_id}")
        if response.status_code not in {204, 404, 502}:
            raise AssertionError(
                f"Failed to clean up time entry {time_id}: HTTP {response.status_code} {response.text}"
            )


@pytest.fixture
def generated_weight() -> float:
    suffix = int(time.time() * 1000) % 1000
    return round(70 + (suffix / 1000), 3)


@pytest.fixture
def unique_suffix() -> str:
    return str(int(time.time() * 1000))


@pytest.fixture
def future_time_window() -> tuple[str, str]:
    start = datetime.now(UTC).replace(microsecond=0) + timedelta(days=14)
    end = start + timedelta(minutes=30)
    return start.isoformat(), end.isoformat()
