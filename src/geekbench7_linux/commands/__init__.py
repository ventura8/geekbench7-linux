"""CLI subcommands."""

from __future__ import annotations

# Management commands for geekbench7-linux and ``geekbench7 wrapper …``.
WRAPPER_COMMANDS: list[str] = [
    "setup",
    "update",
    "doctor",
    "about",
    "uninstall",
    "desktop",
    "version",
]

# Backwards-compatible alias used by older imports/tests.
COMMANDS: list[str] = list(WRAPPER_COMMANDS)
