"""uninstall: remove per-user Geekbench state."""

from __future__ import annotations

import argparse

from ..context import AppContext
from ..install import uninstall_user_state


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "uninstall",
        help="remove per-user Geekbench download and extract (keeps the system package)",
    )
    parser.add_argument("--yes", action="store_true", help="do not ask for confirmation")
    parser.set_defaults(_handler=run)


def run(ctx: AppContext) -> int:
    if not ctx.args.yes and not getattr(ctx.args, "json", False):
        answer = input("Remove per-user Geekbench install? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("aborted")
            return 1
    uninstall_user_state(ctx.paths)
    if getattr(ctx.args, "json", False):
        ctx.print_json({"status": "removed"})
    else:
        print("Per-user Geekbench state removed.")
    return 0
