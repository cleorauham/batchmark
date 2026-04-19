import pytest
from batchmark.ranker import rank_report, RankReport
from batchmark.comparator import ComparisonReport, SuiteComparison
from batchmark.runner import BenchmarkResult


def _result(branch: str, suite: str, duration: float, success: bool = True) -> BenchmarkResult:
    r = BenchmarkResult(branch=branch, suite=suite, duration=duration)
    r._success = success
    return r


def _make_result(branch, suite, duration, ok=True):
    class R:
        pass
    r = R()
    r.branch = branch
    r.suite = suite
    r.duration = duration
    r.success = ok
    return r


def _make_report(branches, comparisons):
    r = ComparisonReport.__new__(ComparisonReport)
    r.branches = branches
    r.comparisons = comparisons
    return r


def _make_cmp(results_dict):
    c = SuiteComparison.__new__(SuiteComparison)
    c.results = results_dict
    return c


def test_rank_single_branch():
    r1 = _make_result("main", "s1", 1.0)
    r2 = _make_result("main", "s2", 3.0)
    cmp1 = _make_cmp({"main": r1})
    cmp2 = _make_cmp({"main": r2})
    report = _make_report(["main"], [cmp1, cmp2])
    rr = rank_report(report)
    assert len(rr.branches) == 1
    assert rr.branches[0].branch == "main"
    assert rr.branches[0].mean_duration == pytest.approx(2.0)
    assert rr.branches[0].rank == 1


def test_rank_orders_by_mean_duration():
    fast = _make_result("fast", "s1", 0.5)
    slow = _make_result("slow", "s1", 2.0)
    cmp1 = _make_cmp({"fast": fast, "slow": slow})
    report = _make_report(["fast", "slow"], [cmp1])
    rr = rank_report(report)
    assert rr.best().branch == "fast"
    assert rr.worst().branch == "slow"
    assert rr.best().rank == 1
    assert rr.worst().rank == 2


def test_failed_results_excluded():
    ok = _make_result("main", "s1", 1.0, ok=True)
    bad = _make_result("dev", "s1", 0.0, ok=False)
    cmp1 = _make_cmp({"main": ok, "dev": bad})
    report = _make_report(["main", "dev"], [cmp1])
    rr = rank_report(report)
    dev_rank = next(r for r in rr.branches if r.branch == "dev")
    assert dev_rank.suite_count == 0
    assert dev_rank.mean_duration == pytest.approx(0.0)


def test_empty_report():
    report = _make_report([], [])
    rr = rank_report(report)
    assert rr.best() is None
    assert rr.worst() is None
