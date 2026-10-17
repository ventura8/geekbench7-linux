"""Download policy and integrity checks."""

from __future__ import annotations

import hashlib
import http.server
import threading
from pathlib import Path

import pytest

from geekbench7_linux.download import LOOPBACK_ENV, Policy, check_url, download_file
from geekbench7_linux.errors import IntegrityFailed


def test_check_url_https_ok() -> None:
    assert check_url("https://cdn.geekbench.com/x", allowed_hosts=["cdn.geekbench.com"]) == "cdn.geekbench.com"


def test_check_url_rejects_http() -> None:
    with pytest.raises(IntegrityFailed):
        check_url("http://cdn.geekbench.com/x", allowed_hosts=["cdn.geekbench.com"])


def test_check_url_rejects_host() -> None:
    with pytest.raises(IntegrityFailed):
        check_url("https://evil.example/x", allowed_hosts=["cdn.geekbench.com"])


class _PayloadHandler(http.server.BaseHTTPRequestHandler):
    payload = b"geekbench-test-payload"

    def do_GET(self) -> None:
        body = type(self).payload
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def test_loopback_download(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    payload = _PayloadHandler.payload
    digest = hashlib.sha256(payload).hexdigest()
    server = http.server.HTTPServer(("127.0.0.1", 0), _PayloadHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv(LOOPBACK_ENV, "1")
    dest = tmp_path / "out.bin"
    try:
        got = download_file(
            f"http://127.0.0.1:{server.server_address[1]}/file",
            dest,
            expected_size=len(payload),
            expected_sha256=digest,
            allowed_hosts=["127.0.0.1"],
            policy=Policy(allow_loopback_http=True),
        )
        assert got == digest
        assert dest.read_bytes() == payload
    finally:
        server.shutdown()


def test_sha_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    server = http.server.HTTPServer(("127.0.0.1", 0), _PayloadHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv(LOOPBACK_ENV, "1")
    dest = tmp_path / "out.bin"
    try:
        with pytest.raises(IntegrityFailed):
            download_file(
                f"http://127.0.0.1:{server.server_address[1]}/file",
                dest,
                expected_size=len(_PayloadHandler.payload),
                expected_sha256="a" * 64,
                allowed_hosts=["127.0.0.1"],
                policy=Policy(allow_loopback_http=True),
            )
    finally:
        server.shutdown()
