import pytest
from pathlib import Path
from batchmark.labeler import (
    LabelEntry, LabelError,
    save_label, load_label, list_labels, delete_label,
)


@pytest.fixture
def store(tmp_path):
    return tmp_path / "labels"


def test_save_creates_file(store):
    e = LabelEntry(run_id="run1", labels=["fast", "stable"])
    path = save_label(store, e)
    assert path.exists()


def test_save_and_load_roundtrip(store):
    e = LabelEntry(run_id="run2", labels=["nightly"], note="CI run")
    save_label(store, e)
    loaded = load_label(store, "run2")
    assert loaded.run_id == "run2"
    assert loaded.labels == ["nightly"]
    assert loaded.note == "CI run"


def test_load_missing_raises(store):
    with pytest.raises(LabelError):
        load_label(store, "nonexistent")


def test_list_empty(store):
    assert list_labels(store) == []


def test_list_returns_all(store):
    save_label(store, LabelEntry(run_id="a", labels=["x"]))
    save_label(store, LabelEntry(run_id="b", labels=["y"]))
    entries = list_labels(store)
    assert len(entries) == 2
    ids = {e.run_id for e in entries}
    assert ids == {"a", "b"}


def test_delete_existing(store):
    save_label(store, LabelEntry(run_id="del1", labels=[]))
    removed = delete_label(store, "del1")
    assert removed is True
    assert list_labels(store) == []


def test_delete_missing_returns_false(store):
    assert delete_label(store, "ghost") is False
