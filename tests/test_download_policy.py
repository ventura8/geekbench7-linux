"""Download policy corners: UA sanitise, redirects, malformed URLs."""

from __future__ import annotations

from pathlib import Path
from urllib.request import Request

import pytest

import geekbench7_linux.download as download_mod
from geekbench7_linux.download import (
    LOOPBACK_ENV,
    Policy,
    SafeRedirectHandler,
    check_url,
    download_file,
    user_agent,
)
from geekbench7_linux.errors import IntegrityFailed


def test_user_agent_sanitises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(download_mod, "get_version", lambda: "bad version!")
    assert user_agent().startswith("geekbench7-linux/0 ")


def test_user_agent_bad_chars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(download_mod, "get_version", lambda: "!!!")
    ua = user_agent()
    assert ua.startswith("geekbench7-linux/0 ")


def test_url_with_userinfo() -> None:
    with pytest.raises(IntegrityFailed):
        check_url("https://user:pass@cdn.geekbench.com/x", allowed_hosts=["cdn.geekbench.com"])


def test_url_with_space() -> None:
    with pytest.raises(IntegrityFailed):
        check_url("https://cdn.geekbench.com/x y", allowed_hosts=["cdn.geekbench.com"])


def test_redirect_downgrade() -> None:
    handler = SafeRedirectHandler()
    req = Request("https://cdn.geekbench.com/x")
    with pytest.raises(IntegrityFailed):
        handler.redirect_request(req, None, 302, "Found", {}, "http://cdn.geekbench.com/y")


def test_https_to_http_blocked_in_download(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Unit-level redirect handler already covered; ensure loopback http without env fails.
    monkeypatch.delenv(LOOPBACK_ENV, raising=False)
    with pytest.raises(IntegrityFailed):
        download_file(
            "http://127.0.0.1:9/x",
            tmp_path / "x",
            expected_size=0,
            expected_sha256="0" * 64,
            allowed_hosts=["127.0.0.1"],
            policy=Policy(allow_loopback_http=True),
        )
