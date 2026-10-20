"""run: exec the official geekbench7 binary with passthrough args."""

from __future__ import annotations

import argparse
import os

from ..context import AppContext
from ..errors import NotInstalled
from ..install import find_geekbench_binary, setup_geekbench


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "run",
        help="run official geekbench7 (passthrough: run --gpu CUDA, or run -- …)",
    )
    parser.add_argument(
        "geekbench_args",
        nargs=argparse.REMAINDER,
        help="args passed to geekbench7 (use -- before options if needed)",
    )
    parser.add_argument("--accept-eula", action="store_true", help="accept consent if setup is needed")
    parser.set_defaults(_handler=run)


def run(ctx: AppContext) -> int:
    paths = ctx.paths
    try:
        binary = find_geekbench_binary(paths.geekbench_dir)
    except NotInstalled:
        binary = setup_geekbench(paths, accept_eula=bool(ctx.args.accept_eula))
    args = list(ctx.args.geekbench_args or [])
    if args and args[0] == "--":
        args = args[1:]
    os.execv(str(binary), [str(binary), *args])
    raise RuntimeError("execv returned")

