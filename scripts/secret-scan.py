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
_SKIP_PARTS = frozenset({".git", "__pycache__", "build", "artifacts"})


def _should_skip(path: Path) -> bool:
    return any(part in _SKIP_PARTS or part.startswith("build-") for part in path.parts)


def _file_hits(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return any(pattern.search(text) for pattern in PATTERNS)


def main() -> int:
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or _should_skip(path):
            continue
        if _file_hits(path):
            hits.append(str(path.relative_to(ROOT)))
    if hits:
        print("possible secrets:", file=sys.stderr)
        for hit in hits:
            print(f"  {hit}", file=sys.stderr)
        return 1
    print("secret-scan: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
