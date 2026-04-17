"""Tests for batchmark.tagger."""

import pytest
from pathlib import Path

from batchmark.tagger import (
    TaggerError,
    delete_tag,
    list_tags,
    load_tag,
    save_tag,
)


@pytest.fixture
def tag_dir(tmp_path: Path) -> Path:
    return tmp_path / "tags"


def test_save_creates_file(tag_dir: Path) -> None:
    path = save_tag("v1", "main", base=tag_dir)
    assert path.exists()


def test_save_and_load_roundtrip(tag_dir: Path) -> None:
    save_tag("release", "feat/x", meta={"note": "ok"}, base=tag_dir)
    entry = load_tag("release", base=tag_dir)
    assert entry.name == "release"
    assert entry.branch == "feat/x"
    assert entry.meta["note"] == "ok"


def test_load_missing_raises(tag_dir: Path) -> None:
    with pytest.raises(TaggerError, match="not found"):
        load_tag("ghost", base=tag_dir)


def test_list_tags_empty(tag_dir: Path) -> None:
    assert list_tags(base=tag_dir) == []


def test_list_tags_returns_names(tag_dir: Path) -> None:
    save_tag("b", "main", base=tag_dir)
    save_tag("a", "dev", base=tag_dir)
    assert list_tags(base=tag_dir) == ["a", "b"]


def test_delete_tag(tag_dir: Path) -> None:
    save_tag("tmp", "main", base=tag_dir)
    delete_tag("tmp", base=tag_dir)
    assert "tmp" not in list_tags(base=tag_dir)


def test_delete_missing_raises(tag_dir: Path) -> None:
    with pytest.raises(TaggerError):
        delete_tag("nope", base=tag_dir)
