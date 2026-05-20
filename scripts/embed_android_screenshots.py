from __future__ import annotations

import html
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: embed_android_screenshots.py <android-report-dir>")
        return 2

    report_dir = Path(sys.argv[1])
    report_path = report_dir / "bdd-report.html"
    manifest_path = report_dir / "screenshots" / "manifest.json"

    if not report_path.exists() or not manifest_path.exists():
        return 0

    items = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not items:
        return 0

    report_html = report_path.read_text(encoding="utf-8")
    screenshots_html = _render_screenshots(items)
    marker = "<!-- tink-android-step-screenshots -->"
    if marker in report_html:
        report_html = report_html.split(marker)[0] + marker + "\n" + screenshots_html
    elif "</body>" in report_html:
        report_html = report_html.replace("</body>", f"{marker}\n{screenshots_html}\n</body>")
    else:
        report_html += f"\n{marker}\n{screenshots_html}\n"

    report_path.write_text(report_html, encoding="utf-8")
    index_path = report_dir / "index.html"
    if index_path.exists():
        index_path.write_text(report_html, encoding="utf-8")
    return 0


def _render_screenshots(items: list[dict[str, Any]]) -> str:
    by_scenario: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_scenario[(item["feature"], item["scenario"])].append(item)

    sections = []
    for (feature, scenario), scenario_items in by_scenario.items():
        cards = "\n".join(_render_card(item) for item in scenario_items)
        sections.append(
            f"""
            <section class="tink-step-scenario">
              <h3>{html.escape(scenario)}</h3>
              <p class="tink-step-feature">{html.escape(feature)}</p>
              <div class="tink-step-grid">
                {cards}
              </div>
            </section>
            """
        )

    return f"""
    <style>
      .tink-step-screenshots {{
        margin: 32px 0;
        padding: 24px;
        border-top: 1px solid #d0d7de;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .tink-step-screenshots h2 {{
        margin: 0 0 8px;
        font-size: 24px;
      }}
      .tink-step-screenshots > p {{
        margin: 0 0 20px;
        color: #57606a;
      }}
      .tink-step-scenario {{
        margin-top: 24px;
      }}
      .tink-step-scenario h3 {{
        margin: 0;
        font-size: 18px;
      }}
      .tink-step-feature {{
        margin: 4px 0 12px;
        color: #57606a;
        font-size: 13px;
      }}
      .tink-step-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
      }}
      .tink-step-card {{
        border: 1px solid #d0d7de;
        border-radius: 8px;
        background: #fff;
        overflow: hidden;
      }}
      .tink-step-card img {{
        display: block;
        width: 100%;
        max-height: 560px;
        object-fit: contain;
        background: #f6f8fa;
        border-bottom: 1px solid #d0d7de;
      }}
      .tink-step-meta {{
        padding: 10px 12px 12px;
      }}
      .tink-step-title {{
        margin: 0;
        font-weight: 600;
        font-size: 13px;
        line-height: 1.35;
      }}
      .tink-step-status {{
        display: inline-block;
        margin-bottom: 6px;
        padding: 2px 8px;
        border-radius: 999px;
        background: #dafbe1;
        color: #116329;
        font-size: 12px;
        font-weight: 600;
      }}
      .tink-step-status.failed {{
        background: #ffebe9;
        color: #cf222e;
      }}
    </style>
    <section class="tink-step-screenshots">
      <h2>Android Step Screenshots</h2>
      <p>Captured after each Appium-backed BDD step so the UI flow is visible directly in this report.</p>
      {''.join(sections)}
    </section>
    """


def _render_card(item: dict[str, Any]) -> str:
    status = html.escape(item["status"])
    status_class = "failed" if item["status"] != "passed" else ""
    return f"""
      <article class="tink-step-card">
        <img src="{html.escape(item["image"])}" alt="{html.escape(item["step"])}">
        <div class="tink-step-meta">
          <span class="tink-step-status {status_class}">{status}</span>
          <p class="tink-step-title">{item["index"]}. {html.escape(item["step"])}</p>
        </div>
      </article>
    """


if __name__ == "__main__":
    raise SystemExit(main())
