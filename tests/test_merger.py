"""Tests for batchmark.merger."""

import pytest
from batchmark.comparator import ComparisonReport, SuiteComparison
from batchmark.merger import merge_reports, MergeReport, MergeError


def _cmp(suite: str, baseline: float | None = 1.0, candidate: float | None = 1.2) -> SuiteComparison:
    delta = None
    if baseline is not None and candidate is not None:
        delta = (candidate - baseline) / baseline
    return SuiteComparison(
        suite_name=suite,
        baseline_duration=baseline,
        candidate_duration=candidate,
        delta_pct=delta,
    )


def _report(branches, *cmps) -> ComparisonReport:
    return ComparisonReport(branches=list(branches), comparisons=list(cmps))


def test_merge_empty_raises():
    with pytest.raises(MergeError):
        merge_reports([])


def test_merge_single_report():
    r = _report(["main", "feat"], _cmp("bench_a"), _cmp("bench_b"))
    merged = merge_reports([r])
    assert merged.total_suites() == 2
    assert "main" in merged.branches


def test_merge_two_reports_combines_suites():
    r1 = _report(["main", "feat-1"], _cmp("suite_x"))
    r2 = _report(["main", "feat-2"], _cmp("suite_y"))
    merged = merge_reports([r1, r2])
    assert merged.total_suites() == 2
    assert set(merged.all_suite_names()) == {"suite_x", "suite_y"}


def test_merge_deduplicates_branches():
    r1 = _report(["main", "feat-1"], _cmp("s"))
    r2 = _report(["main", "feat-2"], _cmp("s"))
    merged = merge_reports([r1, r2])
    assert merged.branches.count("main") == 1


def test_merge_collects_multiple_comparisons_per_suite():
    r1 = _report(["main", "a"], _cmp("bench"))
    r2 = _report(["main", "b"], _cmp("bench"))
    merged = merge_reports([r1, r2])
    assert len(merged.comparisons_for("bench")) == 2


def test_merge_suite_names_sorted():
    r = _report(["main", "dev"], _cmp("z_suite"), _cmp("a_suite"))
    merged = merge_reports([r])
    assert merged.all_suite_names() == ["a_suite", "z_suite"]


def test_merge_missing_suite_returns_empty():
    r = _report(["main", "dev"], _cmp("only_suite"))
    merged = merge_reports([r])
    assert merged.comparisons_for("nonexistent") == []
