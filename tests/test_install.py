"""Install helpers without network."""

from __future__ import annotations

import tarfile
from pathlib import Path

import pytest

from geekbench7_linux.errors import NotInstalled, UsageError
from geekbench7_linux.install import find_geekbench_binary, setup_geekbench, uninstall_user_state
from geekbench7_linux.manifest import load_manifest
from geekbench7_linux.paths import Paths


def _make_fake_tarball(path: Path) -> None:
    root = path.parent / "tree"
    (root / "Geekbench-7.1.0-Linux").mkdir(parents=True)
    binary = root / "Geekbench-7.1.0-Linux" / "geekbench7"
    binary.write_text("#!/bin/sh\necho fake\n", encoding="utf-8")
    binary.chmod(0o755)
    with tarfile.open(path, "w:gz") as tar:
        tar.add(root / "Geekbench-7.1.0-Linux", arcname="Geekbench-7.1.0-Linux")


def test_find_binary_missing(xdg: Path) -> None:
    paths = Paths.from_env()
    with pytest.raises(NotInstalled):
        find_geekbench_binary(paths.geekbench_dir)


def test_setup_requires_consent(xdg: Path, sample_manifest: Path) -> None:
    paths = Paths.from_env()
    man = load_manifest(sample_manifest)
    with pytest.raises(UsageError):
        setup_geekbench(paths, accept_eula=False, manifest=man)


def test_uninstall_empty(xdg: Path) -> None:
    paths = Paths.from_env()
    paths.ensure()
    uninstall_user_state(paths)
