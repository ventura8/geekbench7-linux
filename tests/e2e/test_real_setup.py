"""Real CDN E2E — only when GB_E2E_GEEKBENCH=1 inside a container."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from geekbench7_linux.install import find_geekbench_binary, setup_geekbench, update_geekbench
from geekbench7_linux.manifest import load_manifest
from geekbench7_linux.paths import Paths

pytestmark = pytest.mark.skipif(
    os.environ.get("GB_E2E_GEEKBENCH") != "1",
    reason="needs GB_E2E_GEEKBENCH=1 (container + network)",
)


def test_e1_first_run_setup(xdg: Path) -> None:
    paths = Paths.from_env()
    man = load_manifest()
    binary = setup_geekbench(paths, accept_eula=True, manifest=man)
    assert binary.is_file()
    assert find_geekbench_binary(paths.geekbench_dir) == binary


def test_e2_update(xdg: Path) -> None:
    paths = Paths.from_env()
    man = load_manifest()
    setup_geekbench(paths, accept_eula=True, manifest=man)
    binary = update_geekbench(paths, manifest=man)
    assert binary.is_file()
