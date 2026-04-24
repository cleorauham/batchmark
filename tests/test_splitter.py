"""Tests for batchmark.splitter."""
from __future__ import annotations

import pytest

from batchmark.comparator import ComparisonReport, SuiteComparison
from batchmark.runner import BenchmarkResult
from batchmark.splitter import SplitError, split_report


def _result(branch: str, suite: str, duration: float) -> BenchmarkResult:
    return BenchmarkResult.success(branch=branch, suite_name=suite, duration_s=duration)


def _make_report(
    baseline_branch: str = "main",
    candidate_branch: str = "feature",
    suites: list[tuple[str, float, float]] | None = None,
) -> ComparisonReport:
    """Build a minimal ComparisonReport."""
    if suites is None:
        suites = [("suite-a", 1.0, 1.2), ("suite-b", 2.0, 1.8)]
    comparisons = [
        SuiteComparison(
            suite_name=name,
            baseline=_result(baseline_branch, name, base_dur),
            candidate=_result(candidate_branch, name, cand_dur),
        )
        for name, base_dur, cand_dur in suites
    ]
    return ComparisonReport(
        baseline_branch=baseline_branch,
        candidate_branch=candidate_branch,
        comparisons=comparisons,
    )


def test_split_report_returns_two_slices():
    report = _make_report()
    split = split_report(report)
    assert set(split.slices.keys()) == {"main", "feature"}


def test_split_report_branch_metadata():
    report = _make_report(baseline_branch="stable", candidate_branch="dev")
    split = split_report(report)
    assert split.baseline_branch == "stable"
    assert split.candidate_branch == "dev"


def test_each_slice_contains_all_suites():
    report = _make_report()
    split = split_report(report)
    for branch_slice in split.slices.values():
        assert set(branch_slice.suite_names) == {"suite-a", "suite-b"}


def test_regression_count():
    # suite-a: candidate (1.2) > baseline (1.0) → regression
    # suite-b: candidate (1.8) < baseline (2.0) → improvement
    report = _make_report()
    split = split_report(report)
    assert split.for_branch("feature").regression_count == 1


def test_improvement_count():
    report = _make_report()
    split = split_report(report)
    assert split.for_branch("feature").improvement_count == 1


def test_for_branch_missing_raises():
    report = _make_report()
    split = split_report(report)
    with pytest.raises(SplitError, match="not found"):
        split.for_branch("nonexistent")


def test_split_empty_report_raises():
    report = ComparisonReport(
        baseline_branch="main",
        candidate_branch="feature",
        comparisons=[],
    )
    with pytest.raises(SplitError, match="empty"):
        split_report(report)
