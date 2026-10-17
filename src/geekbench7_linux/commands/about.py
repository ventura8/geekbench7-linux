"""about: credits and disclaimer."""

from __future__ import annotations

import argparse

from .. import APP_NAME
from ..context import AppContext
from ..credits import render_text
from ..version import get_version


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("about", help="credits, thanks and disclaimer")
    parser.set_defaults(_handler=run)


def run(ctx: AppContext) -> int:
    if getattr(ctx.args, "json", False):
        ctx.print_json({"app": APP_NAME, "wrapper_version": get_version()})
    else:
        print(f"{APP_NAME} {get_version()}")
        print()
        print(render_text(), end="")
    return 0
