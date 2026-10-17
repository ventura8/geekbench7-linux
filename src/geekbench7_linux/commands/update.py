"""update: refresh Geekbench from the CDN pin."""

from __future__ import annotations

import argparse

from ..context import AppContext
from ..install import update_geekbench


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("update", help="download the pinned Geekbench version again")
    parser.add_argument("--arch", default="", help="override arch (amd64/arm64)")
    parser.set_defaults(_handler=run)


def run(ctx: AppContext) -> int:
    binary = update_geekbench(ctx.paths, arch=str(ctx.args.arch or ""))
    if getattr(ctx.args, "json", False):
        ctx.print_json({"binary": str(binary), "status": "updated"})
    else:
        print(f"Geekbench updated: {binary}")
    return 0
