"""Architecture and CDN URL helpers."""

from __future__ import annotations

import pytest

from geekbench7_linux.arch import ARCH_AMD64, ARCH_ARM64, build_tarball_url, detect_arch
from geekbench7_linux.errors import UnsupportedEnv


def test_detect_amd64() -> None:
    assert detect_arch("x86_64") == ARCH_AMD64
    assert detect_arch("amd64") == ARCH_AMD64


def test_detect_arm64() -> None:
    assert detect_arch("aarch64") == ARCH_ARM64
    assert detect_arch("arm64") == ARCH_ARM64


def test_detect_rejects_riscv() -> None:
    with pytest.raises(UnsupportedEnv):
        detect_arch("riscv64")


def test_url_templates() -> None:
    assert build_tarball_url("7.1.0", ARCH_AMD64) == "https://cdn.geekbench.com/Geekbench-7.1.0-Linux.tar.gz"
    assert (
        build_tarball_url("7.1.0", ARCH_ARM64)
        == "https://cdn.geekbench.com/Geekbench-7.1.0-LinuxARMPreview.tar.gz"
    )


def test_url_rejects_unsafe_version() -> None:
    with pytest.raises(UnsupportedEnv):
        build_tarball_url("../evil", ARCH_AMD64)
    with pytest.raises(UnsupportedEnv):
        build_tarball_url("7.1.0-beta", ARCH_AMD64)
    with pytest.raises(UnsupportedEnv):
        build_tarball_url(".7.1.0", ARCH_AMD64)
    with pytest.raises(UnsupportedEnv):
        build_tarball_url("7.1.0.", ARCH_AMD64)
    with pytest.raises(UnsupportedEnv):
        build_tarball_url("7..1.0", ARCH_AMD64)
    with pytest.raises(UnsupportedEnv):
        build_tarball_url("7.1.0", "riscv")
    with pytest.raises(UnsupportedEnv):
        build_tarball_url("", ARCH_AMD64)
