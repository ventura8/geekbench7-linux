#!/usr/bin/env python3
"""Detect a newer Geekbench version on the download page vs the runtime manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "src" / "geekbench7_linux" / "data" / "runtime-manifest.json"
VERSION_RE = re.compile(r"Geekbench[- ](\d+\.\d+\.\d+)")


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def fetch_latest() -> str:
    """Scrape a version string from the Linux download page (informational only)."""
    url = "https://www.geekbench.com/download/linux/"
    req = urllib.request.Request(url, headers={"User-Agent": "geekbench7-linux-upstream-watch"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    matches = VERSION_RE.findall(body)
    if not matches:
        raise RuntimeError("could not find Geekbench version on download page")
    return max(matches, key=_version_key)


def pinned_version() -> str:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return str(data["arches"]["amd64"]["version"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-output", action="store_true")
    parser.add_argument("--add", metavar="VERSION", help="record placeholder pin (hashes via separate download step)")
    args = parser.parse_args()
    if args.add:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for arch in data["arches"]:
            data["arches"][arch]["version"] = args.add
            data["arches"][arch]["size"] = 0
            data["arches"][arch]["sha256"] = "0" * 64
        MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"updated manifest version to {args.add} (TOFU hashes; fill after verified download)")
        return 0
    try:
        current = pinned_version()
        latest = fetch_latest()
    except (OSError, urllib.error.URLError, json.JSONDecodeError, KeyError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    newer = latest != current and _version_key(latest) > _version_key(current)
    if args.github_output:
        print(f"new={'true' if newer else 'false'}")
        print(f"version={latest}")
        print(f"current={current}")
    else:
        print(json.dumps({"current": current, "latest": latest, "new": newer}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
