"""Manifest loading and validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from geekbench7_linux.errors import ConfigError
from geekbench7_linux.manifest import load_manifest


def test_load_packaged_manifest() -> None:
    man = load_manifest()
    assert "amd64" in man.arches
    assert "arm64" in man.arches
    assert man.pin("amd64").version == "7.1.0"
    assert "cdn.geekbench.com" in man.allowed_hosts


def test_load_sample(sample_manifest: Path) -> None:
    man = load_manifest(sample_manifest)
    assert man.pin("arm64").url.endswith("LinuxARMPreview.tar.gz")


def test_rejects_bad_sha(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps(
            {
                "schema": 1,
                "allowed_hosts": ["cdn.geekbench.com"],
                "arches": {"amd64": {"version": "7.1.0", "size": 1, "sha256": "deadbeef"}},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        load_manifest(path)
