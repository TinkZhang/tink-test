from __future__ import annotations

import os
import time
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
def generated_weight() -> float:
    suffix = int(time.time() * 1000) % 1000
    return round(70 + (suffix / 1000), 3)
