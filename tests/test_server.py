from http.client import HTTPConnection
import json

import pytest

from otpigeon.server import BridgeServer, MAX_BODY_BYTES, is_allowed_client_ipv4


TOKEN = "test-token-with-enough-length"


@pytest.fixture
def running_server():
    copied: list[str] = []
    server = BridgeServer(
        "127.0.0.1",
        0,
        token_provider=lambda: TOKEN,
        clipboard_writer=copied.append,
    )
    server.start()
    try:
        yield server, copied
    finally:
        server.stop()


def request(server: BridgeServer, method: str, path: str, body=None, headers=None):
    connection = HTTPConnection("127.0.0.1", server.port, timeout=2)
    connection.request(method, path, body=body, headers=headers or {})
    response = connection.getresponse()
    data = response.read().decode("utf-8")
    connection.close()
    return response.status, data


def post_json(server: BridgeServer, path: str, payload: object):
    return request(
        server,
        "POST",
        path,
        body=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )


def test_health(running_server) -> None:
    server, _ = running_server
    assert request(server, "GET", "/health") == (200, "OTPigeon OK")


def test_only_loopback_and_rfc1918_clients_are_allowed() -> None:
    assert is_allowed_client_ipv4("127.0.0.1")
    assert is_allowed_client_ipv4("192.168.137.2")
    assert is_allowed_client_ipv4("10.0.0.9")
    assert not is_allowed_client_ipv4("169.254.1.2")
    assert not is_allowed_client_ipv4("198.51.100.7")
    assert not is_allowed_client_ipv4("not-an-address")


def test_check_validates_token_without_touching_clipboard(running_server) -> None:
    server, copied = running_server
    assert post_json(server, "/check", {"token": TOKEN}) == (200, "OK")
    assert copied == []


def test_otp_is_extracted_and_copied(running_server) -> None:
    server, copied = running_server
    status, body = post_json(
        server,
        "/otp",
        {"token": TOKEN, "text": "您的验证码是 123456"},
    )
    assert (status, body) == (200, "OK")
    assert copied == ["123456"]


def test_wrong_token_is_rejected(running_server) -> None:
    server, copied = running_server
    status, body = post_json(
        server,
        "/otp",
        {"token": "wrong", "text": "验证码 123456"},
    )
    assert (status, body) == (403, "Invalid token")
    assert copied == []


def test_ambiguous_message_returns_422(running_server) -> None:
    server, copied = running_server
    status, body = post_json(
        server,
        "/otp",
        {"token": TOKEN, "text": "订单 123456，金额 7788"},
    )
    assert (status, body) == (422, "OTP not found")
    assert copied == []


def test_invalid_content_type_returns_415(running_server) -> None:
    server, _ = running_server
    assert request(server, "POST", "/check", body="{}") == (
        415,
        "Content-Type must be application/json",
    )


def test_invalid_json_returns_400(running_server) -> None:
    server, _ = running_server
    assert request(
        server,
        "POST",
        "/check",
        body="{broken",
        headers={"Content-Type": "application/json"},
    ) == (400, "Invalid JSON")


def test_oversized_body_returns_413(running_server) -> None:
    server, _ = running_server
    body = "x" * (MAX_BODY_BYTES + 1)
    assert request(
        server,
        "POST",
        "/check",
        body=body,
        headers={"Content-Type": "application/json"},
    ) == (413, "Request body too large")
