"""The single source of every credit, disclaimer and thank-you text.

Used by ``geekbench7-linux about``, the consent dialog, the ``.desktop`` comment,
the AppStream description, the README credits block and ``docs/CREDITS.md``.
``tests/test_credits.py`` fails when those drift apart.
"""

from __future__ import annotations

from . import APP_NAME

LINKS: dict[str, str] = {
    "website": "https://www.geekbench.com",
    "primatelabs": "https://www.primatelabs.com",
    "buy": "https://www.primatelabs.com/store/v7/",
    "download": "https://www.geekbench.com/download/linux/",
    "preview": "https://www.geekbench.com/preview/",
    "browser": "https://browser.geekbench.com",
    "project": "https://github.com/ventura8/geekbench7-linux",
    "project_issues": "https://github.com/ventura8/geekbench7-linux/issues",
}

MAKERS: tuple[str, ...] = ("Primate Labs",)
FOUNDER = "John Poole"
CDN_HOST = "cdn.geekbench.com"


def makers_text() -> str:
    """``Primate Labs``."""
    return MAKERS[0]


def disclaimer() -> str:
    """One sentence: not affiliated, report problems here."""
    return (
        f"{APP_NAME} is NOT affiliated with, endorsed by or supported by {makers_text()}; "
        f"report packaging problems to {LINKS['project_issues']}, not to Primate Labs."
    )


def short_footer() -> str:
    """Short attribution line for footers."""
    return f"Geekbench © {makers_text()} (founder {FOUNDER}) — {LINKS['buy']}"


def thank_you() -> str:
    """Honour Geekbench's makers."""
    return (
        f"Thank you to {FOUNDER} and everyone at {makers_text()} for creating Geekbench — "
        "the cross-platform benchmark that makes performance comparable across machines."
    )


def render_text() -> str:
    """The ``geekbench7-linux about`` screen (plain text)."""
    lines = [
        APP_NAME,
        "",
        "Installs and launches the official, unmodified Geekbench 7 for Linux.",
        f"Geekbench is made by {makers_text()}, founded by {FOUNDER}.",
        thank_you(),
        "",
        f"  Website:        {LINKS['website']}",
        f"  Primate Labs:   {LINKS['primatelabs']}",
        f"  Buy / license:  {LINKS['buy']}",
        "                  Geekbench is proprietary software. Please support Primate Labs",
        "                  by purchasing a license if you find it useful.",
        f"  Geekbench Browser: {LINKS['browser']}",
        f"  Linux download: {LINKS['download']}",
        "",
        "Disclaimer",
        f"  {APP_NAME} is NOT affiliated with, endorsed by or supported by",
        f"  {makers_text()}. Report packaging and wrapper problems to",
        f"  {LINKS['project_issues']} — not to Primate Labs.",
        "  If a problem is in Geekbench itself, contact Primate Labs through their site.",
        "",
        f"  This project downloads the official tarball from {CDN_HOST} on your machine",
        "  and never redistributes or patches Geekbench.",
        f"  Project: {LINKS['project']}",
        "",
        short_footer(),
    ]
    return "\n".join(lines) + "\n"


def render_desktop_comment() -> str:
    """The ``.desktop`` ``Comment=`` value: one line of at most 120 characters."""
    return (
        f"Unofficial packaging for Geekbench 7 by {makers_text()}. "
        f"Not affiliated. Buy Geekbench: {LINKS['buy']}"
    )


def render_metainfo_paragraphs() -> list[str]:
    """Plain-text paragraphs for the AppStream ``<description>`` (no raw URLs)."""
    return [
        f"{APP_NAME} downloads and launches the official, unmodified Geekbench 7 "
        "Linux build from Primate Labs' CDN, with a menu entry and an update command.",
        f"Geekbench is proprietary software made by {makers_text()} (founder {FOUNDER}). "
        f"Please buy a license at primatelabs.com/store/v7 if you find it useful. {thank_you()}",
        "This project is not affiliated with, endorsed by or supported by Primate Labs. "
        "It downloads the official tarball from the Geekbench CDN on your machine and never "
        "redistributes or patches Geekbench. Report problems with the wrapper on the "
        "project issue tracker.",
    ]


def render_consent() -> str:
    """First-run consent text before downloading Geekbench."""
    return "\n".join(
        [
            f"Before downloading Geekbench 7 from {CDN_HOST}:",
            "",
            thank_you(),
            "",
            f"Geekbench is proprietary software by {makers_text()}.",
            f"License / purchase: {LINKS['buy']}",
            "",
            disclaimer(),
            "",
            "By continuing you accept Geekbench's terms from Primate Labs",
            "and understand this wrapper is unofficial.",
        ]
    )
