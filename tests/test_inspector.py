import pytest
from batchmark.inspector import inspect_report, SuiteInspection
from batchmark.runner import BenchmarkResult


def _result(suite: str, branch: str, duration: float, success: bool = True) -> BenchmarkResult:
    r = BenchmarkResult(suite=suite, branch=branch)
    r._success = success
    r._duration = duration
    return r


class FakeResult:
    def __init__(self, suite, branch, duration, success=True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _fr(suite, branch, duration, success=True):
    return FakeResult(suite, branch, duration, success)


def test_inspect_groups_by_suite():
    results = [_fr("a", "main", 1.0), _fr("b", "main", 2.0)]
    report = inspect_report(results, ["main"])
    assert len(report.inspections) == 2
    suites = {ins.suite for ins in report.inspections}
    assert suites == {"a", "b"}


def test_for_suite_returns_correct():
    results = [_fr("alpha", "main", 1.5)]
    report = inspect_report(results, ["main"])
    ins = report.for_suite("alpha")
    assert ins is not None
    assert ins.suite == "alpha"


def test_for_suite_missing_returns_none():
    report = inspect_report([], [])
    assert report.for_suite("nope") is None


def test_fastest_branch():
    results = [_fr("s", "main", 2.0), _fr("s", "dev", 1.0)]
    report = inspect_report(results, ["main", "dev"])
    ins = report.for_suite("s")
    assert ins.fastest() == "dev"


def test_slowest_branch():
    results = [_fr("s", "main", 2.0), _fr("s", "dev", 1.0)]
    report = inspect_report(results, ["main", "dev"])
    ins = report.for_suite("s")
    assert ins.slowest() == "main"


def test_spread():
    results = [_fr("s", "main", 3.0), _fr("s", "dev", 1.0)]
    report = inspect_report(results, ["main", "dev"])
    ins = report.for_suite("s")
    assert ins.spread() == pytest.approx(2.0)


def test_spread_single_branch_is_none():
    results = [_fr("s", "main", 1.0)]
    report = inspect_report(results, ["main"])
    ins = report.for_suite("s")
    assert ins.spread() is None


def test_failed_excluded_from_fastest():
    results = [_fr("s", "main", 0.1, success=False), _fr("s", "dev", 1.5)]
    report = inspect_report(results, ["main", "dev"])
    ins = report.for_suite("s")
    assert ins.fastest() == "dev"
