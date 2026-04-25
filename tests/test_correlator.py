"""Tests for batchmark.correlator."""
import pytest
from batchmark.correlator import CorrelationPair, correlate, _pearson


class _FakeResult:
    def __init__(self, suite: str, branch: str, duration: float, success: bool = True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _r(suite, branch, duration, success=True):
    return _FakeResult(suite, branch, duration, success)


def test_pearson_perfect_positive():
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [2.0, 4.0, 6.0, 8.0]
    assert abs(_pearson(xs, ys) - 1.0) < 1e-9


def test_pearson_perfect_negative():
    xs = [1.0, 2.0, 3.0]
    ys = [3.0, 2.0, 1.0]
    assert abs(_pearson(xs, ys) + 1.0) < 1e-9


def test_pearson_too_short_returns_zero():
    assert _pearson([1.0], [1.0]) == 0.0
    assert _pearson([], []) == 0.0


def test_correlate_empty_results():
    report = correlate([], branch="main")
    assert report.branch == "main"
    assert report.pairs == []


def test_correlate_single_suite_no_pairs():
    results = [_r("bench-a", "main", 1.0), _r("bench-a", "main", 2.0)]
    report = correlate(results, branch="main")
    assert report.pairs == []


def test_correlate_excludes_failed():
    results = [
        _r("bench-a", "main", 1.0, success=False),
        _r("bench-b", "main", 2.0),
    ]
    report = correlate(results, branch="main")
    assert report.pairs == []


def test_correlate_excludes_other_branch():
    results = [
        _r("bench-a", "dev", 1.0),
        _r("bench-b", "dev", 2.0),
        _r("bench-a", "main", 1.0),
    ]
    report = correlate(results, branch="main")
    assert report.pairs == []


def test_correlate_produces_pair():
    results = [
        _r("bench-a", "main", 1.0),
        _r("bench-a", "main", 2.0),
        _r("bench-a", "main", 3.0),
        _r("bench-b", "main", 2.0),
        _r("bench-b", "main", 4.0),
        _r("bench-b", "main", 6.0),
    ]
    report = correlate(results, branch="main")
    assert len(report.pairs) == 1
    pair = report.pairs[0]
    assert pair.suite_a == "bench-a"
    assert pair.suite_b == "bench-b"
    assert abs(pair.coefficient - 1.0) < 1e-4


def test_verdict_strong_positive():
    p = CorrelationPair("a", "b", 0.95)
    assert p.verdict == "strong-positive"


def test_verdict_strong_negative():
    p = CorrelationPair("a", "b", -0.9)
    assert p.verdict == "strong-negative"


def test_verdict_weak():
    p = CorrelationPair("a", "b", 0.1)
    assert p.verdict == "weak"


def test_strong_pairs_filters_correctly():
    pairs = [
        CorrelationPair("a", "b", 0.9),
        CorrelationPair("a", "c", 0.5),
        CorrelationPair("b", "c", -0.85),
    ]
    from batchmark.correlator import CorrelationReport
    report = CorrelationReport(branch="main", pairs=pairs)
    strong = report.strong_pairs()
    assert len(strong) == 2
    assert all(abs(p.coefficient) >= 0.8 for p in strong)
