from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


class WeightMockServer:
    def __init__(self, fixture_path: str | Path, host: str = "127.0.0.1", port: int = 8765):
        self.fixture_path = Path(fixture_path)
        self.host = host
        self.port = port
        self.rows = self._load_rows()
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
                    self._send_json({"error": "mock weight failure"}, HTTPStatus.INTERNAL_SERVER_ERROR)
                    return
                if self._normalized_path() == "/weight":
                    self._send_json(mock.rows)
                    return
                self.send_error(HTTPStatus.NOT_FOUND)

            def do_POST(self) -> None:
                if mock.force_error:
                    self._send_json({"error": "mock weight failure"}, HTTPStatus.INTERNAL_SERVER_ERROR)
                    return
                if self._normalized_path() != "/weight":
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return

                payload = self._read_json()
                next_id = max([row["id"] for row in mock.rows], default=0) + 1
                row = {
                    "id": next_id,
                    "weight": float(payload["weight"]),
                    "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                }
                mock.rows.insert(0, row)
                self._send_json(row, HTTPStatus.CREATED)

            def do_DELETE(self) -> None:
                if mock.force_error:
                    self._send_json({"error": "mock weight failure"}, HTTPStatus.INTERNAL_SERVER_ERROR)
                    return
                path = self._normalized_path()
                if not path.startswith("/weight/"):
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                weight_id = int(path.rsplit("/", 1)[1])
                mock.rows = [row for row in mock.rows if row["id"] != weight_id]
                self.send_response(HTTPStatus.NO_CONTENT)
                self.end_headers()

            def log_message(self, _format: str, *_args: Any) -> None:
                return

            def _normalized_path(self) -> str:
                path = self.path.split("?", 1)[0]
                return path.removeprefix("/dev")

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
        self.force_error = False

    def _load_rows(self) -> list[dict[str, Any]]:
        with self.fixture_path.open(encoding="utf-8") as fixture:
            return json.load(fixture)
