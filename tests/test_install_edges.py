"""Cover install.py extract fallback and update guards."""

from __future__ import annotations

import io
import tarfile
from pathlib import Path

import pytest

import geekbench7_linux.install as install_mod
from geekbench7_linux.config import load_config
from geekbench7_linux.errors import NotInstalled, UsageError
from geekbench7_linux.install import update_geekbench
from geekbench7_linux.manifest import load_manifest
from geekbench7_linux.paths import Paths


def test_update_requires_eula(xdg: Path, sample_manifest: Path) -> None:
    paths = Paths.from_env()
    man = load_manifest(sample_manifest)
    with pytest.raises(UsageError):
        update_geekbench(paths, manifest=man)


def test_safe_extract_rejects_traversal(tmp_path: Path) -> None:
    dest = tmp_path / "out"
    dest.mkdir()
    tar_path = tmp_path / "evil.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        data = b"x"
        info = tarfile.TarInfo(name="../evil")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    with tarfile.open(tar_path, "r:gz") as tar:
        with pytest.raises(NotInstalled):
            install_mod._safe_extract(tar, dest)


def test_setup_after_eula(xdg: Path, monkeypatch: pytest.MonkeyPatch, sample_manifest: Path) -> None:
    def fake_download(url, dest, **kwargs):
        dest.parent.mkdir(parents=True, exist_ok=True)
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            data = b"#!/bin/sh\n"
            info = tarfile.TarInfo(name="Geekbench-7.1.0-Linux/geekbench7")
            info.size = len(data)
            info.mode = 0o755
            tar.addfile(info, io.BytesIO(data))
        dest.write_bytes(buf.getvalue())
        return "c" * 64

    monkeypatch.setattr(install_mod, "download_file", fake_download)
    paths = Paths.from_env()
    cfg = load_config(paths)
    cfg.accepted_eula = True
    cfg.save()
    binary = install_mod.setup_geekbench(
        paths, accept_eula=True, manifest=load_manifest(sample_manifest), arch="amd64"
    )
    assert binary.is_file()
