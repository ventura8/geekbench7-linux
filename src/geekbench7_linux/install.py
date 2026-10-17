"""Download, extract and locate the official Geekbench 7 tree."""

from __future__ import annotations

import logging
import shutil
import tarfile
from pathlib import Path

from .arch import detect_arch
from .config import read_marker, write_marker
from .download import download_file
from .errors import NotInstalled
from .manifest import Manifest, load_manifest
from .paths import Paths

log = logging.getLogger(__name__)


def resolve_arch(paths: Paths, override: str = "") -> str:
    """Return the arch to use (config override or host detection)."""
    from .config import load_config

    if override:
        return detect_arch(override)
    cfg = load_config(paths)
    if cfg.arch_override:
        return detect_arch(cfg.arch_override)
    return detect_arch()


def find_geekbench_binary(geekbench_dir: Path) -> Path:
    """Locate ``geekbench7`` inside an extracted tree."""
    direct = geekbench_dir / "geekbench7"
    if direct.is_file() and os_access_exec(direct):
        return direct
    for child in sorted(geekbench_dir.iterdir()) if geekbench_dir.is_dir() else []:
        candidate = child / "geekbench7"
        if candidate.is_file() and os_access_exec(candidate):
            return candidate
    raise NotInstalled(
        f"geekbench7 binary not found under {geekbench_dir}",
        hint="run: geekbench7-linux setup",
    )


def os_access_exec(path: Path) -> bool:
    return path.is_file() and (path.stat().st_mode & 0o111) != 0


def _extract_tarball(tarball: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tarball, "r:gz") as tar:
        # Python 3.12+ has filter=; use data filter when available.
        if hasattr(tarfile, "data_filter"):
            tar.extractall(dest, filter=tarfile.data_filter)
        else:
            _safe_extract(tar, dest)


def _safe_extract(tar: tarfile.TarFile, dest: Path) -> None:
    dest_resolved = dest.resolve()
    for member in tar.getmembers():
        target = (dest / member.name).resolve()
        if not str(target).startswith(str(dest_resolved)):
            raise NotInstalled(f"refusing unsafe path in tarball: {member.name}")
        tar.extract(member, dest)


def setup_geekbench(
    paths: Paths,
    *,
    accept_eula: bool,
    manifest: Manifest | None = None,
    arch: str = "",
) -> Path:
    """Download and extract Geekbench; return the binary path."""
    from .config import load_config
    from .credits import render_consent
    from .errors import UsageError

    paths.ensure()
    cfg = load_config(paths)
    if not accept_eula and not cfg.accepted_eula:
        raise UsageError(
            "Geekbench EULA / consent required before download",
            hint="re-run with --accept-eula after reading:\n" + render_consent(),
        )
    if accept_eula:
        cfg.accepted_eula = True
        cfg.save()

    man = manifest if manifest is not None else load_manifest()
    resolved = resolve_arch(paths, arch)
    pin = man.pin(resolved)
    tarball_name = f"Geekbench-{pin.version}-{resolved}.tar.gz"
    tarball = paths.downloads_dir / tarball_name
    digest = download_file(
        pin.url,
        tarball,
        expected_size=pin.size,
        expected_sha256=pin.sha256,
        allowed_hosts=man.allowed_hosts,
    )
    _extract_tarball(tarball, paths.geekbench_dir)
    write_marker(paths.marker_file, pin.version, resolved, digest)
    binary = find_geekbench_binary(paths.geekbench_dir)
    binary.chmod(binary.stat().st_mode | 0o111)
    log.info("Geekbench %s (%s) ready at %s", pin.version, resolved, binary)
    return binary


def update_geekbench(paths: Paths, *, manifest: Manifest | None = None, arch: str = "") -> Path:
    """Re-download the pinned version (or refresh TOFU pin)."""
    from .config import load_config
    from .errors import UsageError

    cfg = load_config(paths)
    if not cfg.accepted_eula:
        raise UsageError("run setup --accept-eula first")
    return setup_geekbench(paths, accept_eula=True, manifest=manifest, arch=arch)


def uninstall_user_state(paths: Paths) -> None:
    """Remove per-user Geekbench install and cache (not the system package)."""
    for path in (paths.geekbench_dir, paths.downloads_dir):
        if path.exists():
            shutil.rmtree(path)
    if paths.marker_file.exists():
        paths.marker_file.unlink()


def installed_info(paths: Paths) -> dict[str, str]:
    """Return marker metadata or empty."""
    return read_marker(paths.marker_file)
