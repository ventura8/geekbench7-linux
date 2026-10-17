"""Extra download edge cases for coverage."""

from __future__ import annotations

import hashlib
import http.server
import threading
from pathlib import Path

import pytest

from geekbench7_linux.download import LOOPBACK_ENV, Policy, check_url, download_file, user_agent
from geekbench7_linux.errors import DownloadFailed, IntegrityFailed


def test_user_agent_contains_project() -> None:
    assert "geekbench7-linux/" in user_agent()
    assert "github.com" in user_agent()


def test_malformed_url() -> None:
    with pytest.raises(IntegrityFailed):
        check_url("https://")
    with pytest.raises(IntegrityFailed):
        check_url("ftp://cdn.geekbench.com/x")


class _BoomHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def test_http_404(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    server = http.server.HTTPServer(("127.0.0.1", 0), _BoomHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv(LOOPBACK_ENV, "1")
    try:
        with pytest.raises(DownloadFailed):
            download_file(
                f"http://127.0.0.1:{server.server_address[1]}/missing",
                tmp_path / "x.bin",
                expected_size=1,
                expected_sha256="a" * 64,
                allowed_hosts=["127.0.0.1"],
                policy=Policy(allow_loopback_http=True),
            )
    finally:
        server.shutdown()


class _EmptyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def test_tofu_empty_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    server = http.server.HTTPServer(("127.0.0.1", 0), _EmptyHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv(LOOPBACK_ENV, "1")
    try:
        with pytest.raises(IntegrityFailed):
            download_file(
                f"http://127.0.0.1:{server.server_address[1]}/empty",
                tmp_path / "empty.bin",
                expected_size=0,
                expected_sha256="0" * 64,
                allowed_hosts=["127.0.0.1"],
                policy=Policy(allow_loopback_http=True),
            )
    finally:
        server.shutdown()


class _OkHandler(http.server.BaseHTTPRequestHandler):
    payload = b"abc"

    def do_GET(self) -> None:
        body = type(self).payload
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def test_size_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    server = http.server.HTTPServer(("127.0.0.1", 0), _OkHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv(LOOPBACK_ENV, "1")
    digest = hashlib.sha256(_OkHandler.payload).hexdigest()
    try:
        with pytest.raises(IntegrityFailed):
            download_file(
                f"http://127.0.0.1:{server.server_address[1]}/f",
                tmp_path / "f.bin",
                expected_size=999,
                expected_sha256=digest,
                allowed_hosts=["127.0.0.1"],
                policy=Policy(allow_loopback_http=True),
            )
    finally:
        server.shutdown()
