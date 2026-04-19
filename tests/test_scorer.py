"""Tests for batchmark.scorer."""
import pytest
from unittest.mock import MagicMock
from batchmark.scorer import score_report, ScoreReport, SuiteScore


def _result(branch: str, duration: float, success: bool = True):
    r = MagicMock()
    r.branch = branch
    r.duration = duration
    r.success = success
    return r


def _cmp(suite: str, results_by_branch):
    c = MagicMock()
    c.suite = suite
    c.results_by_branch = results_by_branch
    return c


def _report(branches, comparisons):
    r = MagicMock()
    r.branches = branches
    r.comparisons = comparisons
    return r


def test_score_single_branch():
    cmp = _cmp("bench_a", {"main": [_result("main", 2.0)]})
    report = _report(["main"], [cmp])
    sr = score_report(report)
    assert len(sr.scores) == 1
    assert sr.scores[0].suite == "bench_a"
    assert sr.scores[0].branch == "main"
    assert abs(sr.scores[0].weighted_score - 0.5) < 1e-9


def test_score_two_branches():
    cmp = _cmp("bench_a", {
        "main": [_result("main", 2.0)],
        "dev": [_result("dev", 1.0)],
    })
    report = _report(["main", "dev"], [cmp])
    sr = score_report(report)
    totals = sr.by_branch()
    assert totals["dev"] > totals["main"]


def test_weight_applied():
    cmp = _cmp("bench_a", {"main": [_result("main", 1.0)]})
    report = _report(["main"], [cmp])
    sr = score_report(report, weights={"bench_a": 3.0})
    assert abs(sr.scores[0].weighted_score - 3.0) < 1e-9


def test_failed_results_excluded():
    cmp = _cmp("bench_a", {"main": [_result("main", 1.0, success=False)]})
    report = _report(["main"], [cmp])
    sr = score_report(report)
    assert sr.scores == []


def test_multiple_runs_averaged():
    cmp = _cmp("bench_a", {"main": [
        _result("main", 1.0),
        _result("main", 3.0),
    ]})
    report = _report(["main"], [cmp])
    sr = score_report(report)
    assert abs(sr.scores[0].mean_duration - 2.0) < 1e-9


def test_total_sums_across_suites():
    c1 = _cmp("a", {"main": [_result("main", 1.0)]})
    c2 = _cmp("b", {"main": [_result("main", 4.0)]})
    report = _report(["main"], [c1, c2])
    sr = score_report(report)
    expected = 1.0 + 0.25
    assert abs(sr.total("main") - expected) < 1e-9
