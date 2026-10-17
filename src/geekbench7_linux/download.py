"""HTTPS downloads into the cache: exact size and streamed sha256.

Rules:

* Only ``https://`` URLs (loopback ``http://`` solely for tests with env gate).
* Redirects may never downgrade https to http.
* ``allowed_hosts`` is enforced on the initial URL.
* A size or sha256 mismatch deletes the partial file and raises IntegrityFailed.
* When the manifest pin has ``size == 0`` and a zero sha256, the download is
  trust-on-first-use: any positive size is accepted and the digest is returned
  for the caller to record (never used for production releases without pinning).
"""

from __future__ import annotations

import hashlib
import http.client
import logging
import os
import re
import time
import urllib.error
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .errors import DownloadFailed, IntegrityFailed
from .version import get_version

log = logging.getLogger(__name__)

PROJECT_URL = "https://github.com/ventura8/geekbench7-linux"
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
LOOPBACK_ENV = "GB_TEST_LOOPBACK_HTTP"
CHUNK_SIZE = 64 * 1024
ZERO_SHA256 = "0" * 64
_UA_VERSION = re.compile(r"[0-9A-Za-z.+_-]{1,64}")
# OSError covers ConnectionError, TimeoutError, and ssl.SSLError on Python 3.
_RETRYABLE = (http.client.HTTPException, OSError)


@dataclass(frozen=True)
class Policy:
    """Transport policy. Production code uses the defaults; only tests relax them."""

    allow_loopback_http: bool = False


DEFAULT_POLICY = Policy()


def user_agent() -> str:
    """``geekbench7-linux/<version> (+project URL)``."""
    version = str(get_version())
    if _UA_VERSION.fullmatch(version) is None:
        version = "0"
    return f"geekbench7-linux/{version} (+{PROJECT_URL})"


def _loopback_http_allowed(host: str, policy: Policy) -> bool:
    return policy.allow_loopback_http and host in LOOPBACK_HOSTS and os.environ.get(LOOPBACK_ENV) == "1"


def _url_malformed(parts: object, url: str) -> bool:
    host = getattr(parts, "hostname", None) or ""
    netloc = getattr(parts, "netloc", "")
    port = getattr(parts, "port", None)
    return (
        not host
        or "@" in netloc
        or port == 0
        or not url.isascii()
        or any(ch.isspace() or ord(ch) < 0x20 or ch == "\x7f" for ch in url)
    )


def check_url(url: str, policy: Policy = DEFAULT_POLICY, allowed_hosts: Iterable[str] | None = None) -> str:
    """Return the lowercase host of ``url``; raise IntegrityFailed if forbidden."""
    try:
        parts = urlsplit(url)
        _ = parts.port
    except ValueError:
        raise IntegrityFailed(f"refusing malformed URL {url!r}") from None
    if _url_malformed(parts, url):
        raise IntegrityFailed(f"refusing malformed URL {url!r}")
    host = parts.hostname or ""
    https_ok = parts.scheme == "https"
    http_ok = parts.scheme == "http" and _loopback_http_allowed(host, policy)
    if not (https_ok or http_ok):
        raise IntegrityFailed(
            f"refusing to download over {parts.scheme or 'an unknown scheme'}: {url}",
            hint="geekbench7-linux only downloads over https://",
        )
    if allowed_hosts is not None and host not in {h.lower() for h in allowed_hosts}:
        raise IntegrityFailed(
            f"refusing to download from {host}: it is not an allowed host for this file",
            hint="only the official download hosts listed in the runtime manifest are used",
        )
    return host


class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuse https→http downgrades on redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Wrap urllib redirect; reject scheme downgrade."""
        parts = urlsplit(str(newurl))
        if parts.scheme == "http" and urlsplit(req.full_url).scheme == "https":
            raise IntegrityFailed("refusing https to http redirect")
        return urllib.request.HTTPRedirectHandler.redirect_request(
            self, req, fp, code, msg, headers, newurl
        )


def _is_tofu(expected_size: int, expected_sha256: str) -> bool:
    return expected_size == 0 and expected_sha256.lower() == ZERO_SHA256


def _stream_to_part(resp: object, part: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    written = 0
    with part.open("wb") as out:
        while True:
            chunk = resp.read(CHUNK_SIZE)
            if not chunk:
                break
            out.write(chunk)
            digest.update(chunk)
            written += len(chunk)
    return digest.hexdigest(), written


def _classify_http_error(exc: urllib.error.HTTPError, url: str) -> DownloadFailed | None:
    """Return a DownloadFailed for 4xx; None means the caller should retry/re-raise."""
    if 400 <= exc.code < 500:
        return DownloadFailed(f"HTTP {exc.code} downloading {url}")
    return None


def _attempt_download(
    opener: urllib.request.OpenerDirector,
    request: urllib.request.Request,
    part: Path,
    url: str,
    timeout: float,
) -> tuple[str, int]:
    try:
        with opener.open(request, timeout=timeout) as resp:
            return _stream_to_part(resp, part)
    except urllib.error.HTTPError as exc:
        failed = _classify_http_error(exc, url)
        if failed is not None:
            raise failed from exc
        raise


def _verify_payload(
    part: Path,
    got: str,
    written: int,
    *,
    url: str,
    expected_size: int,
    expected_sha256: str,
    tofu: bool,
) -> None:
    if tofu:
        if written <= 0:
            part.unlink(missing_ok=True)
            raise IntegrityFailed(f"empty download from {url}")
        return
    if expected_size > 0 and written != expected_size:
        part.unlink(missing_ok=True)
        raise IntegrityFailed(f"size mismatch for {url}: got {written}, expected {expected_size}")
    if got != expected_sha256.lower():
        part.unlink(missing_ok=True)
        raise IntegrityFailed(f"sha256 mismatch for {url}")


def download_file(
    url: str,
    dest: Path,
    *,
    expected_size: int,
    expected_sha256: str,
    allowed_hosts: Iterable[str],
    policy: Policy = DEFAULT_POLICY,
    timeout: float = 60.0,
) -> str:
    """Download ``url`` to ``dest``; return the lowercase sha256 of the file."""
    check_url(url, policy=policy, allowed_hosts=allowed_hosts)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    if part.exists() or part.is_symlink():
        part.unlink()

    tofu = _is_tofu(expected_size, expected_sha256)
    opener = urllib.request.build_opener(SafeRedirectHandler())
    request = urllib.request.Request(url, headers={"User-Agent": user_agent()})
    last_error: OSError | urllib.error.URLError | http.client.HTTPException | None = None
    got = ""
    written = 0
    for attempt in range(5):
        try:
            got, written = _attempt_download(opener, request, part, url, timeout)
            break
        except DownloadFailed:
            raise
        # HTTPError is a URLError subclass — do not list it again (python:S5713).
        except (*_RETRYABLE, urllib.error.URLError) as exc:
            last_error = exc
        time.sleep(min(2**attempt, 8))
        if part.exists():
            part.unlink()
    else:
        raise DownloadFailed(f"download failed after retries: {last_error}")

    _verify_payload(
        part,
        got,
        written,
        url=url,
        expected_size=expected_size,
        expected_sha256=expected_sha256,
        tofu=tofu,
    )
    part.replace(dest)
    log.info("downloaded %s (%d bytes, sha256=%s)", dest.name, written, got)
    return got
