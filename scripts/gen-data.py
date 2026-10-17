#!/usr/bin/env python3
"""Generate installed data files for geekbench7-linux from their single sources."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"


def _import_package() -> None:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))


def _resolve_under_allowed(path_arg: str) -> Path:
    """Resolve a CLI path; refuse writes/reads outside the repo or cwd (build dirs)."""
    candidate = Path(path_arg).expanduser()
    if ".." in Path(path_arg).parts:
        raise SystemExit(f"refusing path with parent segments: {path_arg!r}")
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    resolved = candidate.resolve()
    resolved_text = str(resolved)
    for root in (ROOT.resolve(), Path.cwd().resolve()):
        root_text = str(root)
        if resolved_text == root_text or resolved_text.startswith(root_text + os.sep):
            # Rebuild from the validated string so taint analysis treats it as clean.
            return Path(resolved_text)
    raise SystemExit(f"refusing path outside allowed roots: {resolved}")


def cmd_name(args: argparse.Namespace) -> int:
    _import_package()
    from geekbench7_linux import APP_ID, APP_NAME, PACKAGE

    mapping = {"APP_ID": APP_ID, "APP_NAME": APP_NAME, "PACKAGE": PACKAGE}
    key = args.key
    if key not in mapping:
        print(f"unknown name {key}", file=sys.stderr)
        return 1
    print(mapping[key])
    return 0


def cmd_build_info(args: argparse.Namespace) -> int:
    out = _resolve_under_allowed(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f'VERSION = "{args.version}"\nFLAVOR = "{args.flavor}"\n',
        encoding="utf-8",
    )
    return 0


def cmd_desktop(args: argparse.Namespace) -> int:
    _import_package()
    from geekbench7_linux import APP_ID, APP_NAME
    from geekbench7_linux.credits import render_desktop_comment

    template = (
        ROOT
        / "src"
        / "geekbench7_linux"
        / "data"
        / "templates"
        / f"{APP_ID}.desktop.in"
    )
    text = template.read_text(encoding="utf-8")
    rendered = (
        text.replace("@APP_ID@", APP_ID)
        .replace("@APP_NAME@", APP_NAME)
        .replace("@COMMENT@", render_desktop_comment())
        .replace("@EXEC@", "geekbench7-linux")
        .replace("@TRYEXEC@", "geekbench7-linux")
    )
    out = _resolve_under_allowed(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    return 0


def cmd_metainfo(args: argparse.Namespace) -> int:
    _import_package()
    from geekbench7_linux import APP_ID, APP_NAME
    from geekbench7_linux.credits import render_metainfo_paragraphs
    from geekbench7_linux.version import get_version

    text = _resolve_under_allowed(args.input).read_text(encoding="utf-8")
    paragraphs = "".join(f"    <p>{xml_escape(p)}</p>\n" for p in render_metainfo_paragraphs())
    rendered = (
        text.replace("@APP_ID@", APP_ID)
        .replace("@APP_NAME@", xml_escape(APP_NAME))
        .replace("@DESCRIPTION@", paragraphs.rstrip())
        .replace("@VERSION@", get_version())
    )
    out = _resolve_under_allowed(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    return 0


def cmd_check(_args: argparse.Namespace) -> int:
    """Cheap sanity check used by meson test suite data."""
    _import_package()
    from geekbench7_linux import APP_ID, APP_NAME
    from geekbench7_linux.credits import disclaimer, thank_you

    assert APP_ID.startswith("io.github.")
    assert "unofficial" in APP_NAME.lower()
    assert "Primate Labs" in thank_you()
    assert "NOT affiliated" in disclaimer()
    print("gen-data check ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_name = sub.add_parser("name")
    p_name.add_argument("key")
    p_name.set_defaults(func=cmd_name)

    p_bi = sub.add_parser("build-info")
    p_bi.add_argument("version")
    p_bi.add_argument("flavor")
    p_bi.add_argument("output")
    p_bi.set_defaults(func=cmd_build_info)

    p_desk = sub.add_parser("desktop")
    p_desk.add_argument("output")
    p_desk.set_defaults(func=cmd_desktop)

    p_meta = sub.add_parser("metainfo")
    p_meta.add_argument("input")
    p_meta.add_argument("output")
    p_meta.set_defaults(func=cmd_metainfo)

    p_check = sub.add_parser("check")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
