"""XDG path layout."""

from __future__ import annotations

from pathlib import Path

from geekbench7_linux.paths import Paths


def test_paths_from_env(xdg: Path) -> None:
    paths = Paths.from_env()
    paths.ensure()
    assert paths.config_dir.is_dir()
    assert paths.downloads_dir.is_dir()
    assert paths.geekbench_dir.name == "geekbench"
    assert "geekbench7-linux" in str(paths.data_dir)
