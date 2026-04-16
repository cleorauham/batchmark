"""Tests for batchmark.comparator."""
import pytest

from batchmark.comparator import compare_results
from batchmark.runner import BenchmarkResult


def _result(name: str, duration: float, success: bool = True) -> BenchmarkResult:
    return BenchmarkResult(
        suite_name=name,
        branch="branch",
        duration_seconds=duration,
        success=success,
        output="",
    )


def test_compare_improvement():
    baseline = [_result("suite_a", 10.0)]
    compare = [_result("suite_a", 8.0)]
    report = compare_results(baseline, compare, "main", "feature")
    assert len(report.comparisons) == 1
    c = report.comparisons[0]
    assert c.improved is True
    assert abs(c.delta_pct - (-20.0)) < 0.01


def test_compare_regression():
    baseline = [_result("suite_b", 5.0)]
    compare = [_result("suite_b", 6.5)]
    report = compare_results(baseline, compare, "main", "feature")
    c = report.comparisons[0]
    assert c.improved is False
    assert abs(c.delta_pct - 30.0) < 0.01


def test_missing_suite_in_compare():
    baseline = [_result("suite_a", 10.0), _result("suite_b", 5.0)]
    compare = [_result("suite_a", 9.0)]
    report = compare_results(baseline, compare, "main", "feature")
    names = [c.suite_name for c in report.comparisons]
    assert "suite_b" not in names
    assert "suite_a" in names


def test_failed_result_excluded():
    baseline = [_result("suite_a", 10.0)]
    compare = [_result("suite_a", 8.0, success=False)]
    report = compare_results(baseline, compare, "main", "feature")
    assert len(report.comparisons) == 0


def test_regressions_and_improvements_properties():
    baseline = [_result("fast", 1.0), _result("slow", 1.0)]
    compare = [_result("fast", 0.5), _result("slow", 2.0)]
    report = compare_results(baseline, compare, "main", "feature")
    assert len(report.improvements) == 1
    assert len(report.regressions) == 1
    assert report.improvements[0].suite_name == "fast"
    assert report.regressions[0].suite_name == "slow"
