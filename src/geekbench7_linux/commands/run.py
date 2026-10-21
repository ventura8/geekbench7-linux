"""run: exec the official geekbench7 binary with passthrough args."""

from __future__ import annotations

import os
from collections.abc import Sequence

from ..context import AppContext
from ..errors import NotInstalled
from ..install import find_geekbench_binary, setup_geekbench


def run_with_args(
    *,
    geekbench_args: Sequence[str],
    accept_eula: bool = False,
    paths: object | None = None,
) -> int:
    """Exec Geekbench with ``geekbench_args`` (used by the ``geekbench7`` entrypoint)."""
    from ..paths import Paths

    resolved = paths if isinstance(paths, Paths) else Paths.from_env()
    try:
        binary = find_geekbench_binary(resolved.geekbench_dir)
    except NotInstalled:
        binary = setup_geekbench(resolved, accept_eula=accept_eula)
    args = list(geekbench_args)
    if args and args[0] == "--":
        args = args[1:]
    os.execv(str(binary), [str(binary), *args])
    raise RuntimeError("execv returned")


def run(ctx: AppContext) -> int:
    """Handler used by unit tests that build an ``AppContext`` for run."""
    return run_with_args(
        geekbench_args=list(getattr(ctx.args, "geekbench_args", None) or []),
        accept_eula=bool(getattr(ctx.args, "accept_eula", False)),
        paths=ctx.paths,
    )
