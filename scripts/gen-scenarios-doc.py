#!/usr/bin/env python3
"""Validate or regenerate docs/qa/E2E-SCENARIOS.md from tests/e2e/scenarios.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "tests" / "e2e" / "scenarios.json"
DOC = ROOT / "docs" / "qa" / "E2E-SCENARIOS.md"


def render(data: dict) -> str:
    lines = [
        "# E2E scenarios",
        "",
        "Generated from `tests/e2e/scenarios.json`. Do not invent rows.",
        "",
        "| ID | Title | Gate |",
        "|----|-------|------|",
    ]
    for item in data["scenarios"]:
        lines.append(f"| {item['id']} | {item['title']} | `{item['gate']}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("check", "write", "validate"))
    args = parser.parse_args()
    data = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    text = render(data)
    if args.action in {"write"}:
        DOC.parent.mkdir(parents=True, exist_ok=True)
        DOC.write_text(text, encoding="utf-8")
        print(f"wrote {DOC}")
        return 0
    if not DOC.is_file():
        print(f"missing {DOC}", file=sys.stderr)
        return 1
    if DOC.read_text(encoding="utf-8") != text:
        print(f"{DOC} is out of date; run: python3 scripts/gen-scenarios-doc.py write", file=sys.stderr)
        return 1
    print("scenarios doc ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
