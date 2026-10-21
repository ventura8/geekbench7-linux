"""desktop: install or remove a per-user menu entry."""

from __future__ import annotations

import argparse
from pathlib import Path

from .. import APP_ID, APP_NAME
from ..context import AppContext
from ..credits import render_desktop_comment
from ..errors import UsageError


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("desktop", help="install or remove a per-user .desktop entry")
    parser.add_argument("action", choices=("install", "remove"), help="install or remove")
    parser.set_defaults(_handler=run)


def _desktop_path() -> Path:
    home = Path.home()
    return home / ".local" / "share" / "applications" / f"{APP_ID}.desktop"


def _remove_desktop(ctx: AppContext, path: Path) -> None:
    if path.is_file():
        path.unlink()
    if getattr(ctx.args, "json", False):
        ctx.print_json({"status": "removed", "path": str(path)})
    else:
        print(f"removed {path}")


def _install_desktop(ctx: AppContext, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        [
            "[Desktop Entry]",
            "Type=Application",
            f"Name={APP_NAME}",
            f"Comment={render_desktop_comment()}",
            "Exec=geekbench7",
            "TryExec=geekbench7",
            f"Icon={APP_ID}",
            "Categories=System;Monitor;",
            "Terminal=true",
            "Keywords=benchmark;performance;CPU;GPU;Geekbench;",
            "Actions=doctor;about;",
            "",
            "[Desktop Action doctor]",
            "Name=Doctor",
            "Exec=geekbench7-linux doctor",
            "",
            "[Desktop Action about]",
            "Name=About",
            "Exec=geekbench7-linux about",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")
    if getattr(ctx.args, "json", False):
        ctx.print_json({"status": "installed", "path": str(path)})
    else:
        print(f"installed {path}")


def run(ctx: AppContext) -> int:
    path = _desktop_path()
    action = ctx.args.action
    if action == "remove":
        _remove_desktop(ctx, path)
    elif action == "install":
        _install_desktop(ctx, path)
    else:
        raise UsageError(f"unknown desktop action {action!r}")
    return 0
