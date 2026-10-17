"""version: print wrapper version."""

from __future__ import annotations

import argparse

from ..context import AppContext
from ..version import get_version


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("version", help="print geekbench7-linux version")
    parser.set_defaults(_handler=run)


def run(ctx: AppContext) -> int:
    ver = get_version()
    if getattr(ctx.args, "json", False):
        ctx.print_json({"version": ver})
    else:
        print(ver)
    return 0
