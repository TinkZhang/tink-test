from __future__ import annotations

import json
import threading
from datetime import UTC, date, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


class TimeMockServer:
    def __init__(self, fixture_path: str | Path, host: str = "127.0.0.1", port: int = 8765):
        self.fixture_path = Path(fixture_path)
        self.host = host
        self.port = port
        self.rows = self._load_rows()
        self.labels: list[dict[str, Any]] = []
        self.force_error = False
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def start(self) -> None:
        mock = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if mock.force_error:
                    self._send_json({"error": "mock time failure"}, HTTPStatus.INTERNAL_SERVER_ERROR)
                    return

                path = self._normalized_path()
                if path == "/time":
                    self._send_json(mock.rows)
                    return
                if path == "/time/statistics":
                    self._send_json(mock._statistics())
                    return
                if path == "/time/labels":
                    self._send_json(mock.labels)
                    return
                self.send_error(HTTPStatus.NOT_FOUND)

            def do_POST(self) -> None:
                if mock.force_error:
                    self._send_json({"error": "mock time failure"}, HTTPStatus.INTERNAL_SERVER_ERROR)
                    return

                path = self._normalized_path()
                payload = self._read_json()
                if path == "/time":
                    next_id = max([row["id"] for row in mock.rows], default=0) + 1
                    row = {
                        "id": next_id,
                        "type": int(payload["type"]),
                        "start": payload["start"],
                        "end": payload["end"],
                        "duration": _duration_minutes(payload["start"], payload["end"]),
                        "title": payload["title"],
                        "description": payload.get("description") or "",
                        "google_calendar_event_id": f"mock-gcal-{next_id}",
                    }
                    mock.rows.insert(0, row)
                    self._send_json(row, HTTPStatus.CREATED)
                    return
                if path == "/time/labels":
                    next_id = max([row["id"] for row in mock.labels], default=0) + 1
                    row = {
                        "id": next_id,
                        "type": int(payload["type"]),
                        "name": str(payload["name"]).strip(),
                        "sort_order": int(payload.get("sort_order") or 0),
                    }
                    mock.labels.append(row)
                    self._send_json(row, HTTPStatus.CREATED)
                    return
                self.send_error(HTTPStatus.NOT_FOUND)

            def do_PATCH(self) -> None:
                if mock.force_error:
                    self._send_json({"error": "mock time failure"}, HTTPStatus.INTERNAL_SERVER_ERROR)
                    return
                path = self._normalized_path()
                if not path.startswith("/time/labels/"):
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                label_id = int(path.rsplit("/", 1)[1])
                payload = self._read_json()
                for label in mock.labels:
                    if label["id"] == label_id:
                        if "type" in payload and payload["type"] is not None:
                            label["type"] = int(payload["type"])
                        if "name" in payload and payload["name"] is not None:
                            label["name"] = str(payload["name"]).strip()
                        if "sort_order" in payload and payload["sort_order"] is not None:
                            label["sort_order"] = int(payload["sort_order"])
                        self._send_json(label)
                        return
                self.send_error(HTTPStatus.NOT_FOUND)

            def do_DELETE(self) -> None:
                if mock.force_error:
                    self._send_json({"error": "mock time failure"}, HTTPStatus.INTERNAL_SERVER_ERROR)
                    return

                path = self._normalized_path()
                if path.startswith("/time/labels/"):
                    label_id = int(path.rsplit("/", 1)[1])
                    mock.labels = [row for row in mock.labels if row["id"] != label_id]
                    self.send_response(HTTPStatus.NO_CONTENT)
                    self.end_headers()
                    return
                if path.startswith("/time/"):
                    time_id = int(path.rsplit("/", 1)[1])
                    mock.rows = [row for row in mock.rows if row["id"] != time_id]
                    self.send_response(HTTPStatus.NO_CONTENT)
                    self.end_headers()
                    return
                self.send_error(HTTPStatus.NOT_FOUND)

            def log_message(self, _format: str, *_args: Any) -> None:
                return

            def _normalized_path(self) -> str:
                path = self.path.split("?", 1)[0]
                return path.removeprefix("/dev").rstrip("/") or "/"

            def _read_json(self) -> Any:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length) if length else b"{}"
                return json.loads(raw.decode("utf-8"))

            def _send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self._server = ThreadingHTTPServer((self.host, self.port), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._thread:
            self._thread.join(timeout=5)

    def reset(self, fixture_path: str | Path | None = None) -> None:
        if fixture_path is not None:
            self.fixture_path = Path(fixture_path)
        self.rows = self._load_rows()
        self.labels = []
        self.force_error = False

    def _load_rows(self) -> list[dict[str, Any]]:
        with self.fixture_path.open(encoding="utf-8") as fixture:
            payload = json.load(fixture)
        today = date.today().isoformat()
        rows = []
        for row in payload:
            next_row = dict(row)
            next_row["start"] = str(next_row["start"]).replace("{today}", today)
            next_row["end"] = str(next_row["end"]).replace("{today}", today)
            next_row["duration"] = int(next_row.get("duration") or _duration_minutes(next_row["start"], next_row["end"]))
            rows.append(next_row)
        return rows

    def _statistics(self) -> list[dict[str, int]]:
        totals = {type_id: 0 for type_id in range(1, 12)}
        for row in self.rows:
            totals[int(row["type"])] += int(row.get("duration") or 0)
        return [{"type": type_id, "duration": duration} for type_id, duration in totals.items()]


def _duration_minutes(start: str, end: str) -> int:
    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
    return max(0, int((end_dt - start_dt).total_seconds() // 60))
