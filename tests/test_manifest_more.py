"""Manifest error paths."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from geekbench7_linux.errors import ConfigError
from geekbench7_linux.manifest import load_manifest


def test_missing_arches(tmp_path: Path) -> None:
    path = tmp_path / "m.json"
    path.write_text(json.dumps({"schema": 1, "allowed_hosts": ["cdn.geekbench.com"], "arches": {}}), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_manifest(path)


def test_bad_arch_type(tmp_path: Path) -> None:
    path = tmp_path / "m.json"
    path.write_text(
        json.dumps({"schema": 1, "allowed_hosts": ["cdn.geekbench.com"], "arches": {"amd64": "nope"}}),
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        load_manifest(path)


def test_negative_size(tmp_path: Path) -> None:
    path = tmp_path / "m.json"
    path.write_text(
        json.dumps(
            {
                "schema": 1,
                "allowed_hosts": ["cdn.geekbench.com"],
                "arches": {"amd64": {"version": "7.1.0", "size": -1, "sha256": "a" * 64}},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        load_manifest(path)


def test_root_not_object(tmp_path: Path) -> None:
    path = tmp_path / "m.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_manifest(path)


def test_pin_missing_arch(sample_manifest: Path) -> None:
    man = load_manifest(sample_manifest)
    with pytest.raises(ConfigError):
        man.pin("riscv")
