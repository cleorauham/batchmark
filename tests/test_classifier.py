"""Tests for batchmark.classifier and batchmark.classifier_formatter."""
from __future__ import annotations

import pytest
from batchmark.classifier import (
    classify,
    ClassifierError,
    TIERS,
)
from batchmark.classifier_formatter import format_classify_report


class _R:
    """Minimal fake BenchmarkResult."""
    def __init__(self, suite, branch, duration, success=True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _r(suite="suite_a", branch="main", duration=0.1, success=True):
    return _R(suite, branch, duration, success)


# ---------------------------------------------------------------------------
# classify()
# ---------------------------------------------------------------------------

def test_classify_empty_returns_empty_buckets():
    report = classify([])
    assert report.total() == 0
    for tier in TIERS:
        assert len(report.buckets[tier]) == 0


def test_classify_fast_result():
    report = classify([_r(duration=0.2)])
    assert len(report.by_tier("fast")) == 1
    assert report.by_tier("moderate") is not None
    assert len(report.by_tier("moderate")) == 0


def test_classify_moderate_result():
    report = classify([_r(duration=1.5)])
    assert len(report.by_tier("moderate")) == 1


def test_classify_slow_result():
    report = classify([_r(duration=5.0)])
    assert len(report.by_tier("slow")) == 1


def test_classify_critical_result():
    report = classify([_r(duration=99.0)])
    assert len(report.by_tier("critical")) == 1


def test_classify_failed_result_excluded():
    report = classify([_r(duration=0.1, success=False)])
    assert report.total() == 0


def test_classify_multiple_results_distributed():
    results = [
        _r(suite="a", duration=0.1),
        _r(suite="b", duration=1.8),
        _r(suite="c", duration=7.0),
        _r(suite="d", duration=50.0),
    ]
    report = classify(results)
    assert report.total() == 4
    assert len(report.by_tier("fast")) == 1
    assert len(report.by_tier("moderate")) == 1
    assert len(report.by_tier("slow")) == 1
    assert len(report.by_tier("critical")) == 1


def test_classify_missing_threshold_raises():
    with pytest.raises(ClassifierError, match="fast"):
        classify([_r()], thresholds={"moderate": 2.0, "slow": 10.0})


def test_classify_suite_names_in_bucket():
    results = [_r(suite="alpha", duration=0.1), _r(suite="beta", duration=0.3)]
    report = classify(results)
    names = report.by_tier("fast").suite_names()
    assert "alpha" in names
    assert "beta" in names


# ---------------------------------------------------------------------------
# format_classify_report()
# ---------------------------------------------------------------------------

def test_format_shows_tier_headers():
    report = classify([_r(duration=0.1)])
    output = format_classify_report(report, color=False)
    assert "FAST" in output
    assert "MODERATE" in output


def test_format_shows_suite_name():
    report = classify([_r(suite="my_suite", duration=0.1)])
    output = format_classify_report(report, color=False)
    assert "my_suite" in output


def test_format_shows_total():
    results = [_r(duration=0.1), _r(suite="b", duration=1.5)]
    report = classify(results)
    output = format_classify_report(report, color=False)
    assert "Total classified: 2" in output
