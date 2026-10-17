"""CLI dispatch smoke tests."""

from __future__ import annotations

from geekbench7_linux.cli import build_parser, main
from geekbench7_linux.credits import thank_you


def test_about(capsys) -> None:
    code = main(["about"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Primate Labs" in out
    assert "John Poole" in out
    assert thank_you().split(",")[0] in out or "Thank you" in out


def test_version(capsys) -> None:
    code = main(["version"])
    assert code == 0
    assert capsys.readouterr().out.strip()


def test_parser_has_commands() -> None:
    parser = build_parser()
    # ensure setup/run exist
    help_text = parser.format_help()
    assert "setup" in help_text
    assert "run" in help_text
