"""Runtime manifest: pinned Geekbench versions and hashes per architecture."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from .arch import ARCH_AMD64, ARCH_ARM64, ARCH_RISCV64, build_tarball_url
from .errors import ConfigError

ALLOWED_HOSTS: frozenset[str] = frozenset({"cdn.geekbench.com"})


@dataclass(frozen=True)
class ArchPin:
    """One architecture's pinned Geekbench tarball."""

    arch: str
    version: str
    size: int
    sha256: str

    @property
    def url(self) -> str:
        return build_tarball_url(self.version, self.arch)

    @classmethod
    def from_dict(cls, arch: str, data: dict[str, Any]) -> ArchPin:
        try:
            version = str(data["version"])
            size = int(data["size"])
            sha256 = str(data["sha256"]).lower()
        except (KeyError, TypeError, ValueError) as exc:
            raise ConfigError(f"invalid manifest entry for {arch}: {exc}") from exc
        if size < 0:
            raise ConfigError(f"negative size for {arch}")
        if len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
            raise ConfigError(f"invalid sha256 for {arch}")
        return cls(arch=arch, version=version, size=size, sha256=sha256)


@dataclass(frozen=True)
class Manifest:
    """Loaded runtime manifest."""

    schema: int
    arches: dict[str, ArchPin]
    allowed_hosts: frozenset[str]

    def pin(self, arch: str) -> ArchPin:
        if arch not in self.arches:
            raise ConfigError(f"manifest has no pin for arch {arch!r}")
        return self.arches[arch]


def _load_dict(data: dict[str, Any]) -> Manifest:
    schema = int(data.get("schema", 1))
    raw_arches = data.get("arches")
    if not isinstance(raw_arches, dict):
        raise ConfigError("manifest.arches must be an object")
    arches: dict[str, ArchPin] = {}
    for key in (ARCH_AMD64, ARCH_ARM64, ARCH_RISCV64):
        entry = raw_arches.get(key)
        if entry is None:
            continue
        if not isinstance(entry, dict):
            raise ConfigError(f"manifest.arches.{key} must be an object")
        arches[key] = ArchPin.from_dict(key, entry)
    if not arches:
        raise ConfigError("manifest has no architecture pins")
    hosts = data.get("allowed_hosts", list(ALLOWED_HOSTS))
    if not isinstance(hosts, list) or not hosts:
        raise ConfigError("manifest.allowed_hosts must be a non-empty list")
    return Manifest(schema=schema, arches=arches, allowed_hosts=frozenset(str(h) for h in hosts))


def load_manifest(path: Path | None = None) -> Manifest:
    """Load from ``path`` or the packaged ``runtime-manifest.json``."""
    if path is not None:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ConfigError("manifest root must be an object")
        return _load_dict(data)
    ref = resources.files("geekbench7_linux.data").joinpath("runtime-manifest.json")
    with ref.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ConfigError("manifest root must be an object")
    return _load_dict(data)


def default_manifest_path() -> Path:
    """Path to the source-tree or installed manifest file (for tooling)."""
    return Path(__file__).resolve().parent / "data" / "runtime-manifest.json"
