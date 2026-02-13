from __future__ import annotations

import json
import threading
from collections import deque
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from jane.actions import ActionExecutor
from jane.commands import ParsedCommand, parse_command

BASE_DIR = Path(__file__).resolve().parent


class JaneWebState:
    def __init__(self) -> None:
        self.logs: deque[str] = deque(maxlen=300)
        self.pending: deque[ParsedCommand] = deque()
        self._lock = threading.Lock()
        self.executor = ActionExecutor(self._speak)
        self._log("[BOOT] JANE Web is online.")
        self._speak("Hello, I am JANE. Ready on the web dashboard.")

    def _log(self, msg: str) -> None:
        with self._lock:
            self.logs.append(msg)

    def _speak(self, text: str) -> None:
        self._log(f"JANE: {text}")

    def process(self, text: str) -> dict:
        self._log(f"You: {text}")
        parsed = parse_command(text)
        if parsed.action == "empty":
            return {"status": "ignored", "message": "Empty command."}

        if parsed.high_risk:
            with self._lock:
                self.pending.append(parsed)
            self._speak(f"High-risk command queued: {parsed.raw}")
            return {
                "status": "queued",
                "message": "High-risk command is waiting for approval.",
                "parsed": asdict(parsed),
            }

        result = self.executor.execute(parsed)
        self._speak(result.message)
        return {
            "status": "executed" if result.ok else "failed",
            "message": result.message,
            "parsed": asdict(parsed),
        }

    def approve(self) -> tuple[int, dict]:
        with self._lock:
            if not self.pending:
                return HTTPStatus.NOT_FOUND, {"detail": "No pending high-risk command."}
            command = self.pending.popleft()

        self._log(f"[APPROVED] {command.raw}")
        result = self.executor.execute(command)
        self._speak(result.message)
        return HTTPStatus.OK, {"status": "executed" if result.ok else "failed", "message": result.message}

    def deny(self) -> tuple[int, dict]:
        with self._lock:
            if not self.pending:
                return HTTPStatus.NOT_FOUND, {"detail": "No pending high-risk command."}
            command = self.pending.popleft()

        msg = f"Denied: {command.raw}"
        self._speak(msg)
        return HTTPStatus.OK, {"status": "denied", "message": msg}

    def snapshot(self) -> dict:
        with self._lock:
            pending = [asdict(c) for c in self.pending]
            logs = list(self.logs)
        return {
            "name": "JANE",
            "deployed_by": "Visrodeck Technology",
            "pending": pending,
            "logs": logs,
        }


class JaneRequestHandler(BaseHTTPRequestHandler):
    state = JaneWebState()

    def _send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/":
            self._send_file(BASE_DIR / "templates" / "index.html", "text/html; charset=utf-8")
            return
        if route == "/api/state":
            self._send_json(self.state.snapshot())
            return
        if route == "/static/style.css":
            self._send_file(BASE_DIR / "static" / "style.css", "text/css; charset=utf-8")
            return
        if route == "/static/app.js":
            self._send_file(BASE_DIR / "static" / "app.js", "application/javascript; charset=utf-8")
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self):
        route = urlparse(self.path).path
        if route == "/api/command":
            payload = self._read_json_body()
            text = str(payload.get("text", ""))
            self._send_json(self.state.process(text))
            return
        if route == "/api/approve":
            status, payload = self.state.approve()
            self._send_json(payload, status)
            return
        if route == "/api/deny":
            status, payload = self.state.deny()
            self._send_json(payload, status)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def log_message(self, fmt: str, *args):
        return


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), JaneRequestHandler)
    print(f"JANE Web running on http://{host}:{port}")
    server.serve_forever()
