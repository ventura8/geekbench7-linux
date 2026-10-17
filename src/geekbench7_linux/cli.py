"""Argument parser and dispatch for geekbench7-linux."""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path

from . import APP_NAME, PACKAGE
from .commands import COMMANDS
from .context import AppContext
from .errors import Geekbench7LinuxError, UnsupportedEnv
from .version import get_version


def _add_global_options(parser: argparse.ArgumentParser, *, suppress: bool = False) -> None:
    default = argparse.SUPPRESS if suppress else None
    parser.add_argument("--json", action="store_true", default=False if not suppress else default, help="JSON output")
    parser.add_argument(
        "--allow-root",
        action="store_true",
        default=False if not suppress else default,
        help="allow running as root (not recommended)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", default=False if not suppress else default)


class _CommandParser(argparse.ArgumentParser):
    """Subparser that re-adds global options with suppress defaults."""

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("conflict_handler", "resolve")
        super().__init__(*args, **kwargs)
        _add_global_options(self, suppress=True)


def build_parser(prog: str = PACKAGE) -> argparse.ArgumentParser:
    """Build the top-level argparse parser."""
    parser = argparse.ArgumentParser(
        prog=Path(prog).name,
        description=f"{APP_NAME}: install and launch official Geekbench 7",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {get_version()}")
    _add_global_options(parser)
    sub = parser.add_subparsers(dest="command", parser_class=_CommandParser)
    for name in COMMANDS:
        module = importlib.import_module(f"geekbench7_linux.commands.{name}")
        module.register(sub)
    return parser


def _refuse_root(args: argparse.Namespace) -> None:
    if os.geteuid() == 0 and not getattr(args, "allow_root", False):
        raise UnsupportedEnv(
            "refusing to run as root",
            hint="re-run without sudo, or pass --allow-root if you understand the risk",
        )


def main(argv: list[str] | None = None, prog: str | None = None) -> int:
    """Entry point used by the launcher."""
    program = prog or PACKAGE
    basename = Path(program).name
    parser = build_parser(prog=basename)
    args_list = list(sys.argv[1:] if argv is None else argv)
    # ``geekbench7`` alias defaults to run when no subcommand is given.
    if basename == "geekbench7" and (not args_list or args_list[0].startswith("-")):
        helpish = args_list and args_list[0] in {"-V", "--version", "-h", "--help"}
        if not helpish:
            args_list = ["run", "--", *args_list]
    args = parser.parse_args(args_list)
    if not getattr(args, "command", None):
        parser.print_help()
        return 2
    try:
        _refuse_root(args)
        ctx = AppContext(args=args)
        handler = args._handler
        return int(handler(ctx))
    except Geekbench7LinuxError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return int(exc.exit_code)
