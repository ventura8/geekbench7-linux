"""run command with a fake binary (no execv)."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from geekbench7_linux.commands import run as run_cmd
from geekbench7_linux.context import AppContext
from geekbench7_linux.paths import Paths


def test_run_execv(xdg: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = Paths.from_env()
    paths.geekbench_dir.mkdir(parents=True, exist_ok=True)
    binary = paths.geekbench_dir / "geekbench7"
    binary.write_text("#!/bin/sh\n", encoding="utf-8")
    binary.chmod(0o755)
    called: list[list[str]] = []

    def fake_execv(path: str, args: list[str]) -> None:
        called.append([path, *args])
        raise SystemExit(0)

    monkeypatch.setattr(run_cmd.os, "execv", fake_execv)
    ctx = AppContext(
        args=argparse.Namespace(
            command="run",
            geekbench_args=["--", "--help"],
            accept_eula=False,
            json=False,
            allow_root=False,
            verbose=False,
        )
    )
    with pytest.raises(SystemExit):
        run_cmd.run(ctx)
    assert called and "--help" in called[0]
