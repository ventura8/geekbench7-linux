"""Shared CLI context."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass

from .config import Config, load_config
from .paths import Paths


@dataclass
class AppContext:
    """Parsed args plus lazy paths/config."""

    args: argparse.Namespace

    @property
    def paths(self) -> Paths:
        return Paths.from_env()

    @property
    def config(self) -> Config:
        return load_config(self.paths)

    def print_json(self, payload: dict) -> None:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
