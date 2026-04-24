"""Tests for batchmark.throttler."""

from __future__ import annotations

import pytest

from batchmark.runner import BenchmarkResult
from batchmark.throttler import ThrottleError, throttle


def _result(suite: str, branch: str, duration: float = 1.0) -> BenchmarkResult:
    return BenchmarkResult(suite=suite, branch=branch, duration=duration, success=True)


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_throttle_no_limits_keeps_all():
    results = [_result("s1", "main"), _result("s1", "main"), _result("s2", "main")]
    report = throttle(results)
    assert report.total_kept == 3
    assert report.total_dropped == 0


def test_throttle_max_per_branch():
    results = [_result("s1", "main"), _result("s2", "main"), _result("s3", "main")]
    report = throttle(results, max_per_branch=2)
    assert report.total_kept == 2
    assert report.total_dropped == 1
    assert report.dropped[0].suite == "s3"


def test_throttle_max_per_suite():
    results = [
        _result("bench", "main"),
        _result("bench", "dev"),
        _result("bench", "feat"),
    ]
    report = throttle(results, max_per_suite=2)
    assert report.total_kept == 2
    assert report.total_dropped == 1


def test_throttle_combined_limits():
    results = [
        _result("s1", "main"),
        _result("s2", "main"),
        _result("s1", "dev"),
        _result("s2", "dev"),
    ]
    report = throttle(results, max_per_branch=1, max_per_suite=2)
    # max_per_branch=1: only first result per branch kept → main:s1, dev:s1
    assert report.total_kept == 2
    assert all(r.suite == "s1" for r in report.kept)


def test_throttle_empty_results():
    report = throttle([])
    assert report.total_kept == 0
    assert report.total_dropped == 0


# ---------------------------------------------------------------------------
# by_branch / by_suite grouping
# ---------------------------------------------------------------------------

def test_by_branch_groups_correctly():
    results = [_result("s1", "main"), _result("s2", "dev"), _result("s3", "main")]
    report = throttle(results)
    by_branch = report.by_branch()
    assert len(by_branch["main"]) == 2
    assert len(by_branch["dev"]) == 1


def test_by_suite_groups_correctly():
    results = [_result("alpha", "main"), _result("alpha", "dev"), _result("beta", "main")]
    report = throttle(results)
    by_suite = report.by_suite()
    assert len(by_suite["alpha"]) == 2
    assert len(by_suite["beta"]) == 1


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_invalid_max_per_branch_raises():
    with pytest.raises(ThrottleError, match="max_per_branch"):
        throttle([], max_per_branch=0)


def test_invalid_max_per_suite_raises():
    with pytest.raises(ThrottleError, match="max_per_suite"):
        throttle([], max_per_suite=-1)
