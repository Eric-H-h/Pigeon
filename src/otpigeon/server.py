from __future__ import annotations

from dataclasses import dataclass
from hmac import compare_digest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from typing import Callable
from urllib.parse import urlsplit

from .network import is_supported_private_ipv4
from .otp import extract_otp


MAX_BODY_BYTES = 16 * 1024
MAX_DISCARD_BYTES = 32 * 1024
MAX_TEXT_CHARS = 8192


@dataclass(frozen=True, slots=True)
class BridgeEvent:
    kind: str
    message: str


class _RequestError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


class _BridgeHttpServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def is_allowed_client_ipv4(address: str) -> bool:
    """Allow only this PC and RFC1918 peers even though the socket binds broadly."""
    return address.startswith("127.") or is_supported_private_ipv4(address)


class BridgeServer:
    def __init__(
        self,
        host: str,
        port: int,
        token_provider: Callable[[], str],
        clipboard_writer: Callable[[str], None],
        event_sink: Callable[[BridgeEvent], None] | None = None,
    ) -> None:
        self._host = host
        self._requested_port = port
        self._token_provider = token_provider
        self._clipboard_writer = clipboard_writer
        self._event_sink = event_sink
        self._httpd: _BridgeHttpServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def port(self) -> int:
        if self._httpd:
            return int(self._httpd.server_address[1])
        return self._requested_port

    @property
    def running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def start(self) -> None:
        if self.running:
            return
        self._httpd = _BridgeHttpServer(
            (self._host, self._requested_port), self._make_handler()
        )
        self._thread = threading.Thread(
            target=self._httpd.serve_forever,
            kwargs={"poll_interval": 0.2},
            name="otpigeon-http",
            daemon=True,
        )
        self._thread.start()
        self._emit("server_started", f"Listening on port {self.port}")

    def stop(self) -> None:
        httpd = self._httpd
        thread = self._thread
        if httpd:
            httpd.shutdown()
            httpd.server_close()
        if thread and thread is not threading.current_thread():
            thread.join(timeout=2.0)
        self._httpd = None
        self._thread = None
        self._emit("server_stopped", "Server stopped")

    def _make_handler(self) -> type[BaseHTTPRequestHandler]:
        bridge = self

        class Handler(BaseHTTPRequestHandler):
            server_version = "OTPigeon"
            sys_version = ""

            def setup(self) -> None:
                super().setup()
                self.connection.settimeout(5.0)

            def do_GET(self) -> None:
                if not self._client_is_allowed():
                    self._send_text(403, "Private network clients only")
                    return
                if urlsplit(self.path).path == "/health":
                    self._send_text(200, "OTPigeon OK")
                else:
                    self._send_text(404, "Not Found")

            def do_POST(self) -> None:
                if not self._client_is_allowed():
                    bridge._emit("client_rejected", "Request rejected: public client")
                    self._send_text(403, "Private network clients only")
                    return
                path = urlsplit(self.path).path
                if path not in {"/check", "/otp"}:
                    self._send_text(404, "Not Found")
                    return

                try:
                    body = self._read_json_object()
                    provided_token = body.get("token")
                    expected_token = bridge._token_provider()
                    if (
                        not isinstance(provided_token, str)
                        or not compare_digest(provided_token, expected_token)
                    ):
                        bridge._emit("auth_failed", "Request rejected: invalid token")
                        raise _RequestError(403, "Invalid token")

                    if path == "/check":
                        bridge._emit("check_ok", "iPhone connection check succeeded")
                        self._send_text(200, "OK")
                        return

                    text = body.get("text")
                    if not isinstance(text, str):
                        raise _RequestError(400, "Field 'text' must be a string")
                    if len(text) > MAX_TEXT_CHARS:
                        raise _RequestError(413, "Text too large")

                    otp = extract_otp(text)
                    if not otp:
                        bridge._emit("otp_not_found", "Message received; OTP not found")
                        raise _RequestError(422, "OTP not found")

                    bridge._clipboard_writer(otp)
                    masked = otp[0] + "*" * (len(otp) - 2) + otp[-1]
                    bridge._emit("otp_copied", f"OTP copied: {masked}")
                    self._send_text(200, "OK")
                except _RequestError as exc:
                    self._send_text(exc.status, exc.message)
                except Exception as exc:
                    bridge._emit("server_error", f"Request failed: {type(exc).__name__}")
                    self._send_text(500, "Internal Server Error")

            def _read_json_object(self) -> dict[str, object]:
                content_type = self.headers.get("Content-Type", "")
                media_type = content_type.partition(";")[0].strip().lower()
                if media_type != "application/json":
                    raise _RequestError(415, "Content-Type must be application/json")

                raw_length = self.headers.get("Content-Length")
                if raw_length is None:
                    raise _RequestError(400, "Content-Length required")
                try:
                    length = int(raw_length)
                except ValueError as exc:
                    raise _RequestError(400, "Invalid Content-Length") from exc
                if length <= 0:
                    raise _RequestError(400, "Empty request body")
                if length > MAX_BODY_BYTES:
                    # On Windows, closing a socket with a small unread request body can
                    # turn the intended 413 response into WSAECONNABORTED for the client.
                    # Drain only a bounded overage; never allocate from Content-Length.
                    if length <= MAX_DISCARD_BYTES:
                        remaining = length
                        while remaining:
                            chunk = self.rfile.read(min(remaining, 4096))
                            if not chunk:
                                break
                            remaining -= len(chunk)
                    raise _RequestError(413, "Request body too large")

                try:
                    body = json.loads(self.rfile.read(length).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise _RequestError(400, "Invalid JSON") from exc
                if not isinstance(body, dict):
                    raise _RequestError(400, "JSON root must be an object")
                return body

            def _send_text(self, status: int, text: str) -> None:
                data = text.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(data)

            def _client_is_allowed(self) -> bool:
                return is_allowed_client_ipv4(str(self.client_address[0]))

            def log_message(self, format: str, *args: object) -> None:
                return

        return Handler

    def _emit(self, kind: str, message: str) -> None:
        if not self._event_sink:
            return
        try:
            self._event_sink(BridgeEvent(kind, message))
        except Exception:
            pass
