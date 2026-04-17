"""Tests for batchmark.notify_formatter."""
from __future__ import annotations
from batchmark.notifier import build_event
from batchmark.notify_formatter import format_event_summary
from batchmark.comparator import ComparisonReport, SuiteComparison
from batchmark.runner import BenchmarkResult


def _result(name: str, duration: float) -> BenchmarkResult:
    return BenchmarkResult(suite=name, branch="b", duration=duration, exit_code=0, output="")


def _report(pairs):
    comparisons = [
        SuiteComparison(suite=s, baseline=_result(s, b), candidate=_result(s, c))
        for s, b, c in pairs
    ]
    return ComparisonReport(branches=["main", "feat"], comparisons=comparisons)


def test_format_shows_branches():
    report = _report([("s1", 1.0, 1.0)])
    out = format_event_summary(build_event(report))
    assert "main" in out
    assert "feat" in out


def test_format_shows_regression_count():
    report = _report([("s1", 1.0, 2.0)])
    out = format_event_summary(build_event(report))
    assert "1" in out


def test_format_shows_total_suites():
    report = _report([("s1", 1.0, 1.0), ("s2", 1.0, 1.0), ("s3", 1.0, 1.0)])
    out = format_event_summary(build_event(report))
    assert "3" in out


def test_format_neutral_count():
    report = _report([("s1", 1.0, 1.0), ("s2", 1.0, 2.0)])
    out = format_event_summary(build_event(report))
    assert "Neutral" in out
