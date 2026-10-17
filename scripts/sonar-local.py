#!/usr/bin/env python3
"""Local Sonar-style gates without uploading: complexity + duplication.

usage: scripts/sonar-local.py [--max-complexity N]

Scans src/geekbench7_linux and scripts (Python). Exit 0 clean, 1 findings, 2 bad input.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_COMPLEXITY = 15
MIN_LINES = 10
MIN_TOKENS = 100
_TOKEN = re.compile(r"\w+|[^\w\s]")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}: {self.message}"


def _py_files() -> list[Path]:
    """Only the package Sonar measures (sonar.sources)."""
    base = ROOT / "src" / "geekbench7_linux"
    files: list[Path] = []
    for path in base.rglob("*.py"):
        if any(part.startswith(".") or part == "__pycache__" for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def _complexity(node: ast.AST) -> int:
    """Sonar-ish cognitive complexity for a function body."""

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.score = 0
            self.nesting = 0

        def _bump(self, extra: int = 0) -> None:
            self.score += 1 + self.nesting + extra

        def visit_If(self, node: ast.If) -> None:
            self._bump()
            self.nesting += 1
            for child in node.body:
                self.visit(child)
            self.nesting -= 1
            for i, handler in enumerate(node.orelse):
                if i == 0 and isinstance(handler, ast.If):
                    self.score += 1  # elif
                    self.visit(handler)
                else:
                    if node.orelse:
                        self.score += 1  # else
                    self.nesting += 1
                    for child in node.orelse:
                        self.visit(child)
                    self.nesting -= 1
                    break

        def _visit_nested_block(self, node: ast.AST) -> None:
            self._bump()
            self.nesting += 1
            self.generic_visit(node)
            self.nesting -= 1

        def visit_For(self, node: ast.For) -> None:
            self._visit_nested_block(node)

        def visit_While(self, node: ast.While) -> None:
            self._visit_nested_block(node)

        def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
            self._visit_nested_block(node)

        def visit_BoolOp(self, node: ast.BoolOp) -> None:
            self.score += max(0, len(node.values) - 1)
            self.generic_visit(node)

        def visit_comprehension(self, node: ast.comprehension) -> None:
            self._bump()
            self.generic_visit(node)

    visitor = Visitor()
    for child in ast.iter_child_nodes(node):
        visitor.visit(child)
    return visitor.score


def check_complexity(max_complexity: int) -> list[Finding]:
    findings: list[Finding] = []
    for path in _py_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                score = _complexity(node)
                if score > max_complexity:
                    rel = path.relative_to(ROOT).as_posix()
                    findings.append(
                        Finding(
                            rel,
                            getattr(node, "lineno", 1),
                            "python:S3776",
                            f"Refactor this function to reduce its Cognitive Complexity from {score} "
                            f"to the {max_complexity} allowed.",
                        )
                    )
    return findings


def _normalised_lines(path: Path) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        rows.append((i, " ".join(stripped.split())))
    return rows


def check_duplication() -> list[Finding]:
    """Simple CPD-like duplicate block detector."""
    blocks: dict[str, list[tuple[str, int]]] = {}
    findings: list[Finding] = []
    for path in _py_files():
        rows = _normalised_lines(path)
        rel = path.relative_to(ROOT).as_posix()
        for start in range(0, max(0, len(rows) - MIN_LINES + 1)):
            chunk = rows[start : start + MIN_LINES]
            text = "\n".join(line for _, line in chunk)
            tokens = _TOKEN.findall(text)
            if len(tokens) < MIN_TOKENS:
                continue
            digest = hashlib.sha256(text.encode()).hexdigest()
            blocks.setdefault(digest, []).append((rel, chunk[0][0]))
    seen: set[str] = set()
    for digest, locs in blocks.items():
        if len(locs) < 2:
            continue
        key = digest
        if key in seen:
            continue
        seen.add(key)
        first = locs[0]
        for loc in locs[1:]:
            findings.append(
                Finding(
                    loc[0],
                    loc[1],
                    "common-python:DuplicatedBlocks",
                    f"duplicated block also at {first[0]}:{first[1]}",
                )
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-complexity", type=int, default=MAX_COMPLEXITY)
    args = parser.parse_args()
    findings = check_complexity(args.max_complexity) + check_duplication()
    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        print(f"sonar-local: {len(findings)} finding(s)", file=sys.stderr)
        return 1
    print("sonar-local: ok (0 issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
