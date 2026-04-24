"""Tests for batchmark.aggregate_formatter."""

from __future__ import annotations

from unittest.mock import MagicMock

from batchmark.aggregator import aggregate, AggregateReport
from batchmark.aggregate_formatter import format_aggregate_report


def _result(suite: str, branch: str, duration: float, success: bool = True):
    r = MagicMock()
    r.suite = suite
    r.branch = branch
    r.duration = duration
    r.success = success
    return r


def _report():
    results = [
        _result("bench_login", "main", 0.42),
        _result("bench_login", "main", 0.45),
        _result("bench_query", "feature", 1.10),
    ]
    return aggregate(results)


def test_format_empty_report_shows_warning():
    report = AggregateReport(entries=[])
    output = format_aggregate_report(report)
    assert "No aggregated" in output


def test_format_shows_suite_name():
    output = format_aggregate_report(_report())
    assert "bench_login" in output
    assert "bench_query" in output


def test_format_shows_branch_name():
    output = format_aggregate_report(_report())
    assert "main" in output
    assert "feature" in output


def test_format_shows_run_count():
    output = format_aggregate_report(_report())
    # bench_login has 2 runs
    assert "2" in output


def test_format_shows_header_labels():
    output = format_aggregate_report(_report())
    assert "mean" in output
    assert "stdev" in output
    assert "median" in output


def test_format_shows_summary_line():
    output = format_aggregate_report(_report())
    assert "combination" in output
    assert "branch" in output
