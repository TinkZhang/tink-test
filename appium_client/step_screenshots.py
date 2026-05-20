from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class StepScreenshot:
    index: int
    feature: str
    scenario: str
    step: str
    status: str
    image: str
    timestamp_ms: int


class StepScreenshotRecorder:
    def __init__(self, report_dir: str | Path) -> None:
        self.report_dir = Path(report_dir)
        self.screenshot_dir = self.report_dir / "screenshots"
        self.manifest_path = self.screenshot_dir / "manifest.json"
        self._counter = 0
        self._items: list[StepScreenshot] = []

    def capture(
        self,
        driver: WebDriver,
        *,
        feature: Any,
        scenario: Any,
        step: Any,
        status: str,
    ) -> None:
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self._counter += 1

        feature_name = _name(feature, fallback="Feature")
        scenario_name = _name(scenario, fallback="Scenario")
        step_name = _step_name(step)
        filename = (
            f"{self._counter:03d}-"
            f"{_slug(scenario_name)}-"
            f"{_slug(status)}-"
            f"{_slug(step_name)}.png"
        )
        image_path = self.screenshot_dir / filename

        driver.save_screenshot(str(image_path))
        self._items.append(
            StepScreenshot(
                index=self._counter,
                feature=feature_name,
                scenario=scenario_name,
                step=step_name,
                status=status,
                image=f"screenshots/{filename}",
                timestamp_ms=int(time.time() * 1000),
            )
        )
        self._write_manifest()

    def _write_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps([asdict(item) for item in self._items], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def _step_name(step: Any) -> str:
    keyword = getattr(step, "keyword", "").strip()
    name = getattr(step, "name", None) or str(step)
    return f"{keyword} {name}".strip()


def _name(value: Any, *, fallback: str) -> str:
    return getattr(value, "name", None) or fallback


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-").lower()
    return slug[:80] or "step"
