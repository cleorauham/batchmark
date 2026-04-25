"""Tests for batchmark.recommender."""
from __future__ import annotations

import pytest

from batchmark.runner import BenchmarkResult
from batchmark.comparator import SuiteComparison, ComparisonReport
from batchmark.recommender import build_recommendations, Recommendation


def _result(suite: str, branch: str, duration: float, success: bool = True) -> BenchmarkResult:
    return BenchmarkResult(
        suite_name=suite,
        branch=branch,
        duration=duration,
        success=success,
        output="",
    )


def _report(*cmps: SuiteComparison) -> ComparisonReport:
    return ComparisonReport(
        baseline_branch="main",
        candidate_branch="feature",
        comparisons=list(cmps),
    )


def _cmp(suite: str, base_dur: float, cand_dur: float) -> SuiteComparison:
    return SuiteComparison(
        suite_name=suite,
        baseline=_result(suite, "main", base_dur),
        candidate=_result(suite, "feature", cand_dur),
    )


def test_regression_triggers_investigate():
    report = _report(_cmp("slow_suite", 1.0, 1.25))
    recs = build_recommendations(report, investigate_threshold=10.0)
    assert len(recs.investigate) == 1
    assert recs.investigate[0].suite == "slow_suite"
    assert "25.0%" in recs.investigate[0].reason


def test_improvement_triggers_promote():
    report = _report(_cmp("fast_suite", 1.0, 0.80))
    recs = build_recommendations(report, promote_threshold=-10.0)
    assert len(recs.promote) == 1
    assert recs.promote[0].suite == "fast_suite"


def test_within_threshold_produces_no_recommendation():
    report = _report(_cmp("stable_suite", 1.0, 1.03))
    recs = build_recommendations(report, investigate_threshold=10.0, promote_threshold=-5.0)
    assert recs.recommendations == []


def test_missing_candidate_triggers_skip():
    cmp = SuiteComparison(
        suite_name="missing",
        baseline=_result("missing", "main", 1.0),
        candidate=None,
    )
    recs = build_recommendations(_report(cmp))
    assert len(recs.skip) == 1
    assert recs.skip[0].suite == "missing"


def test_failed_result_triggers_skip():
    cmp = SuiteComparison(
        suite_name="broken",
        baseline=_result("broken", "main", 1.0, success=True),
        candidate=_result("broken", "feature", 0.0, success=False),
    )
    recs = build_recommendations(_report(cmp))
    assert len(recs.skip) == 1


def test_by_kind_filters_correctly():
    report = _report(
        _cmp("s1", 1.0, 1.5),   # investigate
        _cmp("s2", 1.0, 0.7),   # promote
    )
    recs = build_recommendations(report, investigate_threshold=10.0, promote_threshold=-10.0)
    assert len(recs.investigate) == 1
    assert len(recs.promote) == 1
    assert len(recs.skip) == 0
