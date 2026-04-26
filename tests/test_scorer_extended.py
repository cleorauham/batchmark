from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from batchmark.scorer import build_score_report, SuiteScore, ScoreReport


def _result(suite: str, branch: str, success: bool, duration: float):
    r = MagicMock()
    r.suite = suite
    r.branch = branch
    r.success = success
    r.duration = duration
    return r


def test_build_score_report_empty_returns_empty():
    report = build_score_report([])
    assert isinstance(report, ScoreReport)
    assert report.by_branch == {}
    assert report.best_branch is None


def test_build_score_report_single_result():
    results = [_result("bench_a", "main", True, 1.0)]
    report = build_score_report(results)
    assert "main" in report.by_branch
    ss = report.by_branch["main"]
    assert isinstance(ss, SuiteScore)
    assert ss.total > 0


def test_build_score_report_failed_excluded():
    results = [
        _result("bench_a", "main", True, 1.0),
        _result("bench_b", "main", False, 99.0),
    ]
    report = build_score_report(results)
    ss = report.by_branch["main"]
    assert "bench_b" not in ss.suite_scores


def test_build_score_report_best_branch_highest_score():
    results = [
        _result("bench_a", "fast", True, 0.5),
        _result("bench_a", "slow", True, 5.0),
    ]
    report = build_score_report(results)
    assert report.best_branch == "fast"


def test_build_score_report_mean_duration_correct():
    results = [
        _result("bench_a", "main", True, 2.0),
        _result("bench_b", "main", True, 4.0),
    ]
    report = build_score_report(results)
    ss = report.by_branch["main"]
    assert abs(ss.mean_duration - 3.0) < 1e-9


def test_build_score_report_multiple_branches_independent():
    results = [
        _result("bench_a", "main", True, 1.0),
        _result("bench_a", "dev", True, 2.0),
    ]
    report = build_score_report(results)
    assert "main" in report.by_branch
    assert "dev" in report.by_branch
    assert report.by_branch["main"].total != report.by_branch["dev"].total
