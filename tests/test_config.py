"""Config and marker helpers."""

from __future__ import annotations

from pathlib import Path

from geekbench7_linux.config import load_config, read_marker, write_marker
from geekbench7_linux.paths import Paths


def test_config_roundtrip(xdg: Path) -> None:
    paths = Paths.from_env()
    cfg = load_config(paths)
    assert cfg.accepted_eula is False
    cfg.accepted_eula = True
    cfg.save()
    cfg2 = load_config(paths)
    assert cfg2.accepted_eula is True


def test_marker(xdg: Path) -> None:
    paths = Paths.from_env()
    paths.ensure()
    write_marker(paths.marker_file, "7.1.0", "amd64", "a" * 64)
    info = read_marker(paths.marker_file)
    assert info["version"] == "7.1.0"
    assert read_marker(paths.geekbench_dir / "missing") == {}
