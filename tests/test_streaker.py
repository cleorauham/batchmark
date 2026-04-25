"""Tests for batchmark.streaker."""

from __future__ import annotations

from batchmark.comparator import SuiteComparison, ComparisonReport
from batchmark.streaker import build_streaks, StreakReport


def _cmp(suite: str, baseline: float | None, candidate: float | None) -> SuiteComparison:
    cmp = SuiteComparison(suite=suite)
    cmp.baseline_mean = baseline
    cmp.candidate_mean = candidate
    return cmp


def _report(branch: str, *cmps: SuiteComparison) -> ComparisonReport:
    r = ComparisonReport(baseline_branch="main", candidate_branch=branch)
    r.comparisons = list(cmps)
    return r


def test_build_streaks_empty_returns_empty():
    result = build_streaks([])
    assert isinstance(result, StreakReport)
    assert result.entries == []


def test_single_report_streak_length_one():
    report = _report("feat", _cmp("suite_a", 1.0, 1.5))
    result = build_streaks([report])
    assert len(result.entries) == 1
    entry = result.entries[0]
    assert entry.suite == "suite_a"
    assert entry.branch == "feat"
    assert entry.kind == "regression"
    assert entry.length == 1


def test_consecutive_regressions_accumulate():
    r1 = _report("feat", _cmp("suite_a", 1.0, 1.5))
    r2 = _report("feat", _cmp("suite_a", 1.0, 2.0))
    r3 = _report("feat", _cmp("suite_a", 1.0, 2.5))
    result = build_streaks([r1, r2, r3])
    assert result.entries[0].length == 3
    assert result.entries[0].kind == "regression"


def test_streak_resets_on_kind_change():
    r1 = _report("feat", _cmp("suite_a", 1.0, 1.5))  # regression
    r2 = _report("feat", _cmp("suite_a", 1.0, 0.8))  # improvement
    result = build_streaks([r1, r2])
    entry = result.entries[0]
    assert entry.kind == "improvement"
    assert entry.length == 1


def test_improvements_filter():
    r1 = _report("feat", _cmp("a", 2.0, 1.0), _cmp("b", 1.0, 1.5))
    result = build_streaks([r1])
    improvements = result.improvements()
    regressions = result.regressions()
    assert len(improvements) == 1
    assert improvements[0].suite == "a"
    assert len(regressions) == 1
    assert regressions[0].suite == "b"


def test_longest_streak():
    r1 = _report("feat", _cmp("a", 1.0, 1.5), _cmp("b", 1.0, 1.2))
    r2 = _report("feat", _cmp("a", 1.0, 1.6), _cmp("b", 1.0, 0.9))
    r3 = _report("feat", _cmp("a", 1.0, 1.7), _cmp("b", 1.0, 0.8))
    result = build_streaks([r1, r2, r3])
    longest = result.longest()
    assert longest is not None
    assert longest.length == 3


def test_unchanged_when_equal_means():
    r1 = _report("feat", _cmp("suite_a", 1.0, 1.0))
    result = build_streaks([r1])
    assert result.entries[0].kind == "unchanged"


def test_multiple_branches_tracked_independently():
    r1 = _report("branch_x", _cmp("s", 1.0, 2.0))
    r2 = _report("branch_y", _cmp("s", 1.0, 2.0))
    result = build_streaks([r1, r2])
    branches = {e.branch for e in result.entries}
    assert "branch_x" in branches
    assert "branch_y" in branches
