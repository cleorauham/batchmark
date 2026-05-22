"""Tests for batchmark.reducer."""
from __future__ import annotations

import pytest

from batchmark.reducer import ReducerError, ReduceReport, reduce


class _FakeResult:
    def __init__(self, suite: str, branch: str, duration: float, success: bool = True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _r(suite="bench", branch="main", duration=1.0, success=True):
    return _FakeResult(suite, branch, duration, success)


# ---------------------------------------------------------------------------
# reduce()
# ---------------------------------------------------------------------------

def test_reduce_empty_returns_empty_report():
    report = reduce([])
    assert isinstance(report, ReduceReport)
    assert report.results == []


def test_reduce_single_result_mean():
    report = reduce([_r(duration=2.5)], strategy="mean")
    assert len(report.results) == 1
    assert report.results[0].duration == pytest.approx(2.5)
    assert report.results[0].sample_size == 1


def test_reduce_multiple_results_mean():
    results = [_r(duration=1.0), _r(duration=3.0)]
    report = reduce(results, strategy="mean")
    assert len(report.results) == 1
    assert report.results[0].duration == pytest.approx(2.0)
    assert report.results[0].sample_size == 2


def test_reduce_strategy_min():
    results = [_r(duration=1.0), _r(duration=5.0), _r(duration=3.0)]
    report = reduce(results, strategy="min")
    assert report.results[0].duration == pytest.approx(1.0)


def test_reduce_strategy_max():
    results = [_r(duration=1.0), _r(duration=5.0), _r(duration=3.0)]
    report = reduce(results, strategy="max")
    assert report.results[0].duration == pytest.approx(5.0)


def test_reduce_strategy_median_odd():
    results = [_r(duration=1.0), _r(duration=3.0), _r(duration=5.0)]
    report = reduce(results, strategy="median")
    assert report.results[0].duration == pytest.approx(3.0)


def test_reduce_failed_results_excluded():
    results = [_r(duration=2.0), _r(duration=99.0, success=False)]
    report = reduce(results)
    assert report.results[0].duration == pytest.approx(2.0)
    assert report.results[0].sample_size == 1


def test_reduce_groups_by_suite_and_branch():
    results = [
        _r(suite="a", branch="main", duration=1.0),
        _r(suite="b", branch="main", duration=2.0),
        _r(suite="a", branch="dev", duration=4.0),
    ]
    report = reduce(results)
    assert len(report.results) == 3
    assert set(report.suite_names) == {"a", "b"}
    assert set(report.branches) == {"main", "dev"}


def test_reduce_unknown_strategy_raises():
    with pytest.raises(ReducerError, match="Unknown strategy"):
        reduce([_r()], strategy="geometric")


def test_reduce_report_strategy_stored():
    report = reduce([_r()], strategy="min")
    assert report.strategy == "min"


def test_reduce_by_branch_filters_correctly():
    results = [
        _r(branch="main", duration=1.0),
        _r(branch="dev", duration=2.0),
    ]
    report = reduce(results)
    main_results = report.by_branch("main")
    assert len(main_results) == 1
    assert main_results[0].branch == "main"
