"""Container smoke E2E without requiring a real CDN download."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from geekbench7_linux.cli import main
from geekbench7_linux.credits import thank_you
from geekbench7_linux.install import uninstall_user_state
from geekbench7_linux.paths import Paths

pytestmark = pytest.mark.skipif(
    os.environ.get("GB_E2E_SMOKE") != "1" and os.environ.get("GB_E2E") != "1",
    reason="needs GB_E2E_SMOKE=1 or GB_E2E=1",
)


def test_e4_uninstall_and_e5_doctor(xdg: Path, capsys) -> None:
    paths = Paths.from_env()
    paths.ensure()
    (paths.geekbench_dir).mkdir(parents=True, exist_ok=True)
    (paths.geekbench_dir / "geekbench7").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    (paths.geekbench_dir / "geekbench7").chmod(0o755)
    code = main(["doctor"])
    assert code in {0, 1}
    uninstall_user_state(paths)
    assert not paths.geekbench_dir.exists() or not any(paths.geekbench_dir.iterdir())


def test_e6_no_embedded_binary_in_tree() -> None:
    root = Path(__file__).resolve().parents[2]
    for path in root.rglob("Geekbench-*.tar.gz"):
        pytest.fail(f"embedded tarball {path}")


def test_credits_surface_in_about(capsys) -> None:
    assert main(["about"]) == 0
    out = capsys.readouterr().out
    assert "Primate Labs" in out
    assert "John Poole" in out
    assert "Thank you" in thank_you()
