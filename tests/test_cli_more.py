"""CLI root refusal and alias behaviour."""

from __future__ import annotations

from geekbench7_linux.cli import main
from geekbench7_linux.errors import UnsupportedEnv


def test_root_refused(monkeypatch) -> None:
    monkeypatch.setattr("geekbench7_linux.cli.os.geteuid", lambda: 0)
    code = main(["about"])
    assert code == UnsupportedEnv.exit_code


def test_allow_root(monkeypatch, capsys) -> None:
    monkeypatch.setattr("geekbench7_linux.cli.os.geteuid", lambda: 0)
    assert main(["--allow-root", "about"]) == 0
    assert "Primate Labs" in capsys.readouterr().out


def test_no_command_prints_help(capsys) -> None:
    assert main([]) == 2


def test_geekbench7_wrapper_with_json(capsys) -> None:
    assert main(["--json", "wrapper", "version"], prog="geekbench7") == 0
    out = capsys.readouterr().out
    assert out.strip()


def test_dispatch_without_handler() -> None:
    import argparse

    from geekbench7_linux.cli import _dispatch

    assert _dispatch(argparse.Namespace(allow_root=True, _handler=None)) == 2
