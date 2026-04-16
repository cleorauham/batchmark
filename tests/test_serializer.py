"""Tests for the JSON serializer."""
from unittest.mock import MagicMock

from batchmark.runner import BenchmarkResult
from batchmark.comparator import SuiteComparison, ComparisonReport
from batchmark.serializer import result_to_dict, suite_comparison_to_dict, report_to_dict


def _make_result(suite="bench", branch="main", duration=1.5, success=True):
    return BenchmarkResult(suite=suite, branch=branch, duration=duration, success=success, output="", error=None)


def test_result_to_dict_fields():
    r = _make_result()
    d = result_to_dict(r)
    assert d["suite"] == "bench"
    assert d["branch"] == "main"
    assert d["duration"] == 1.5
    assert d["success"] is True


def test_suite_comparison_to_dict():
    baseline = _make_result(branch="main", duration=2.0)
    candidate = _make_result(branch="feature", duration=1.5)
    cmp = SuiteComparison(suite="bench", baseline=baseline, candidate=candidate)
    d = suite_comparison_to_dict(cmp)
    assert d["suite"] == "bench"
    assert d["delta"] == cmp.delta
    assert d["delta_pct"] == cmp.delta_pct
    assert "summary" in d


def test_suite_comparison_missing_baseline():
    candidate = _make_result(branch="feature")
    cmp = SuiteComparison(suite="bench", baseline=None, candidate=candidate)
    d = suite_comparison_to_dict(cmp)
    assert d["baseline"] is None


def test_report_to_dict_structure():
    baseline = _make_result(branch="main", duration=2.0)
    candidate = _make_result(branch="feature", duration=2.5)
    cmp = SuiteComparison(suite="bench", baseline=baseline, candidate=candidate)
    report = ComparisonReport(
        baseline_branch="main",
        candidate_branch="feature",
        comparisons=[cmp],
    )
    d = report_to_dict(report)
    assert d["baseline_branch"] == "main"
    assert d["candidate_branch"] == "feature"
    assert len(d["comparisons"]) == 1
    assert "regressions" in d
    assert "improvements" in d
