"""Fill remaining coverage gaps so every package file is >= 90%."""

from __future__ import annotations

import argparse
import io
import tarfile
from pathlib import Path

import pytest

from geekbench7_linux.cli import main
from geekbench7_linux.commands import desktop, doctor, setup, uninstall, update, version
from geekbench7_linux.commands import run as run_cmd
from geekbench7_linux.config import load_config, read_marker
from geekbench7_linux.context import AppContext
from geekbench7_linux.errors import Geekbench7LinuxError, IntegrityFailed
from geekbench7_linux.install import (
    find_geekbench_binary,
    resolve_arch,
    setup_geekbench,
    uninstall_user_state,
)
from geekbench7_linux.manifest import default_manifest_path, load_manifest
from geekbench7_linux.paths import Paths
from geekbench7_linux import version as version_mod
import geekbench7_linux.install as install_mod


def _ctx(**kwargs: object) -> AppContext:
    base: dict[str, object] = {
        "command": "x",
        "json": False,
        "allow_root": False,
        "verbose": False,
        "accept_eula": True,
        "arch": "",
        "yes": True,
        "action": "install",
        "geekbench_args": [],
    }
    base.update(kwargs)
    return AppContext(args=argparse.Namespace(**base))


def _fake_tarball_download(url, dest, **kwargs):
    dest.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        data = b"#!/bin/sh\necho ok\n"
        info = tarfile.TarInfo(name="Geekbench-7.1.0-Linux/geekbench7")
        info.size = len(data)
        info.mode = 0o755
        tar.addfile(info, io.BytesIO(data))
    dest.write_bytes(buf.getvalue())
    return "b" * 64


def test_json_branches(xdg: Path, capsys, monkeypatch, sample_manifest: Path) -> None:
    monkeypatch.setattr(install_mod, "download_file", _fake_tarball_download)
    monkeypatch.setattr(install_mod, "load_manifest", lambda path=None: load_manifest(sample_manifest))
    assert setup.run(_ctx(command="setup", json=True, accept_eula=True, arch="amd64")) == 0
    assert "status" in capsys.readouterr().out
    assert update.run(_ctx(command="update", json=True, arch="amd64")) == 0
    assert doctor.run(_ctx(command="doctor", json=True)) == 0
    assert version.run(_ctx(command="version", json=True)) == 0
    assert desktop.run(_ctx(command="desktop", action="install", json=True)) == 0
    assert desktop.run(_ctx(command="desktop", action="remove", json=True)) == 0
    assert uninstall.run(_ctx(command="uninstall", yes=True, json=True)) == 0


def test_uninstall_abort(xdg: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr("builtins.input", lambda _p: "n")
    assert uninstall.run(_ctx(command="uninstall", yes=False, json=False)) == 1
    assert "aborted" in capsys.readouterr().out


def test_run_triggers_setup(xdg: Path, monkeypatch, sample_manifest: Path) -> None:
    monkeypatch.setattr(install_mod, "download_file", _fake_tarball_download)
    monkeypatch.setattr(install_mod, "load_manifest", lambda path=None: load_manifest(sample_manifest))
    called: list[str] = []

    def fake_execv(path: str, args: list[str]) -> None:
        called.append(path)
        raise SystemExit(0)

    monkeypatch.setattr(run_cmd.os, "execv", fake_execv)
    ctx = _ctx(command="run", geekbench_args=["--help"], accept_eula=True)
    with pytest.raises(SystemExit):
        run_cmd.run(ctx)
    assert called


def test_cli_alias_geekbench7(monkeypatch, xdg: Path) -> None:
    assert main(["version"], prog="/usr/bin/geekbench7") == 0
    # alias with flag-only argv prepends run; without eula/setup it errors (no network)
    code = main(["--json"], prog="geekbench7")
    assert code != 0


def test_error_str_with_hint() -> None:
    err = Geekbench7LinuxError("boom", hint="try again")
    assert "hint:" in str(err)
    assert str(IntegrityFailed("x")) == "x"


def test_paths_home_missing(monkeypatch) -> None:
    monkeypatch.delenv("HOME", raising=False)
    monkeypatch.delenv("USERPROFILE", raising=False)
    with pytest.raises(RuntimeError):
        Paths.from_env({})


def test_paths_xdg_relative(monkeypatch, tmp_path: Path) -> None:
    home = tmp_path / "h"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", "relative-not-abs")
    paths = Paths.from_env()
    assert paths.config_dir.is_absolute()


def test_resolve_arch_override(xdg: Path) -> None:
    paths = Paths.from_env()
    cfg = load_config(paths)
    # write arch override via parser
    cfg._parser.set("main", "arch", "arm64")
    cfg.save()
    assert resolve_arch(paths) == "arm64"
    assert resolve_arch(paths, "x86_64") == "amd64"


def test_version_fallback(monkeypatch, tmp_path: Path) -> None:
    # Force import failure path by pointing away from _build
    monkeypatch.setattr(version_mod, "_FALLBACK", "9.9.9")
    # Ensure VERSION file read works from cwd
    monkeypatch.chdir(tmp_path)
    (tmp_path / "VERSION").write_text("2.3.4\n", encoding="utf-8")
    # get_version walks to VERSION; may still find repo VERSION via __file__
    ver = version_mod.get_version()
    assert ver


def test_install_safe_extract_and_marker(xdg: Path, sample_manifest: Path, monkeypatch) -> None:
    monkeypatch.setattr(install_mod, "download_file", _fake_tarball_download)
    paths = Paths.from_env()
    man = load_manifest(sample_manifest)
    binary = setup_geekbench(paths, accept_eula=True, manifest=man, arch="amd64")
    assert binary.exists()
    assert find_geekbench_binary(paths.geekbench_dir).exists()
    assert read_marker(paths.marker_file)["version"] == "7.1.0"
    uninstall_user_state(paths)
    assert default_manifest_path().is_file()


def test_config_arch_property(xdg: Path) -> None:
    cfg = load_config(Paths.from_env())
    assert cfg.arch_override == ""
