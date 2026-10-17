"""desktop: install or remove a per-user menu entry."""

from __future__ import annotations

import argparse
from pathlib import Path

from .. import APP_ID, APP_NAME
from ..context import AppContext
from ..credits import render_desktop_comment


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("desktop", help="install or remove a per-user .desktop entry")
    parser.add_argument("action", choices=("install", "remove"), help="install or remove")
    parser.set_defaults(_handler=run)


def _desktop_path() -> Path:
    home = Path.home()
    return home / ".local" / "share" / "applications" / f"{APP_ID}.desktop"


def run(ctx: AppContext) -> int:
    path = _desktop_path()
    if ctx.args.action == "remove":
        if path.is_file():
            path.unlink()
        if getattr(ctx.args, "json", False):
            ctx.print_json({"status": "removed", "path": str(path)})
        else:
            print(f"removed {path}")
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        [
            "[Desktop Entry]",
            "Type=Application",
            f"Name={APP_NAME}",
            f"Comment={render_desktop_comment()}",
            "Exec=geekbench7-linux run",
            "TryExec=geekbench7-linux",
            f"Icon={APP_ID}",
            "Categories=System;Monitor;",
            "Terminal=true",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")
    if getattr(ctx.args, "json", False):
        ctx.print_json({"status": "installed", "path": str(path)})
    else:
        print(f"installed {path}")
    return 0
