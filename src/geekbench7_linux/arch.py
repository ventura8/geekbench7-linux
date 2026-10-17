"""Host architecture detection and CDN URL templates."""

from __future__ import annotations

import platform

from .errors import UnsupportedEnv

# Canonical arch keys used in the runtime manifest.
ARCH_AMD64 = "amd64"
ARCH_ARM64 = "arm64"

_MACHINE_MAP = {
    "x86_64": ARCH_AMD64,
    "amd64": ARCH_AMD64,
    "aarch64": ARCH_ARM64,
    "arm64": ARCH_ARM64,
}

URL_TEMPLATES: dict[str, str] = {
    ARCH_AMD64: "https://cdn.geekbench.com/Geekbench-{version}-Linux.tar.gz",
    ARCH_ARM64: "https://cdn.geekbench.com/Geekbench-{version}-LinuxARMPreview.tar.gz",
}


def detect_arch(machine: str | None = None) -> str:
    """Return ``amd64`` or ``arm64`` for the host; raise if unsupported."""
    raw = (machine if machine is not None else platform.machine()).strip().lower()
    arch = _MACHINE_MAP.get(raw)
    if arch is None:
        raise UnsupportedEnv(
            f"unsupported architecture {raw!r}",
            hint="geekbench7-linux supports amd64/x86_64 and arm64/aarch64",
        )
    return arch


def build_tarball_url(version: str, arch: str) -> str:
    """Build the CDN URL locally from the template (never trust a scraped URL)."""
    if arch not in URL_TEMPLATES:
        raise UnsupportedEnv(f"no CDN template for arch {arch!r}")
    if not version or any(c not in "0123456789." for c in version):
        raise UnsupportedEnv(f"refusing unsafe Geekbench version {version!r}")
    if ".." in version or version.startswith(".") or version.endswith("."):
        raise UnsupportedEnv(f"refusing unsafe Geekbench version {version!r}")
    return URL_TEMPLATES[arch].format(version=version)
