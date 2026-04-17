import json
import pytest
from batchmark.archiver import (
    save_archive, load_archive, list_archives, delete_archive, ArchiveError
)


@pytest.fixture
def archive_dir(tmp_path):
    return str(tmp_path / "archives")


_report = {
    "branches": ["main", "feature"],
    "suites": [{"suite": "bench_sort", "verdict": "improvement", "delta_pct": -5.2}],
}


def test_save_creates_file(archive_dir):
    path = save_archive("run1", _report, archive_dir=archive_dir)
    assert path.exists()


def test_save_and_load_roundtrip(archive_dir):
    save_archive("run1", _report, archive_dir=archive_dir)
    data = load_archive("run1", archive_dir=archive_dir)
    assert data["name"] == "run1"
    assert data["report"]["branches"] == ["main", "feature"]


def test_load_missing_raises(archive_dir):
    with pytest.raises(ArchiveError, match="not found"):
        load_archive("nope", archive_dir=archive_dir)


def test_list_empty(archive_dir):
    result = list_archives(archive_dir=archive_dir)
    assert result == []


def test_list_shows_entries(archive_dir):
    save_archive("alpha", _report, archive_dir=archive_dir)
    save_archive("beta", _report, archive_dir=archive_dir)
    entries = list_archives(archive_dir=archive_dir)
    names = [e.name for e in entries]
    assert "alpha" in names
    assert "beta" in names


def test_list_entry_has_branches(archive_dir):
    save_archive("run1", _report, archive_dir=archive_dir)
    entries = list_archives(archive_dir=archive_dir)
    assert entries[0].branches == ["main", "feature"]


def test_delete_removes_file(archive_dir):
    save_archive("run1", _report, archive_dir=archive_dir)
    delete_archive("run1", archive_dir=archive_dir)
    with pytest.raises(ArchiveError):
        load_archive("run1", archive_dir=archive_dir)


def test_delete_missing_raises(archive_dir):
    with pytest.raises(ArchiveError, match="not found"):
        delete_archive("ghost", archive_dir=archive_dir)
