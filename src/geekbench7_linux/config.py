"""Simple INI config under XDG_CONFIG_HOME."""

from __future__ import annotations

import configparser
from pathlib import Path

from .paths import Paths


class Config:
    """Wrapper config (consent flag, optional arch override)."""

    def __init__(self, paths: Paths) -> None:
        self.paths = paths
        self._parser = configparser.ConfigParser()
        if paths.config_file.is_file():
            self._parser.read(paths.config_file, encoding="utf-8")
        if not self._parser.has_section("main"):
            self._parser.add_section("main")

    @property
    def accepted_eula(self) -> bool:
        return self._parser.getboolean("main", "accepted_eula", fallback=False)

    @accepted_eula.setter
    def accepted_eula(self, value: bool) -> None:
        self._parser.set("main", "accepted_eula", "true" if value else "false")

    @property
    def arch_override(self) -> str:
        return self._parser.get("main", "arch", fallback="")

    def save(self) -> None:
        self.paths.config_dir.mkdir(parents=True, exist_ok=True)
        with self.paths.config_file.open("w", encoding="utf-8") as fh:
            self._parser.write(fh)


def load_config(paths: Paths) -> Config:
    """Load or create config for ``paths``."""
    return Config(paths)


def write_marker(path: Path, version: str, arch: str, sha256: str) -> None:
    """Record what was installed in the Geekbench extract directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"version={version}\narch={arch}\nsha256={sha256}\n", encoding="utf-8")


def read_marker(path: Path) -> dict[str, str]:
    """Parse the install marker; empty dict if missing."""
    if not path.is_file():
        return {}
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result
