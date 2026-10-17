"""Packaging hygiene: no maintainer scripts, no embedded Geekbench binaries."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_no_debian_maintainer_scripts() -> None:
    debian = ROOT / "debian"
    if not debian.is_dir():
        return
    for name in ("postinst", "preinst", "prerm", "postrm"):
        assert not (debian / name).exists(), f"must not ship debian/{name}"


def test_no_geekbench_tarball_in_repo() -> None:
    for path in ROOT.rglob("*.tar.gz"):
        if "Geekbench-" in path.name:
            raise AssertionError(f"must not vendor Geekbench tarball: {path}")


def test_rpm_specs_have_no_scriptlets() -> None:
    for spec in (ROOT / "packaging" / "rpm").rglob("*.spec"):
        text = spec.read_text(encoding="utf-8")
        forbidden = {"%pre", "%post", "%preun", "%postun", "%pretrans", "%posttrans"}
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            token = stripped.split()[0] if stripped else ""
            assert token not in forbidden, f"{spec} has scriptlet {token}"
