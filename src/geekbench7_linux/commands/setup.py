"""setup: download and extract official Geekbench 7."""

from __future__ import annotations

import argparse

from ..context import AppContext
from ..install import setup_geekbench


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("setup", help="download and install official Geekbench 7")
    parser.add_argument(
        "--accept-eula",
        action="store_true",
        help="accept Geekbench terms / unofficial-wrapper consent before download",
    )
    parser.add_argument("--arch", default="", help="override arch (amd64/arm64)")
    parser.set_defaults(_handler=run)


def run(ctx: AppContext) -> int:
    binary = setup_geekbench(ctx.paths, accept_eula=bool(ctx.args.accept_eula), arch=str(ctx.args.arch or ""))
    if getattr(ctx.args, "json", False):
        ctx.print_json({"binary": str(binary), "status": "ok"})
    else:
        print(f"Geekbench ready: {binary}")
        print("Thank you to Primate Labs and John Poole for Geekbench.")
    return 0
