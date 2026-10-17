"""Refuse gated real-network / E2E tests outside a container."""

from __future__ import annotations

import os
import sys
from pathlib import Path

SETTINGS_ALLOW = frozenset(
    {
        "GB_E2E_SETTINGS",
    }
)


def in_container() -> bool:
    """Return True when running inside Docker/Podman."""
    return Path("/.dockerenv").exists() or Path("/run/.containerenv").exists()


def _gated_env_vars() -> list[str]:
    found: list[str] = []
    for key, value in os.environ.items():
        if not value:
            continue
        if key in SETTINGS_ALLOW:
            continue
        if key.startswith("GB_E2E_") or key.startswith("GB_REAL_"):
            found.append(key)
    return found


def enforce() -> None:
    """Exit pytest if gated env vars are set outside a container."""
    gated = _gated_env_vars()
    if not gated:
        return
    if in_container():
        return
    sys.stderr.write(
        "error: gated real-tier / E2E env vars set outside a container: "
        + ", ".join(sorted(gated))
        + "\n"
        "hint: use scripts/e2e-docker.sh or scripts/qa/hardware-smoke.sh\n"
    )
    raise SystemExit(2)
