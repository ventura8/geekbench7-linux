"""Typed errors and exit codes for geekbench7-linux."""

from __future__ import annotations


class Geekbench7LinuxError(Exception):
    """Base error; ``exit_code`` maps to the process exit status."""

    exit_code = 1

    def __init__(self, message: str, *, hint: str = "") -> None:
        super().__init__(message)
        self.hint = hint

    def __str__(self) -> str:
        text = super().__str__()
        if self.hint:
            return f"{text}\nhint: {self.hint}"
        return text


class UsageError(Geekbench7LinuxError):
    """Bad CLI arguments or missing required consent."""

    exit_code = 2


class UnsupportedEnv(Geekbench7LinuxError):
    """Unsupported architecture, root without --allow-root, etc."""

    exit_code = 3


class DownloadFailed(Geekbench7LinuxError):
    """Network or HTTP failure while downloading."""

    exit_code = 4


class IntegrityFailed(Geekbench7LinuxError):
    """URL policy, size or sha256 mismatch."""

    exit_code = 5


class NotInstalled(Geekbench7LinuxError):
    """Geekbench is not set up yet."""

    exit_code = 6


class ConfigError(Geekbench7LinuxError):
    """Invalid config or manifest."""

    exit_code = 7
