#!/usr/bin/env python3
"""Fail when the tree contains lint/coverage suppressions."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_ROOTS = (
    "src",
    "tests",
    "scripts",
    "packaging",
    "docker",
    "bin",
    "data",
    "debian",
    ".github",
)
SKIP_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    "build",
    "artifacts",
    "logs",
    ".cache",
}
PATTERNS = [
    re.compile(r"#\s*noqa\b"),
    re.compile(r"#\s*type:\s*ignore\b"),
    re.compile(r"#\s*pragma:\s*no cover\b"),
    re.compile(r"NOSONAR"),
    re.compile(r"NOLINT"),
    re.compile(r"#\s*shellcheck\s+disable\b"),
    re.compile(r"@pytest\.mark\.(skip|xfail)\b"),
    re.compile(r"exclude_lines\s*="),
    re.compile(r"per-file-ignores\s*="),
]
SELF = Path(__file__).resolve()
TEXT_SUFFIXES = {".py", ".sh", ".yml", ".yaml", ".toml", ".in", ".spec", ".bash", ".fish", ""}
TEXT_NAMES = {"Dockerfile", "Makefile"}


def _skip_dir(path: Path) -> bool:
    return any(part in SKIP_DIR_NAMES or part.startswith("build-") for part in path.parts)


def _is_scanned_file(path: Path) -> bool:
    if path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES:
        return True
    return "Dockerfile" in path.name


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or _skip_dir(path):
                continue
            if path.resolve() == SELF:
                continue
            if _is_scanned_file(path):
                files.append(path)
    return files


def _find_hits(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    for pattern in PATTERNS:
        if pattern.search(text):
            return f"{path.relative_to(ROOT)}: matched {pattern.pattern}"
    return None


def main() -> int:
    hits = [hit for hit in (_find_hits(path) for path in _iter_files()) if hit]
    if hits:
        print("suppressions found:", file=sys.stderr)
        for hit in hits:
            print(f"  {hit}", file=sys.stderr)
        return 1
    print("no-suppressions-lint: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
