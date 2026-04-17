"""Tests for batchmark.tag_formatter."""

from batchmark.tagger import TagEntry
from batchmark.tag_formatter import format_tag_detail, format_tag_list


def test_format_list_empty() -> None:
    out = format_tag_list([], color=False)
    assert "No tags" in out


def test_format_list_shows_names() -> None:
    out = format_tag_list(["alpha", "beta"], color=False)
    assert "alpha" in out
    assert "beta" in out


def test_format_detail_shows_branch() -> None:
    entry = TagEntry(name="v1", branch="main", created_at="2024-01-01T00:00:00+00:00")
    out = format_tag_detail(entry, color=False)
    assert "main" in out
    assert "v1" in out


def test_format_detail_shows_meta() -> None:
    entry = TagEntry(
        name="v2",
        branch="dev",
        created_at="2024-01-01T00:00:00+00:00",
        meta={"env": "ci"},
    )
    out = format_tag_detail(entry, color=False)
    assert "env" in out
    assert "ci" in out


def test_format_detail_no_meta_section() -> None:
    entry = TagEntry(name="v3", branch="main", created_at="2024-01-01T00:00:00+00:00")
    out = format_tag_detail(entry, color=False)
    assert "Meta" not in out
