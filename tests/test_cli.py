"""CLI dispatch smoke tests."""

from __future__ import annotations

from geekbench7_linux.cli import _normalize_run_argv, build_parser, main
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


def test_normalize_run_inserts_separator_before_geekbench_flags() -> None:
    assert _normalize_run_argv(["run", "--gpu", "CUDA"]) == ["run", "--", "--gpu", "CUDA"]
    assert _normalize_run_argv(["run", "--accept-eula", "--gpu", "CUDA"]) == [
        "run",
        "--accept-eula",
        "--",
        "--gpu",
        "CUDA",
    ]
    assert _normalize_run_argv(["run", "--", "--gpu", "CUDA"]) == ["run", "--", "--gpu", "CUDA"]
    assert _normalize_run_argv(["run"]) == ["run"]


def test_run_parses_gpu_without_explicit_separator() -> None:
    args = build_parser().parse_args(_normalize_run_argv(["run", "--gpu", "CUDA"]))
    assert args.command == "run"
    assert args.geekbench_args == ["--", "--gpu", "CUDA"]
