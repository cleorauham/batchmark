"""Tests for batchmark.flattener."""
from __future__ import annotations

import pytest

from batchmark.comparator import ComparisonReport, SuiteComparison
from batchmark.flattener import FlatReport, FlatRow, flatten_report


def _cmp(suite: str, base: float | None, cand: float | None) -> SuiteComparison:
    if base is None or cand is None:
        delta = None
    else:
        delta = (cand - base) / base if base != 0 else None
    return SuiteComparison(suite_name=suite, baseline_mean=base, candidate_mean=cand, delta_pct=delta)


def _report(*cmps: SuiteComparison) -> ComparisonReport:
    return ComparisonReport(
        baseline_branch="main",
        candidate_branch="dev",
        comparisons=list(cmps),
    )


def test_flatten_empty_report():
    report = _report()
    flat = flatten_report(report)
    assert isinstance(flat, FlatReport)
    assert flat.rows == []


def test_flatten_preserves_suite_name():
    report = _report(_cmp("auth", 1.0, 1.0))
    flat = flatten_report(report)
    assert flat.rows[0].suite == "auth"


def test_flatten_preserves_branches():
    report = _report(_cmp("auth", 1.0, 1.0))
    flat = flatten_report(report)
    row = flat.rows[0]
    assert row.baseline_branch == "main"
    assert row.candidate_branch == "dev"


def test_flatten_regression_verdict():
    report = _report(_cmp("slow-suite", 1.0, 2.0))
    flat = flatten_report(report)
    assert flat.rows[0].verdict == "regression"


def test_flatten_improvement_verdict():
    report = _report(_cmp("fast-suite", 2.0, 1.0))
    flat = flatten_report(report)
    assert flat.rows[0].verdict == "improvement"


def test_flatten_unchanged_verdict():
    report = _report(_cmp("stable", 1.0, 1.0))
    flat = flatten_report(report)
    assert flat.rows[0].verdict == "unchanged"


def test_flatten_missing_verdict_when_no_baseline():
    report = _report(_cmp("new-suite", None, 1.5))
    flat = flatten_report(report)
    assert flat.rows[0].verdict == "missing"


def test_to_dicts_returns_list_of_dicts():
    report = _report(_cmp("auth", 1.0, 1.2))
    flat = flatten_report(report)
    dicts = flat.to_dicts()
    assert isinstance(dicts, list)
    assert isinstance(dicts[0], dict)
    assert "suite" in dicts[0]
    assert "verdict" in dicts[0]
    assert "delta_pct" in dicts[0]


def test_filter_verdict_keeps_matching_rows():
    report = _report(
        _cmp("a", 1.0, 2.0),  # regression
        _cmp("b", 2.0, 1.0),  # improvement
        _cmp("c", 1.0, 1.0),  # unchanged
    )
    flat = flatten_report(report)
    regressions = flat.filter_verdict("regression")
    assert len(regressions.rows) == 1
    assert regressions.rows[0].suite == "a"


def test_filter_verdict_empty_when_no_match():
    report = _report(_cmp("a", 1.0, 1.0))
    flat = flatten_report(report)
    result = flat.filter_verdict("regression")
    assert result.rows == []
