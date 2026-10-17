"""Pytest configuration for geekbench7-linux."""

from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Import after sys.path bootstrap (tests/fixtures is on path via tests/).
sys.path.insert(0, str(Path(__file__).resolve().parent))
real_tier = importlib.import_module("fixtures.real_tier")


def pytest_configure(config: pytest.Config) -> None:
    real_tier.enforce()


@pytest.fixture
def xdg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate all XDG directories under tmp_path."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path / "runtime"))
    (tmp_path / "runtime").mkdir()
    return tmp_path


@pytest.fixture
def fake_bin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Prepend an empty fake bin directory to PATH."""
    bindir = tmp_path / "fake-bin"
    bindir.mkdir()
    monkeypatch.setenv("PATH", str(bindir) + os.pathsep + os.environ.get("PATH", ""))
    log = tmp_path / "fake-bin-calls.jsonl"
    log.write_text("", encoding="utf-8")
    monkeypatch.setenv("GB_FAKE_BIN_LOG", str(log))
    return bindir


@pytest.fixture
def sample_manifest(tmp_path: Path) -> Path:
    """Write a small TOFU manifest for unit tests."""
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema": 1,
                "allowed_hosts": ["cdn.geekbench.com", "127.0.0.1"],
                "arches": {
                    "amd64": {
                        "version": "7.1.0",
                        "size": 0,
                        "sha256": "0" * 64,
                    },
                    "arm64": {
                        "version": "7.1.0",
                        "size": 0,
                        "sha256": "0" * 64,
                    },
                    "riscv64": {
                        "version": "7.1.0",
                        "size": 0,
                        "sha256": "0" * 64,
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    return path
