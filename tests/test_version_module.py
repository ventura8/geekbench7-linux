"""version.py branches."""

from __future__ import annotations

from pathlib import Path

import geekbench7_linux.version as version_mod


def test_from_build(monkeypatch) -> None:
    monkeypatch.setattr(version_mod, "_from_build", lambda: "9.8.7")
    assert version_mod.get_version() == "9.8.7"


def test_from_version_file(monkeypatch, tmp_path: Path) -> None:
    ver = tmp_path / "VERSION"
    ver.write_text("3.2.1\n", encoding="utf-8")
    monkeypatch.setattr(version_mod, "_from_build", lambda: None)
    monkeypatch.setattr(version_mod, "_version_candidates", lambda: [ver])
    assert version_mod.get_version() == "3.2.1"


def test_fallback(monkeypatch) -> None:
    monkeypatch.setattr(version_mod, "_from_build", lambda: None)
    monkeypatch.setattr(version_mod, "_version_candidates", lambda: [])
    assert version_mod.get_version() == version_mod._FALLBACK


def test_skips_comment_version(monkeypatch, tmp_path: Path) -> None:
    ver = tmp_path / "VERSION"
    ver.write_text("# nope\n", encoding="utf-8")
    monkeypatch.setattr(version_mod, "_from_build", lambda: None)
    monkeypatch.setattr(version_mod, "_version_candidates", lambda: [ver])
    assert version_mod.get_version() == version_mod._FALLBACK
