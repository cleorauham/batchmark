"""Tests for batchmark.validator."""
from __future__ import annotations

import pytest

from batchmark.runner import BenchmarkResult
from batchmark.comparator import SuiteComparison, ComparisonReport
from batchmark.validator import (
    ValidationRule,
    ValidationViolation,
    ValidationReport,
    validate_results,
    validate_report,
)


def _result(suite: str, branch: str, duration: float, success: bool = True) -> BenchmarkResult:
    return BenchmarkResult(suite=suite, branch=branch, duration=duration, success=success)


def _cmp(suite: str, delta_pct: float | None) -> SuiteComparison:
    return SuiteComparison(
        suite=suite,
        baseline_duration=1.0,
        candidate_duration=1.0 * (1 + (delta_pct or 0) / 100) if delta_pct is not None else None,
        delta_pct=delta_pct,
    )


# --- validate_results ---

def test_no_violations_when_within_limit():
    rules = [ValidationRule(suite="bench_a", max_duration=5.0)]
    results = [_result("bench_a", "main", 3.0)]
    report = validate_results(results, rules)
    assert report.passed
    assert report.violations == []


def test_violation_when_exceeds_max_duration():
    rules = [ValidationRule(suite="bench_a", max_duration=2.0)]
    results = [_result("bench_a", "main", 3.5)]
    report = validate_results(results, rules)
    assert report.failed
    assert len(report.violations) == 1
    v = report.violations[0]
    assert v.suite == "bench_a"
    assert v.rule == "max_duration"
    assert "3.500" in v.detail


def test_failed_results_skipped():
    rules = [ValidationRule(suite="bench_a", max_duration=1.0)]
    results = [_result("bench_a", "main", 99.0, success=False)]
    report = validate_results(results, rules)
    assert report.passed


def test_no_rule_for_suite_skipped():
    rules = [ValidationRule(suite="other", max_duration=1.0)]
    results = [_result("bench_a", "main", 99.0)]
    report = validate_results(results, rules)
    assert report.passed


# --- validate_report ---

def test_regression_within_limit_passes():
    rules = [ValidationRule(suite="bench_a", max_regression_pct=20.0)]
    comp_report = ComparisonReport(
        baseline="main", candidate="feat",
        comparisons=[_cmp("bench_a", 15.0)],
    )
    report = validate_report(comp_report, rules)
    assert report.passed


def test_regression_exceeds_limit_fails():
    rules = [ValidationRule(suite="bench_a", max_regression_pct=10.0)]
    comp_report = ComparisonReport(
        baseline="main", candidate="feat",
        comparisons=[_cmp("bench_a", 25.0)],
    )
    report = validate_report(comp_report, rules)
    assert report.failed
    assert report.violations[0].rule == "max_regression_pct"


def test_none_delta_pct_skipped():
    rules = [ValidationRule(suite="bench_a", max_regression_pct=5.0)]
    comp_report = ComparisonReport(
        baseline="main", candidate="feat",
        comparisons=[_cmp("bench_a", None)],
    )
    report = validate_report(comp_report, rules)
    assert report.passed


def test_violation_str_contains_suite():
    v = ValidationViolation(suite="s", branch="b", rule="max_duration", detail="too slow")
    assert "s" in str(v)
    assert "b" in str(v)
