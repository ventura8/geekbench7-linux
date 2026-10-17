"""Cover download retry / redirect branches."""

from __future__ import annotations

import hashlib
import http.server
import threading
from pathlib import Path

import pytest

from geekbench7_linux.download import LOOPBACK_ENV, Policy, download_file
from geekbench7_linux.errors import DownloadFailed, IntegrityFailed
import geekbench7_linux.download as download_mod


class _FlakyHandler(http.server.BaseHTTPRequestHandler):
    hits = 0
    payload = b"retry-ok"

    def do_GET(self) -> None:
        type(self).hits += 1
        if type(self).hits < 2:
            self.send_response(503)
            self.end_headers()
            return
        body = type(self).payload
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def test_retry_then_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_FlakyHandler, "hits", 0)
    server = http.server.HTTPServer(("127.0.0.1", 0), _FlakyHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv(LOOPBACK_ENV, "1")
    monkeypatch.setattr(download_mod.time, "sleep", lambda _s: None)
    digest = hashlib.sha256(_FlakyHandler.payload).hexdigest()
    try:
        got = download_file(
            f"http://127.0.0.1:{server.server_address[1]}/f",
            tmp_path / "f.bin",
            expected_size=len(_FlakyHandler.payload),
            expected_sha256=digest,
            allowed_hosts=["127.0.0.1"],
            policy=Policy(allow_loopback_http=True),
        )
        assert got == digest
    finally:
        server.shutdown()


def test_loopback_policy_requires_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(LOOPBACK_ENV, raising=False)
    url = "http://127.0.0.1:1/x"
    dest = tmp_path / "x"
    bad_sha = "a" * 64
    hosts = ["127.0.0.1"]
    policy = Policy(allow_loopback_http=False)
    with pytest.raises(IntegrityFailed):
        download_file(url, dest, expected_size=1, expected_sha256=bad_sha, allowed_hosts=hosts, policy=policy)


class _Always500(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(500)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def test_exhaust_retries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    server = http.server.HTTPServer(("127.0.0.1", 0), _Always500)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv(LOOPBACK_ENV, "1")
    monkeypatch.setattr(download_mod.time, "sleep", lambda _s: None)
    url = f"http://127.0.0.1:{server.server_address[1]}/f"
    dest = tmp_path / "f.bin"
    bad_sha = "a" * 64
    hosts = ["127.0.0.1"]
    policy = Policy(allow_loopback_http=True)
    try:
        with pytest.raises(DownloadFailed):
            download_file(url, dest, expected_size=1, expected_sha256=bad_sha, allowed_hosts=hosts, policy=policy)
    finally:
        server.shutdown()
