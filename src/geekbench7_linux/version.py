"""Wrapper version from Meson ``_build.py`` or the repository ``VERSION`` file."""

from __future__ import annotations

from pathlib import Path

_FALLBACK = "0.0.0"


def _from_build() -> str | None:
    """Return VERSION from generated ``_build.py`` when installed via Meson."""
    try:
        from . import _build

        return str(_build.VERSION)
    except Exception:
        return None


def _version_candidates() -> list[Path]:
    here = Path(__file__).resolve()
    return [here.parent.parent.parent / "VERSION", Path.cwd() / "VERSION"]


def get_version() -> str:
    """Return the wrapper version string."""
    built = _from_build()
    if built is not None:
        return built
    for candidate in _version_candidates():
        if candidate.is_file():
            line = candidate.read_text(encoding="utf-8").splitlines()[0].strip()
            if line and not line.startswith("#"):
                return line
    return _FALLBACK
