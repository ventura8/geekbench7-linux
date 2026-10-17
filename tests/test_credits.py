"""Credits and disclaimer must stay intact across surfaces."""

from __future__ import annotations

from pathlib import Path

from geekbench7_linux.credits import (
    FOUNDER,
    LINKS,
    disclaimer,
    makers_text,
    render_consent,
    render_desktop_comment,
    render_metainfo_paragraphs,
    render_text,
    short_footer,
    thank_you,
)

ROOT = Path(__file__).resolve().parent.parent


def test_thank_you_names_makers() -> None:
    text = thank_you()
    assert FOUNDER in text
    assert makers_text() == "Primate Labs"
    assert "Primate Labs" in text


def test_disclaimer_not_affiliated() -> None:
    text = disclaimer()
    assert "NOT affiliated" in text
    assert LINKS["project_issues"] in text


def test_about_text_honours_geekbench() -> None:
    text = render_text()
    assert "John Poole" in text
    assert "Primate Labs" in text
    assert LINKS["buy"] in text
    assert "never redistributes" in text


def test_desktop_and_metainfo() -> None:
    comment = render_desktop_comment()
    assert "Primate Labs" in comment
    assert LINKS["buy"] in comment
    paragraphs = render_metainfo_paragraphs()
    joined = " ".join(paragraphs)
    assert "John Poole" in joined
    assert "not affiliated" in joined.lower()


def test_consent_mentions_terms() -> None:
    text = render_consent()
    assert "Primate Labs" in text
    assert "unofficial" in text.lower()


def test_docs_credits_file() -> None:
    path = ROOT / "docs" / "CREDITS.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "Primate Labs" in text
    assert "John Poole" in text
    assert short_footer().split("—")[0].strip() in text or "Geekbench" in text


def test_readme_credits_block() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Primate Labs" in text
    assert "John Poole" in text
    assert "not affiliated" in text.lower()
