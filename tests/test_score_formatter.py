from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from batchmark.score_formatter import format_score_report
from batchmark.scorer import ScoreReport, SuiteScore


def _make_suite_score(total: float, suite_scores: dict, mean_duration: float):
    ss = MagicMock(spec=SuiteScore)
    ss.total = total
    ss.suite_scores = suite_scores
    ss.mean_duration = mean_duration
    return ss


def _make_report(by_branch: dict, best: str | None = None):
    r = MagicMock(spec=ScoreReport)
    r.by_branch = by_branch
    r.best_branch = best
    return r


def test_format_empty_returns_warning():
    report = _make_report({})
    out = format_score_report(report, color=False)
    assert "No score data" in out


def test_format_shows_branch_name():
    ss = _make_suite_score(0.95, {"bench_a": 0.95}, 1.23)
    report = _make_report({"main": ss}, best="main")
    out = format_score_report(report, color=False)
    assert "main" in out


def test_format_shows_score_value():
    ss = _make_suite_score(0.85, {"bench_a": 0.85}, 2.0)
    report = _make_report({"feature": ss}, best="feature")
    out = format_score_report(report, color=False)
    assert "0.8500" in out


def test_format_shows_best_branch():
    ss = _make_suite_score(0.99, {"s": 0.99}, 0.5)
    report = _make_report({"release": ss}, best="release")
    out = format_score_report(report, color=False)
    assert "Best branch" in out
    assert "release" in out


def test_format_ranks_highest_score_first():
    low = _make_suite_score(0.5, {"s": 0.5}, 3.0)
    high = _make_suite_score(0.95, {"s": 0.95}, 1.0)
    report = _make_report({"dev": low, "main": high}, best="main")
    out = format_score_report(report, color=False)
    idx_main = out.index("main")
    idx_dev = out.index("dev")
    assert idx_main < idx_dev


def test_format_no_color_has_no_escape_codes():
    ss = _make_suite_score(0.75, {"s": 0.75}, 1.5)
    report = _make_report({"main": ss}, best="main")
    out = format_score_report(report, color=False)
    assert "\033[" not in out
