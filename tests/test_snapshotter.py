"""Tests for batchmark.snapshotter."""
from __future__ import annotations

import pytest

from batchmark.snapshotter import SnapshotError, delete_snapshot, list_snapshots, load_snapshot, save_snapshot


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path / "snaps")


class _FakeReport:
    branches = ["main", "dev"]

    def __init__(self):
        self.comparisons = []


def _make_report():
    return _FakeReport()


# patch report_to_dict so we don't need a real report
import batchmark.snapshotter as _mod


@pytest.fixture(autouse=True)
def patch_serializer(monkeypatch):
    monkeypatch.setattr(_mod, "report_to_dict", lambda r: {"comparisons": [], "branches": r.branches})


def test_save_creates_file(store):
    report = _make_report()
    path = save_snapshot(store, "snap1", report)
    import os
    assert os.path.exists(path)


def test_save_and_load_roundtrip(store):
    report = _make_report()
    save_snapshot(store, "mysnap", report)
    entry = load_snapshot(store, "mysnap")
    assert entry.name == "mysnap"
    assert entry.branches == ["main", "dev"]


def test_load_missing_raises(store):
    with pytest.raises(SnapshotError):
        load_snapshot(store, "ghost")


def test_list_empty(store):
    assert list_snapshots(store) == []


def test_list_shows_names(store):
    report = _make_report()
    save_snapshot(store, "alpha", report)
    save_snapshot(store, "beta", report)
    names = list_snapshots(store)
    assert "alpha" in names
    assert "beta" in names


def test_delete_removes_file(store):
    report = _make_report()
    save_snapshot(store, "bye", report)
    delete_snapshot(store, "bye")
    assert list_snapshots(store) == []


def test_delete_missing_raises(store):
    with pytest.raises(SnapshotError):
        delete_snapshot(store, "nope")


def test_save_overwrites_existing(store):
    """Saving a snapshot with the same name should overwrite without error."""
    report = _make_report()
    save_snapshot(store, "dup", report)
    # Overwrite should not raise
    save_snapshot(store, "dup", report)
    # There should still be only one snapshot with that name
    names = list_snapshots(store)
    assert names.count("dup") == 1
