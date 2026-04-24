"""Tests for batchmark.aggregator."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from batchmark.aggregator import aggregate, AggregateReport, AggregatedSuite


def _result(suite: str, branch: str, duration: float | None, success: bool = True):
    r = MagicMock()
    r.suite = suite
    r.branch = branch
    r.duration = duration
    r.success = success
    return r


def test_aggregate_empty_returns_empty_report():
    report = aggregate([])
    assert isinstance(report, AggregateReport)
    assert report.entries == []


def test_aggregate_single_result():
    results = [_result("bench_a", "main", 1.5)]
    report = aggregate(results)
    assert len(report.entries) == 1
    e = report.entries[0]
    assert e.suite == "bench_a"
    assert e.branch == "main"
    assert e.runs == 1
    assert e.mean == pytest.approx(1.5)
    assert e.stdev == pytest.approx(0.0)
    assert e.failed_runs == 0


def test_aggregate_multiple_runs_same_suite_branch():
    results = [
        _result("bench_a", "main", 1.0),
        _result("bench_a", "main", 2.0),
        _result("bench_a", "main", 3.0),
    ]
    report = aggregate(results)
    assert len(report.entries) == 1
    e = report.entries[0]
    assert e.runs == 3
    assert e.mean == pytest.approx(2.0)
    assert e.min_duration == pytest.approx(1.0)
    assert e.max_duration == pytest.approx(3.0)


def test_aggregate_failed_results_counted_separately():
    results = [
        _result("bench_a", "main", 1.0, success=True),
        _result("bench_a", "main", None, success=False),
        _result("bench_a", "main", None, success=False),
    ]
    report = aggregate(results)
    e = report.entries[0]
    assert e.runs == 1
    assert e.failed_runs == 2
    assert e.success_rate == pytest.approx(1 / 3)


def test_aggregate_all_failed_produces_zero_mean():
    results = [_result("bench_a", "main", None, success=False)]
    report = aggregate(results)
    e = report.entries[0]
    assert e.runs == 0
    assert e.mean == 0.0
    assert e.success_rate == 0.0


def test_aggregate_groups_by_branch():
    results = [
        _result("bench_a", "main", 1.0),
        _result("bench_a", "feature", 2.0),
    ]
    report = aggregate(results)
    assert len(report.entries) == 2
    branches = {e.branch for e in report.entries}
    assert branches == {"main", "feature"}


def test_aggregate_report_by_branch_filter():
    results = [
        _result("bench_a", "main", 1.0),
        _result("bench_b", "feature", 2.0),
    ]
    report = aggregate(results)
    main_entries = report.by_branch("main")
    assert len(main_entries) == 1
    assert main_entries[0].branch == "main"


def test_aggregate_report_suite_names_and_branches():
    results = [
        _result("alpha", "main", 1.0),
        _result("beta", "main", 2.0),
        _result("alpha", "dev", 1.5),
    ]
    report = aggregate(results)
    assert set(report.suite_names()) == {"alpha", "beta"}
    assert set(report.branches()) == {"main", "dev"}
