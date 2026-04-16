"""Tests for batchmark.filter module."""

import pytest
from unittest.mock import MagicMock

from batchmark.filter import filter_suites, filter_report
from batchmark.comparator import ComparisonReport, SuiteComparison


def _make_suite(name: str):
    s = MagicMock()
    s.name = name
    return s


def _make_comparison(name: str, delta_pct: float | None):
    c = MagicMock(spec=SuiteComparison)
    c.suite_name = name
    c.delta_pct = delta_pct
    return c


def _make_report(comparisons):
    return ComparisonReport(
        baseline_branch="main",
        candidate_branch="dev",
        comparisons=comparisons,
    )


def test_filter_suites_include():
    suites = [_make_suite("a"), _make_suite("b"), _make_suite("c")]
    result = filter_suites(suites, include=["a", "c"])
    assert [s.name for s in result] == ["a", "c"]


def test_filter_suites_exclude():
    suites = [_make_suite("a"), _make_suite("b"), _make_suite("c")]
    result = filter_suites(suites, exclude=["b"])
    assert [s.name for s in result] == ["a", "c"]


def test_filter_suites_no_filter():
    suites = [_make_suite("x"), _make_suite("y")]
    assert filter_suites(suites) == suites


def test_filter_report_only_regressions():
    comps = [_make_comparison("a", 5.0), _make_comparison("b", -3.0), _make_comparison("c", 0.0)]
    report = _make_report(comps)
    filtered = filter_report(report, only_regressions=True)
    assert len(filtered.comparisons) == 1
    assert filtered.comparisons[0].suite_name == "a"


def test_filter_report_only_improvements():
    comps = [_make_comparison("a", 5.0), _make_comparison("b", -3.0)]
    report = _make_report(comps)
    filtered = filter_report(report, only_improvements=True)
    assert len(filtered.comparisons) == 1
    assert filtered.comparisons[0].suite_name == "b"


def test_filter_report_min_delta_pct():
    comps = [_make_comparison("a", 1.0), _make_comparison("b", 10.0), _make_comparison("c", -8.0)]
    report = _make_report(comps)
    filtered = filter_report(report, min_delta_pct=5.0)
    assert {c.suite_name for c in filtered.comparisons} == {"b", "c"}


def test_filter_report_conflict_raises():
    report = _make_report([])
    with pytest.raises(ValueError):
        filter_report(report, only_regressions=True, only_improvements=True)
