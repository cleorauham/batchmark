import pytest
from dataclasses import dataclass, field
from typing import Optional
from batchmark.grouper import group_by, group_by_prefix, group_by_branch, GroupReport
from batchmark.comparator import SuiteComparison
from batchmark.runner import BenchmarkResult


def _result(branch: str, duration: float = 1.0) -> BenchmarkResult:
    return BenchmarkResult(suite="s", branch=branch, duration=duration,
                           exit_code=0, stdout="", stderr="")


def _cmp(suite: str, summary: str = "ok", branch: str = "main") -> SuiteComparison:
    cand = _result(branch)
    base = _result("baseline")
    return SuiteComparison(suite=suite, baseline=base, candidate=cand, summary=summary)


def _report(cmps):
    from batchmark.comparator import ComparisonReport
    return ComparisonReport(baseline_branch="baseline", candidate_branch="main",
                            comparisons=cmps)


def test_group_by_prefix_single_group():
    report = _report([_cmp("api_latency"), _cmp("api_throughput")])
    grp = group_by_prefix(report, sep="_")
    assert "api" in grp.keys()
    assert len(grp.get("api").comparisons) == 2


def test_group_by_prefix_multiple_groups():
    report = _report([_cmp("api_latency"), _cmp("db_query"), _cmp("api_throughput")])
    grp = group_by_prefix(report)
    assert set(grp.keys()) == {"api", "db"}


def test_group_by_branch():
    c1 = _cmp("suite1", branch="feat-a")
    c2 = _cmp("suite2", branch="feat-b")
    c3 = _cmp("suite3", branch="feat-a")
    report = _report([c1, c2, c3])
    grp = group_by_branch(report)
    assert set(grp.keys()) == {"feat-a", "feat-b"}
    assert len(grp.get("feat-a").comparisons) == 2


def test_regression_count():
    report = _report([
        _cmp("api_a", summary="regression"),
        _cmp("api_b", summary="ok"),
        _cmp("api_c", summary="regression"),
    ])
    grp = group_by_prefix(report)
    assert grp.get("api").regression_count == 2


def test_improvement_count():
    report = _report([
        _cmp("db_fast", summary="improvement"),
        _cmp("db_slow", summary="ok"),
    ])
    grp = group_by_prefix(report)
    assert grp.get("db").improvement_count == 1


def test_empty_report():
    report = _report([])
    grp = group_by_prefix(report)
    assert grp.keys() == []


def test_suite_names():
    report = _report([_cmp("api_latency"), _cmp("api_throughput")])
    grp = group_by_prefix(report)
    assert set(grp.get("api").suite_names) == {"api_latency", "api_throughput"}
