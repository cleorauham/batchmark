"""Tests for batchmark.deduplicator."""
from __future__ import annotations

import pytest

from batchmark.deduplicator import deduplicate, DeduplicateReport
from batchmark.runner import BenchmarkResult


def _result(
    suite: str = "bench_a",
    branch: str = "main",
    duration: float = 1.0,
    timestamp: float = 0.0,
    failed: bool = False,
) -> BenchmarkResult:
    r = BenchmarkResult(suite_name=suite, branch=branch, duration=duration)
    r.failed = failed
    r.timestamp = timestamp
    return r


def test_deduplicate_no_duplicates():
    results = [_result("a", "main"), _result("b", "main")]
    report = deduplicate(results)
    assert report.total_kept == 2
    assert report.total_removed == 0


def test_deduplicate_keeps_latest_by_timestamp():
    old = _result("bench_a", "main", duration=2.0, timestamp=100.0)
    new = _result("bench_a", "main", duration=1.0, timestamp=200.0)
    report = deduplicate([old, new])
    assert report.total_kept == 1
    assert report.total_removed == 1
    assert report.kept[0].duration == 1.0


def test_deduplicate_keeps_later_when_timestamps_equal():
    first = _result("bench_a", "main", duration=5.0, timestamp=50.0)
    second = _result("bench_a", "main", duration=3.0, timestamp=50.0)
    report = deduplicate([first, second])
    assert report.total_kept == 1
    assert report.kept[0].duration == 3.0


def test_deduplicate_different_branches_kept_separately():
    r1 = _result("bench_a", "main", timestamp=10.0)
    r2 = _result("bench_a", "feature", timestamp=10.0)
    report = deduplicate([r1, r2])
    assert report.total_kept == 2
    assert report.total_removed == 0


def test_deduplicate_preserves_insertion_order():
    ra = _result("z_suite", "main", timestamp=1.0)
    rb = _result("a_suite", "main", timestamp=1.0)
    report = deduplicate([ra, rb])
    assert [r.suite_name for r in report.kept] == ["z_suite", "a_suite"]


def test_deduplicate_removed_contains_discarded():
    old = _result("bench_a", "main", duration=9.0, timestamp=1.0)
    new = _result("bench_a", "main", duration=1.0, timestamp=2.0)
    report = deduplicate([old, new])
    assert len(report.removed) == 1
    assert report.removed[0].duration == 9.0


def test_deduplicate_empty_input():
    report = deduplicate([])
    assert report.total_kept == 0
    assert report.total_removed == 0


def test_deduplicate_unsupported_strategy_raises():
    with pytest.raises(ValueError, match="Unsupported keep strategy"):
        deduplicate([_result()], keep="oldest")
