"""Hit remaining manifest branches."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from geekbench7_linux.errors import ConfigError
from geekbench7_linux.manifest import ArchPin, default_manifest_path, load_manifest


def test_default_manifest_path_exists() -> None:
    assert default_manifest_path().is_file()


def test_allowed_hosts_empty(tmp_path: Path) -> None:
    path = tmp_path / "m.json"
    path.write_text(
        json.dumps(
            {
                "schema": 1,
                "allowed_hosts": [],
                "arches": {"amd64": {"version": "7.1.0", "size": 0, "sha256": "0" * 64}},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        load_manifest(path)


def test_arches_not_object(tmp_path: Path) -> None:
    path = tmp_path / "m.json"
    path.write_text(json.dumps({"schema": 1, "allowed_hosts": ["cdn.geekbench.com"], "arches": []}), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_manifest(path)


def test_archpin_key_error() -> None:
    with pytest.raises(ConfigError):
        ArchPin.from_dict("amd64", {"version": "7.1.0"})
