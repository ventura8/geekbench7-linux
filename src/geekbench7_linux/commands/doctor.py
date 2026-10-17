"""doctor: report install health."""

from __future__ import annotations

import argparse

from ..arch import detect_arch
from ..context import AppContext
from ..install import find_geekbench_binary, installed_info
from ..manifest import load_manifest


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("doctor", help="report Geekbench install status")
    parser.set_defaults(_handler=run)


def run(ctx: AppContext) -> int:
    paths = ctx.paths
    arch = detect_arch()
    man = load_manifest()
    pin = man.pin(arch)
    info = installed_info(paths)
    binary = ""
    try:
        binary = str(find_geekbench_binary(paths.geekbench_dir))
        status = "ok"
    except Exception as exc:
        status = f"missing: {exc}"
    payload = {
        "status": status,
        "host_arch": arch,
        "pinned_version": pin.version,
        "pinned_url": pin.url,
        "installed": info,
        "binary": binary,
        "paths": {
            "geekbench_dir": str(paths.geekbench_dir),
            "config": str(paths.config_file),
            "cache": str(paths.downloads_dir),
        },
    }
    if getattr(ctx.args, "json", False):
        ctx.print_json(payload)
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0 if status == "ok" else 1
