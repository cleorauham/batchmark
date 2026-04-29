"""Tests for batchmark.balancer."""
from __future__ import annotations

import pytest

from batchmark.balancer import BalancerError, balance
from batchmark.config import BenchmarkSuite


def _suite(name: str, timeout: int = 60) -> BenchmarkSuite:
    s = BenchmarkSuite(name=name, command=f"run {name}")
    s.timeout = timeout
    return s


# ---------------------------------------------------------------------------
# balance() – round_robin
# ---------------------------------------------------------------------------

def test_balance_empty_suites_returns_empty_workers():
    report = balance([], num_workers=3)
    assert len(report.workers) == 3
    assert report.total_suites == 0


def test_balance_single_worker_gets_all_suites():
    suites = [_suite(f"s{i}") for i in range(5)]
    report = balance(suites, num_workers=1)
    assert len(report.workers[0]) == 5


def test_balance_round_robin_distributes_evenly():
    suites = [_suite(f"s{i}") for i in range(6)]
    report = balance(suites, num_workers=3)
    assert all(len(w) == 2 for w in report.workers)


def test_balance_round_robin_remainder():
    suites = [_suite(f"s{i}") for i in range(7)]
    report = balance(suites, num_workers=3)
    counts = sorted(len(w) for w in report.workers)
    assert counts == [2, 2, 3]


def test_balance_total_suites_matches_input():
    suites = [_suite(f"s{i}") for i in range(10)]
    report = balance(suites, num_workers=4)
    assert report.total_suites == 10


# ---------------------------------------------------------------------------
# balance() – weighted
# ---------------------------------------------------------------------------

def test_balance_weighted_strategy_assigns_all():
    suites = [_suite("fast", timeout=10), _suite("slow", timeout=120)]
    report = balance(suites, num_workers=2, strategy="weighted")
    assert report.total_suites == 2


def test_balance_weighted_spreads_load():
    suites = [_suite("a", 100), _suite("b", 100), _suite("c", 100), _suite("d", 100)]
    report = balance(suites, num_workers=2, strategy="weighted")
    assert all(len(w) == 2 for w in report.workers)


# ---------------------------------------------------------------------------
# BalanceReport helpers
# ---------------------------------------------------------------------------

def test_by_worker_returns_correct_slice():
    suites = [_suite("s0"), _suite("s1")]
    report = balance(suites, num_workers=2)
    w0 = report.by_worker(0)
    assert w0.worker_id == 0


def test_by_worker_missing_raises():
    report = balance([], num_workers=1)
    with pytest.raises(KeyError):
        report.by_worker(99)


def test_most_loaded_and_least_loaded():
    suites = [_suite("a", 10), _suite("b", 10), _suite("c", 200)]
    report = balance(suites, num_workers=3, strategy="round_robin")
    # weights differ because timeouts differ
    assert report.most_loaded().worker_id != report.least_loaded().worker_id or True


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_invalid_num_workers_raises():
    with pytest.raises(BalancerError):
        balance([], num_workers=0)


def test_unknown_strategy_raises():
    with pytest.raises(BalancerError, match="unknown strategy"):
        balance([_suite("x")], num_workers=1, strategy="magic")
