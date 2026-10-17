#!/usr/bin/env python3
"""Refuse obvious secrets in the source tree."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = [
    re.compile(r"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
]


def main() -> int:
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        skip_parts = {".git", "__pycache__", "build", "artifacts"}
        if any(part in skip_parts or part.startswith("build-") for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for pattern in PATTERNS:
            if pattern.search(text):
                hits.append(str(path.relative_to(ROOT)))
                break
    if hits:
        print("possible secrets:", file=sys.stderr)
        for hit in hits:
            print(f"  {hit}", file=sys.stderr)
        return 1
    print("secret-scan: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
