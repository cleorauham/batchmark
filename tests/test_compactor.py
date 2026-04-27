"""Tests for batchmark.compactor."""
import pytest
from batchmark.compactor import CompactEntry, compact, CompactError


def _e(suite: str, branch: str, duration: float = 1.0, passed: bool = True, ts: str = "2024-01-01T00:00:00") -> CompactEntry:
    return CompactEntry(suite=suite, branch=branch, duration=duration, passed=passed, timestamp=ts)


def test_compact_empty_raises():
    with pytest.raises(CompactError):
        compact([])


def test_compact_single_list_no_duplicates():
    entries = [_e("suite_a", "main"), _e("suite_b", "main")]
    report = compact([entries])
    assert report.total_kept == 2
    assert report.total_removed == 0
    assert report.sources_merged == 1


def test_compact_removes_duplicate_keeps_latest():
    old = _e("suite_a", "main", duration=2.0, ts="2024-01-01T00:00:00")
    new = _e("suite_a", "main", duration=1.0, ts="2024-01-02T00:00:00")
    report = compact([[old], [new]])
    assert report.total_kept == 1
    assert report.total_removed == 1
    kept = report.entries[0]
    assert kept.duration == 1.0


def test_compact_different_branches_kept_separately():
    entries = [
        _e("suite_a", "main"),
        _e("suite_a", "dev"),
    ]
    report = compact([entries])
    assert report.total_kept == 2


def test_compact_sources_merged_count():
    a = [_e("s1", "main")]
    b = [_e("s2", "main")]
    c = [_e("s3", "main")]
    report = compact([a, b, c])
    assert report.sources_merged == 3


def test_compact_by_branch():
    entries = [
        _e("suite_a", "main"),
        _e("suite_b", "dev"),
        _e("suite_c", "main"),
    ]
    report = compact([entries])
    by_branch = report.by_branch()
    assert len(by_branch["main"]) == 2
    assert len(by_branch["dev"]) == 1


def test_compact_by_suite():
    entries = [
        _e("suite_a", "main"),
        _e("suite_a", "dev"),
        _e("suite_b", "main"),
    ]
    report = compact([entries])
    by_suite = report.by_suite()
    assert len(by_suite["suite_a"]) == 2
    assert len(by_suite["suite_b"]) == 1


def test_compact_equal_timestamps_keeps_last_seen():
    ts = "2024-06-01T12:00:00"
    first = _e("suite_a", "main", duration=3.0, ts=ts)
    second = _e("suite_a", "main", duration=1.5, ts=ts)
    report = compact([[first, second]])
    assert report.total_kept == 1
    assert report.entries[0].duration == 1.5
