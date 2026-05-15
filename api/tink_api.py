from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class TinkApiError(AssertionError):
    """Raised when the black-box API preconditions or responses are invalid."""


@dataclass(frozen=True)
class TinkApi:
    base_url: str
    timeout: float = 10.0

    def __post_init__(self) -> None:
        normalized = self.base_url.rstrip("/")
        object.__setattr__(self, "base_url", normalized)

    def check_dev_weight_available(self) -> None:
        response = self.get_weights()
        if response.status_code == 404:
            raise TinkApiError(
                f"{self.base_url}/weight returned 404. "
                "The deployed dev API route is unavailable; deploy backend /dev routes before running E2E tests."
            )
        self.assert_status(response, 200)

    def create_weight(self, weight: float) -> requests.Response:
        return requests.post(
            self._url("/weight"),
            json={"weight": weight},
            timeout=self.timeout,
        )

    def get_weights(self) -> requests.Response:
        return requests.get(self._url("/weight"), timeout=self.timeout)

    def delete_weight(self, weight_id: int) -> requests.Response:
        return requests.delete(self._url(f"/weight/{weight_id}"), timeout=self.timeout)

    @staticmethod
    def assert_status(response: requests.Response, *expected_statuses: int) -> None:
        if response.status_code not in expected_statuses:
            expected = ", ".join(str(status) for status in expected_statuses)
            raise TinkApiError(
                f"Expected HTTP {expected}, got {response.status_code}: {response.text}"
            )

    @staticmethod
    def json(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise TinkApiError(f"Response was not valid JSON: {response.text}") from exc

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"
