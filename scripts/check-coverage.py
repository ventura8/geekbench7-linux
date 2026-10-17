#!/usr/bin/env python3
"""Per-file coverage gate aligned with SonarQube.

Scores each file the way Sonar does:
  (covered_lines + covered_conditions) / (lines_to_cover + conditions)
Overall and every measured ``src/geekbench7_linux/**/*.py`` file must be >= --min
(default 90). Scripts/bin are excluded via sonar.coverage.exclusions.

Exit: 0 pass, 1 gate failed, 2 bad input.
"""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROPS = ROOT / "sonar-project.properties"
DEFAULT_XML = ROOT / "artifacts" / "coverage" / "coverage.xml"


def _parse_properties(text: str) -> dict[str, str]:
    props: dict[str, str] = {}
    pending = ""
    for raw in text.splitlines():
        line = raw.strip()
        if pending:
            if line.endswith("\\"):
                pending += line[:-1].strip()
                continue
            line = pending + line
            pending = ""
        elif not line or line.startswith("#") or line.startswith("!"):
            continue
        elif line.endswith("\\"):
            pending = line[:-1].strip()
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            props[key.strip()] = value.strip()
    return props


def _split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _wildcard_to_re(pattern: str) -> re.Pattern[str]:
    pattern = pattern.strip().replace("\\", "/")
    if pattern.endswith("/"):
        pattern += "**"
    out: list[str] = ["^"]
    i = 1 if pattern.startswith("/") else 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/|)")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    out.append("$")
    return re.compile("".join(out))


def _excluded(path: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(p.match(path.replace("\\", "/")) for p in patterns)


def _file_score(cls: ET.Element) -> tuple[float, int, int]:
    """Return (percent, covered_units, total_units) using Sonar's combined metric."""
    lines_covered = 0
    lines_valid = 0
    cond_covered = 0
    cond_valid = 0
    for line in cls.findall("lines/line"):
        hits = int(line.attrib.get("hits", "0"))
        lines_valid += 1
        if hits > 0:
            lines_covered += 1
        if line.attrib.get("branch") == "true":
            raw = line.attrib.get("condition-coverage", "")
            match = re.search(r"\((\d+)/(\d+)\)", raw)
            if match:
                cond_covered += int(match.group(1))
                cond_valid += int(match.group(2))
    total = lines_valid + cond_valid
    covered = lines_covered + cond_covered
    if total == 0:
        return 100.0, 0, 0
    return (covered / total) * 100.0, covered, total


def _repo_relative(filename: str) -> str:
    name = filename.replace("\\", "/")
    if "src/geekbench7_linux/" in name:
        return name[name.index("src/geekbench7_linux/") :]
    if name.startswith("geekbench7_linux/"):
        return "src/" + name
    # Sonar-oriented Cobertura paths are relative to src/geekbench7_linux/.
    if name.endswith(".py") and not name.startswith("/"):
        return f"src/geekbench7_linux/{name}"
    return name


def _load_exclusions(properties: Path) -> list[re.Pattern[str]]:
    if not properties.is_file():
        return []
    props = _parse_properties(properties.read_text(encoding="utf-8"))
    return [_wildcard_to_re(item) for item in _split_list(props.get("sonar.coverage.exclusions", ""))]


def _measure_classes(
    root: ET.Element, exclusions: list[re.Pattern[str]], floor: float
) -> tuple[list[str], int, int, int]:
    failed: list[str] = []
    total_covered = 0
    total_units = 0
    measured = 0
    for cls in root.findall(".//class"):
        filename = cls.attrib.get("filename", "").replace("\\", "/")
        if not filename.endswith(".py"):
            continue
        rel = _repo_relative(filename)
        if "geekbench7_linux" not in rel:
            continue
        if _excluded(rel, exclusions) or _excluded(filename, exclusions):
            continue
        if "/tests/" in f"/{rel}/":
            continue
        percent, covered, total = _file_score(cls)
        if total == 0:
            continue
        measured += 1
        total_covered += covered
        total_units += total
        if percent < floor:
            failed.append(f"{rel}: {percent:.1f}% < {floor}%")
    return failed, total_covered, total_units, measured


def _resolve_under_repo(path: Path) -> Path:
    """Refuse CLI paths that escape the repository root."""
    resolved = path.expanduser().resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        print(f"error: refusing path outside repository: {resolved}", file=sys.stderr)
        raise SystemExit(2)
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml", type=Path, default=DEFAULT_XML)
    parser.add_argument("--properties", type=Path, default=DEFAULT_PROPS)
    parser.add_argument("--min", type=float, default=90.0)
    parser.add_argument("--min-python-line", type=float, default=90.0)
    parser.add_argument("--min-python-branch", type=float, default=90.0)
    args = parser.parse_args()

    xml_path = _resolve_under_repo(args.xml)
    props_path = _resolve_under_repo(args.properties)
    if not xml_path.is_file():
        print(f"error: missing coverage xml: {xml_path}", file=sys.stderr)
        return 2

    floor = min(args.min, args.min_python_line, args.min_python_branch)
    exclusions = _load_exclusions(props_path)
    failed, total_covered, total_units, measured = _measure_classes(
        ET.parse(xml_path).getroot(), exclusions, floor
    )
    if total_units == 0:
        print("error: no measurable Python files in coverage report", file=sys.stderr)
        return 2
    overall = (total_covered / total_units) * 100.0
    if overall < args.min:
        failed.append(f"OVERALL: {overall:.1f}%")
        print(f"overall coverage {overall:.1f}% < {args.min}%", file=sys.stderr)
    if failed:
        print("coverage gate failed:", file=sys.stderr)
        for item in failed:
            print(f"  {item}", file=sys.stderr)
        return 1
    print(f"coverage ok: overall {overall:.1f}% ({measured} files, min {args.min}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
