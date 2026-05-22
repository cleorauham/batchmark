"""Tests for batchmark.isolator."""

import pytest
from batchmark.isolator import isolate, IsolateReport
from batchmark.isolator_formatter import format_isolate_report


class _FakeResult:
    def __init__(self, suite, branch, duration, success=True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _r(suite, branch, duration, success=True):
    return _FakeResult(suite, branch, duration, success)


def test_isolate_empty_returns_empty_report():
    report = isolate([], "main", "dev")
    assert isinstance(report, IsolateReport)
    assert report.suites == []


def test_isolate_single_suite_no_anomaly():
    results = [
        _r("bench_a", "main", 1.0),
        _r("bench_a", "dev", 1.05),
    ]
    report = isolate(results, "main", "dev", threshold=0.2)
    assert len(report.suites) == 2
    assert not any(s.is_anomalous for s in report.suites)


def test_isolate_detects_anomaly():
    results = [
        _r("bench_slow", "main", 1.0),
        _r("bench_slow", "dev", 2.0),
    ]
    report = isolate(results, "main", "dev", threshold=0.2)
    assert len(report.anomalous()) == 2  # both branches flagged
    assert all(s.is_anomalous for s in report.suites)


def test_isolate_excludes_failed_results():
    results = [
        _r("bench_a", "main", 1.0, success=False),
        _r("bench_a", "dev", 1.0),
    ]
    report = isolate(results, "main", "dev")
    # main has no successful results so suite is skipped
    assert report.suites == []


def test_isolate_by_suite_filter():
    results = [
        _r("alpha", "main", 1.0),
        _r("alpha", "dev", 1.1),
        _r("beta", "main", 2.0),
        _r("beta", "dev", 2.1),
    ]
    report = isolate(results, "main", "dev")
    alpha_entries = report.by_suite("alpha")
    assert len(alpha_entries) == 2
    assert all(s.suite == "alpha" for s in alpha_entries)


def test_format_empty_returns_warning():
    report = IsolateReport(branch_a="main", branch_b="dev")
    out = format_isolate_report(report)
    assert "No isolation data" in out


def test_format_shows_branch_names():
    results = [
        _r("suite_x", "main", 1.0),
        _r("suite_x", "dev", 1.0),
    ]
    report = isolate(results, "main", "dev")
    out = format_isolate_report(report)
    assert "main" in out
    assert "dev" in out


def test_format_shows_anomaly_flag():
    results = [
        _r("slow_suite", "main", 1.0),
        _r("slow_suite", "dev", 5.0),
    ]
    report = isolate(results, "main", "dev", threshold=0.1)
    out = format_isolate_report(report)
    assert "ANOMALY" in out


def test_format_shows_no_anomaly_message():
    results = [
        _r("suite_a", "main", 1.0),
        _r("suite_a", "dev", 1.01),
    ]
    report = isolate(results, "main", "dev", threshold=0.5)
    out = format_isolate_report(report)
    assert "No anomalies detected" in out
