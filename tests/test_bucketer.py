"""Tests for batchmark.bucketer."""
from __future__ import annotations

import pytest

from batchmark.bucketer import bucket_results, BucketerError, _DEFAULT_THRESHOLDS


class _FakeResult:
    def __init__(self, suite: str, branch: str, duration: float, success: bool = True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _r(suite: str, duration: float, branch: str = "main", success: bool = True) -> _FakeResult:
    return _FakeResult(suite=suite, branch=branch, duration=duration, success=success)


def test_bucket_empty_results():
    report = bucket_results([], branch="main")
    assert report.total_results == 0
    assert all(len(b) == 0 for b in report.buckets)


def test_bucket_fast_result():
    results = [_r("suite_a", 0.05)]
    report = bucket_results(results, branch="main")
    fast = report.by_label("fast")
    assert fast is not None
    assert len(fast) == 1
    assert "suite_a" in fast.suite_names


def test_bucket_slow_result():
    results = [_r("suite_b", 5.0)]
    report = bucket_results(results, branch="main")
    slow = report.by_label("slow")
    assert slow is not None
    assert len(slow) == 1


def test_bucket_very_slow_result():
    results = [_r("suite_c", 99.0)]
    report = bucket_results(results, branch="main")
    vs = report.by_label("very_slow")
    assert vs is not None
    assert len(vs) == 1


def test_bucket_excludes_failed_results():
    results = [_r("suite_d", 0.01, success=False)]
    report = bucket_results(results, branch="main")
    assert report.total_results == 0


def test_bucket_filters_by_branch():
    results = [
        _r("suite_a", 0.05, branch="main"),
        _r("suite_b", 0.05, branch="dev"),
    ]
    report = bucket_results(results, branch="main")
    assert report.total_results == 1
    assert report.branch == "main"


def test_bucket_non_empty_helper():
    results = [_r("s1", 0.05), _r("s2", 0.5)]
    report = bucket_results(results, branch="main")
    non_empty = report.non_empty()
    labels = [b.label for b in non_empty]
    assert "fast" in labels
    assert "moderate" in labels


def test_bucket_no_thresholds_raises():
    with pytest.raises(BucketerError):
        bucket_results([], branch="main", thresholds=[])


def test_bucket_custom_thresholds():
    thresholds = [("low", 0.0, 1.0), ("high", 1.0, float("inf"))]
    results = [_r("s1", 0.5), _r("s2", 2.0)]
    report = bucket_results(results, branch="main", thresholds=thresholds)
    assert len(report.by_label("low")) == 1
    assert len(report.by_label("high")) == 1


def test_bucket_boundary_at_threshold():
    # 0.1 should fall in 'moderate' (min=0.1, max=1.0), not 'fast' (max=0.1)
    results = [_r("s1", 0.1)]
    report = bucket_results(results, branch="main")
    assert len(report.by_label("moderate")) == 1
    assert len(report.by_label("fast")) == 0
