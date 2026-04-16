"""Tests for batchmark.differ and batchmark.diff_formatter."""
import pytest
from unittest.mock import MagicMock

from batchmark.comparator import ComparisonReport, SuiteComparison
from batchmark.runner import BenchmarkResult
from batchmark.differ import diff_reports, SuiteDelta
from batchmark.diff_formatter import format_diff


def _result(duration: float, ok: bool = True) -> BenchmarkResult:
    r = MagicMock(spec=BenchmarkResult)
    r.duration_s = duration
    r.success = ok
    return r


def _report(comparisons: dict) -> ComparisonReport:
    r = MagicMock(spec=ComparisonReport)
    r.baseline_branch = "main"
    r.candidate_branch = "feature"
    r.comparisons = comparisons
    return r


def test_diff_no_change():
    comp = MagicMock(spec=SuiteComparison)
    comp.baseline_results = [_result(1.0), _result(1.0)]
    comp.candidate_results = [_result(1.0), _result(1.0)]
    diff = diff_reports(_report({"suite_a": comp}))
    assert len(diff.deltas) == 1
    assert diff.deltas[0].delta_pct == pytest.approx(0.0)


def test_diff_regression():
    comp = MagicMock(spec=SuiteComparison)
    comp.baseline_results = [_result(1.0)]
    comp.candidate_results = [_result(1.5)]
    diff = diff_reports(_report({"suite_b": comp}))
    assert diff.deltas[0].delta_pct == pytest.approx(50.0)
    assert len(diff.regressions) == 1
    assert len(diff.improvements) == 0


def test_diff_improvement():
    comp = MagicMock(spec=SuiteComparison)
    comp.baseline_results = [_result(2.0)]
    comp.candidate_results = [_result(1.0)]
    diff = diff_reports(_report({"suite_c": comp}))
    assert diff.deltas[0].delta_pct == pytest.approx(-50.0)
    assert len(diff.improvements) == 1


def test_diff_failed_results_excluded():
    comp = MagicMock(spec=SuiteComparison)
    comp.baseline_results = [_result(1.0, ok=False)]
    comp.candidate_results = [_result(1.0)]
    diff = diff_reports(_report({"suite_d": comp}))
    delta = diff.deltas[0]
    assert delta.baseline_mean is None
    assert delta.only_in_candidate is True
    assert delta.delta_pct is None


def test_format_diff_contains_branches():
    comp = MagicMock(spec=SuiteComparison)
    comp.baseline_results = [_result(1.0)]
    comp.candidate_results = [_result(0.8)]
    diff = diff_reports(_report({"suite_e": comp}))
    output = format_diff(diff)
    assert "main" in output
    assert "feature" in output
    assert "suite_e" in output


def test_format_diff_summary_line():
    comp = MagicMock(spec=SuiteComparison)
    comp.baseline_results = [_result(1.0)]
    comp.candidate_results = [_result(2.0)]
    diff = diff_reports(_report({"suite_f": comp}))
    output = format_diff(diff)
    assert "Regressions: 1" in output
    assert "Improvements: 0" in output
