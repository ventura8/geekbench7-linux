"""E2E tests require GB_E2E* and a container (enforced globally)."""

from __future__ import annotations

import os

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("GB_E2E") != "1" and not any(
        os.environ.get(k) for k in ("GB_E2E_SMOKE", "GB_E2E_GEEKBENCH")
    ):
        skip = pytest.mark.skip(reason="E2E requires GB_E2E=1 in a container")
        for item in items:
            item.add_marker(skip)
