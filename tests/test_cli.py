"""CLI dispatch smoke tests."""

from __future__ import annotations

import pytest

from geekbench7_linux.cli import _normalize_passthrough_argv, build_parser, main
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


def test_parser_has_wrapper_commands_only() -> None:
    from geekbench7_linux.commands import WRAPPER_COMMANDS

    help_text = build_parser().format_help()
    assert "setup" in help_text
    assert "doctor" in help_text
    assert "run" not in WRAPPER_COMMANDS


def test_normalize_passthrough_inserts_separator() -> None:
    assert _normalize_passthrough_argv(["--gpu", "CUDA"]) == ["--", "--gpu", "CUDA"]
    assert _normalize_passthrough_argv(["--accept-eula", "--gpu", "CUDA"]) == [
        "--accept-eula",
        "--",
        "--gpu",
        "CUDA",
    ]
    assert _normalize_passthrough_argv(["--", "--gpu", "CUDA"]) == ["--", "--gpu", "CUDA"]
    # Non-flag tokens start the Geekbench remainder (``wrapper`` is peeled earlier in main).
    assert _normalize_passthrough_argv(["wrapper", "doctor"]) == ["--", "wrapper", "doctor"]
    assert _normalize_passthrough_argv(["--gpu", "CUDA", "--"]) == ["--", "--gpu", "CUDA", "--"]
    # All wrapper flags → no separator inserted.
    assert _normalize_passthrough_argv(["--json", "-v"]) == ["--json", "-v"]


def test_geekbench7_wrapper_doctor(capsys) -> None:
    assert main(["wrapper", "about"], prog="geekbench7") == 0
    assert "Primate Labs" in capsys.readouterr().out


def test_geekbench7_linux_rejects_run() -> None:
    # ``run`` is no longer a geekbench7-linux subcommand.
    with pytest.raises(SystemExit) as exc:
        main(["run"])
    assert exc.value.code not in (0, None)


def test_geekbench7_help_passthrough(monkeypatch, xdg) -> None:
    """``geekbench7 --help`` must reach the official binary, not a wrapper tip."""
    from pathlib import Path

    from geekbench7_linux.commands import run as run_cmd
    from geekbench7_linux.paths import Paths

    paths = Paths.from_env()
    paths.geekbench_dir.mkdir(parents=True, exist_ok=True)
    binary = paths.geekbench_dir / "geekbench7"
    binary.write_text("#!/bin/sh\n", encoding="utf-8")
    binary.chmod(0o755)
    seen: list[list[str]] = []

    def fake_execv(path: str, args: list[str]) -> None:
        seen.append(list(args))
        raise SystemExit(0)

    monkeypatch.setattr(run_cmd.os, "execv", fake_execv)
    with pytest.raises(SystemExit):
        main(["--help"], prog="geekbench7")
    assert seen and "--help" in seen[0]
    assert Path(seen[0][0]).name == "geekbench7"
