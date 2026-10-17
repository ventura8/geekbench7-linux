"""Command handlers with fakes."""

from __future__ import annotations

import argparse
from pathlib import Path

from geekbench7_linux.commands import about, desktop, doctor, setup, uninstall, update, version
from geekbench7_linux.context import AppContext
from geekbench7_linux.install import find_geekbench_binary
from geekbench7_linux.manifest import load_manifest
from geekbench7_linux.paths import Paths


def _ctx(command: str, **kwargs: object) -> AppContext:
    base: dict[str, object] = {"command": command, "json": False, "allow_root": False, "verbose": False}
    base.update(kwargs)
    return AppContext(args=argparse.Namespace(**base))


def test_about_and_version(xdg: Path, capsys) -> None:
    assert about.run(_ctx("about")) == 0
    assert "Primate Labs" in capsys.readouterr().out
    assert version.run(_ctx("version")) == 0


def test_about_json(xdg: Path, capsys) -> None:
    ctx = _ctx("about", json=True)
    assert about.run(ctx) == 0
    assert "wrapper_version" in capsys.readouterr().out


def test_doctor_missing(xdg: Path) -> None:
    assert doctor.run(_ctx("doctor")) == 1


def test_desktop_install_remove(xdg: Path) -> None:
    assert desktop.run(_ctx("desktop", action="install")) == 0
    path = Path.home() / ".local" / "share" / "applications" / "io.github.ventura8.Geekbench7Linux.desktop"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "Primate Labs" in text
    assert desktop.run(_ctx("desktop", action="remove")) == 0


def test_uninstall_yes(xdg: Path) -> None:
    paths = Paths.from_env()
    paths.ensure()
    paths.geekbench_dir.mkdir(parents=True, exist_ok=True)
    (paths.geekbench_dir / "geekbench7").write_text("x", encoding="utf-8")
    assert uninstall.run(_ctx("uninstall", yes=True)) == 0


def test_setup_with_mocked_download(xdg: Path, sample_manifest: Path, monkeypatch) -> None:
    import geekbench7_linux.install as install_mod

    paths = Paths.from_env()

    def fake_download(url, dest, **kwargs):
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Build a tiny tar.gz with geekbench7 inside
        import tarfile
        import io

        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            data = b"#!/bin/sh\necho ok\n"
            info = tarfile.TarInfo(name="Geekbench-7.1.0-Linux/geekbench7")
            info.size = len(data)
            info.mode = 0o755
            tar.addfile(info, io.BytesIO(data))
        dest.write_bytes(buf.getvalue())
        return "a" * 64

    monkeypatch.setattr(install_mod, "download_file", fake_download)
    monkeypatch.setattr(install_mod, "load_manifest", lambda path=None: load_manifest(sample_manifest))
    man = load_manifest(sample_manifest)
    binary = install_mod.setup_geekbench(paths, accept_eula=True, manifest=man, arch="amd64")
    assert binary.is_file()
    assert find_geekbench_binary(paths.geekbench_dir) == binary
    updated = install_mod.update_geekbench(paths, manifest=man, arch="amd64")
    assert updated.is_file()
    assert update.run(_ctx("update", arch="amd64")) == 0
    assert setup.run(_ctx("setup", accept_eula=True, arch="amd64")) == 0
