import pytest
from batchmark.grouper import group_by_prefix, GroupReport, ResultGroup
from batchmark.group_formatter import format_group_report
from batchmark.comparator import SuiteComparison, ComparisonReport
from batchmark.runner import BenchmarkResult


def _result(branch: str = "main") -> BenchmarkResult:
    return BenchmarkResult(suite="s", branch=branch, duration=1.0,
                           exit_code=0, stdout="", stderr="")


def _cmp(suite: str, summary: str = "ok") -> SuiteComparison:
    return SuiteComparison(suite=suite, baseline=_result("base"),
                           candidate=_result("main"), summary=summary)


def _report(cmps):
    return ComparisonReport(baseline_branch="base", candidate_branch="main",
                            comparisons=cmps)


def test_format_empty_report():
    out = format_group_report(GroupReport())
    assert "No groups" in out


def test_format_shows_group_key():
    r = _report([_cmp("api_latency")])
    grp = group_by_prefix(r)
    out = format_group_report(grp)
    assert "api" in out


def test_format_shows_suite_name():
    r = _report([_cmp("api_latency")])
    grp = group_by_prefix(r)
    out = format_group_report(grp)
    assert "api_latency" in out


def test_format_shows_regression_count():
    r = _report([_cmp("api_a", "regression"), _cmp("api_b", "ok")])
    grp = group_by_prefix(r)
    out = format_group_report(grp)
    assert "Regressions" in out


def test_format_multiple_groups_sorted():
    r = _report([_cmp("z_suite"), _cmp("a_suite")])
    grp = group_by_prefix(r)
    out = format_group_report(grp)
    assert out.index("a") < out.index("z")
