"""XDG paths for geekbench7-linux (per-user state only)."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

APP_DIR = "geekbench7-linux"
_LOCAL = ".local"


def _home(env: Mapping[str, str]) -> Path:
    home = env.get("HOME") or env.get("USERPROFILE") or ""
    if not home:
        raise RuntimeError("HOME is not set")
    return Path(home)


def _xdg(env: Mapping[str, str], key: str, default: Path) -> Path:
    value = env.get(key, "")
    if value and os.path.isabs(value):
        return Path(value)
    return default


@dataclass(frozen=True)
class Paths:
    """Per-user XDG layout for the wrapper and the extracted Geekbench tree."""

    home: Path
    config_dir: Path
    data_dir: Path
    cache_dir: Path
    state_dir: Path
    runtime_dir: Path

    @property
    def config_file(self) -> Path:
        return self.config_dir / "config.ini"

    @property
    def geekbench_dir(self) -> Path:
        """Extracted official Geekbench tree."""
        return self.data_dir / "geekbench"

    @property
    def downloads_dir(self) -> Path:
        return self.cache_dir / "downloads"

    @property
    def logs_dir(self) -> Path:
        return self.state_dir / "logs"

    @property
    def marker_file(self) -> Path:
        return self.geekbench_dir / ".geekbench7-linux-installed"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Paths:
        """Build paths from ``env`` (default ``os.environ``)."""
        environ: Mapping[str, str] = os.environ if env is None else env
        home = _home(environ)
        config_dir = _xdg(environ, "XDG_CONFIG_HOME", home / ".config") / APP_DIR
        data_dir = _xdg(environ, "XDG_DATA_HOME", home / _LOCAL / "share") / APP_DIR
        cache_dir = _xdg(environ, "XDG_CACHE_HOME", home / ".cache") / APP_DIR
        state_dir = _xdg(environ, "XDG_STATE_HOME", home / _LOCAL / "state") / APP_DIR
        runtime_base = environ.get("XDG_RUNTIME_DIR", "")
        if runtime_base and os.path.isabs(runtime_base):
            runtime_dir = Path(runtime_base) / APP_DIR
        else:
            runtime_dir = state_dir / "run"
        return cls(
            home=home,
            config_dir=config_dir,
            data_dir=data_dir,
            cache_dir=cache_dir,
            state_dir=state_dir,
            runtime_dir=runtime_dir,
        )

    def ensure(self) -> None:
        """Create the XDG directories (not the Geekbench extract)."""
        for path in (
            self.config_dir,
            self.data_dir,
            self.cache_dir,
            self.state_dir,
            self.runtime_dir,
            self.downloads_dir,
            self.logs_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)
