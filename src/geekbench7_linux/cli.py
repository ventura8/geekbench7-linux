"""Argument parser and dispatch for geekbench7-linux / geekbench7."""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path

from . import APP_NAME, PACKAGE
from .commands import WRAPPER_COMMANDS
from .commands import run as run_cmd
from .context import AppContext
from .errors import Geekbench7LinuxError, UnsupportedEnv
from .version import get_version

# Flags consumed by the wrapper itself (not passed through to Geekbench).
# Note: -h/--help are *not* here so ``geekbench7 --help`` reaches Geekbench.
_WRAPPER_FLAGS = frozenset(
    {
        "--json",
        "--allow-root",
        "-v",
        "--verbose",
        "--accept-eula",
    }
)


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


def _register_wrapper_commands(sub: argparse._SubParsersAction) -> None:
    for name in WRAPPER_COMMANDS:
        module = importlib.import_module(f"geekbench7_linux.commands.{name}")
        module.register(sub)


def build_parser(prog: str = PACKAGE) -> argparse.ArgumentParser:
    """Build the management parser used by ``geekbench7-linux`` (wrapper commands only)."""
    parser = argparse.ArgumentParser(
        prog=Path(prog).name,
        description=f"{APP_NAME}: manage the official Geekbench 7 install (wrapper commands)",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {get_version()}")
    _add_global_options(parser)
    sub = parser.add_subparsers(dest="command", parser_class=_CommandParser)
    _register_wrapper_commands(sub)
    return parser


def _refuse_root(*, allow_root: bool) -> None:
    if os.geteuid() == 0 and not allow_root:
        raise UnsupportedEnv(
            "refusing to run as root",
            hint="re-run without sudo, or pass --allow-root if you understand the risk",
        )


def _normalize_passthrough_argv(args_list: list[str]) -> list[str]:
    """Insert ``--`` before the first Geekbench option so argparse does not eat it."""
    if not args_list or args_list[0] == "--":
        return args_list
    out: list[str] = []
    i = 0
    while i < len(args_list):
        arg = args_list[i]
        if arg in _WRAPPER_FLAGS:
            out.append(arg)
            i += 1
            continue
        out.append("--")
        out.extend(args_list[i:])
        return out
    return out


def _peel_wrapper_flags(argv: list[str]) -> tuple[list[str], list[str]]:
    """Split leading wrapper flags from the rest of argv."""
    flags: list[str] = []
    i = 0
    while i < len(argv) and argv[i] in _WRAPPER_FLAGS:
        flags.append(argv[i])
        i += 1
    return flags, argv[i:]


def _dispatch(args: argparse.Namespace) -> int:
    _refuse_root(allow_root=bool(getattr(args, "allow_root", False)))
    ctx = AppContext(args=args)
    handler = getattr(args, "_handler", None)
    if handler is None:
        return 2
    return int(handler(ctx))


def _main_wrapper(argv: list[str], prog: str) -> int:
    parser = build_parser(prog=prog)
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 2
    try:
        return _dispatch(args)
    except Geekbench7LinuxError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return int(exc.exit_code)


def _main_benchmark(argv: list[str], prog: str) -> int:
    flags, rest = _peel_wrapper_flags(argv)

    # ``geekbench7 [flags] wrapper …`` → management CLI.
    if rest and rest[0] == "wrapper":
        return _main_wrapper([*flags, *rest[1:]], prog=f"{Path(prog).name} wrapper")

    # Default: passthrough to official Geekbench (including ``--help`` / ``-h``).
    accept_eula = "--accept-eula" in flags
    allow_root = "--allow-root" in flags
    try:
        _refuse_root(allow_root=allow_root)
        return run_cmd.run_with_args(geekbench_args=list(rest), accept_eula=accept_eula)
    except Geekbench7LinuxError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return int(exc.exit_code)


def main(argv: list[str] | None = None, prog: str | None = None) -> int:
    """Entry point used by the launcher."""
    program = prog or PACKAGE
    basename = Path(program).name
    args_list = list(sys.argv[1:] if argv is None else argv)
    if basename == "geekbench7":
        return _main_benchmark(args_list, program)
    return _main_wrapper(args_list, program)
