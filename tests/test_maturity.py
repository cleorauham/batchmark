"""Tests for batchmark.maturity and batchmark.maturity_formatter."""
import pytest
from unittest.mock import MagicMock

from batchmark.maturity import (
    SuiteMaturity,
    MaturityReport,
    build_maturity_report,
    _verdict,
    _stdev,
)
from batchmark.maturity_formatter import format_maturity_report


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _agg(suite="bench", branch="main", total=5, success_rate=1.0, durations=None):
    a = MagicMock()
    a.suite = suite
    a.branch = branch
    a.total_runs = total
    a.success_rate = success_rate
    a.durations = durations if durations is not None else [1.0, 1.0, 1.0, 1.0, 1.0]
    return a


def _report(suites):
    r = MagicMock()
    r.suites = suites
    return r


# ---------------------------------------------------------------------------
# _stdev
# ---------------------------------------------------------------------------

def test_stdev_single_value_returns_zero():
    assert _stdev([5.0]) == 0.0


def test_stdev_identical_values_returns_zero():
    assert _stdev([3.0, 3.0, 3.0]) == pytest.approx(0.0)


def test_stdev_known_values():
    result = _stdev([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert result == pytest.approx(2.0, rel=1e-3)


# ---------------------------------------------------------------------------
# _verdict
# ---------------------------------------------------------------------------

def test_verdict_stable():
    assert _verdict(1.0, 0.1) == "stable"


def test_verdict_unstable_high_cv():
    assert _verdict(1.0, 0.5) == "unstable"


def test_verdict_flaky_low_success_rate():
    assert _verdict(0.5, 0.05) == "flaky"


# ---------------------------------------------------------------------------
# build_maturity_report
# ---------------------------------------------------------------------------

def test_build_maturity_empty_report():
    report = build_maturity_report(_report([]))
    assert report.entries == []


def test_build_maturity_stable_suite():
    agg = _agg(durations=[1.0, 1.0, 1.0, 1.0, 1.0], success_rate=1.0)
    report = build_maturity_report(_report([agg]))
    assert len(report.entries) == 1
    e = report.entries[0]
    assert e.verdict == "stable"
    assert e.cv == pytest.approx(0.0)
    assert e.success_rate == 1.0


def test_build_maturity_flaky_suite():
    agg = _agg(durations=[1.0, 2.0], success_rate=0.4)
    report = build_maturity_report(_report([agg]))
    assert report.entries[0].verdict == "flaky"


def test_build_maturity_unstable_suite():
    agg = _agg(durations=[1.0, 10.0, 1.0, 10.0], success_rate=1.0)
    report = build_maturity_report(_report([agg]))
    assert report.entries[0].verdict == "unstable"


def test_maturity_report_grouping():
    entries = [
        SuiteMaturity("a", "main", 5, 1.0, 0.05, "stable"),
        SuiteMaturity("b", "main", 5, 0.5, 0.05, "flaky"),
        SuiteMaturity("c", "main", 5, 1.0, 0.4, "unstable"),
    ]
    r = MaturityReport(entries=entries)
    assert len(r.stable()) == 1
    assert len(r.flaky()) == 1
    assert len(r.unstable()) == 1


# ---------------------------------------------------------------------------
# formatter
# ---------------------------------------------------------------------------

def test_format_empty_returns_no_data():
    out = format_maturity_report(MaturityReport())
    assert "no maturity data" in out


def test_format_shows_suite_name():
    entries = [SuiteMaturity("my_suite", "main", 3, 1.0, 0.0, "stable")]
    out = format_maturity_report(MaturityReport(entries=entries))
    assert "my_suite" in out


def test_format_shows_verdict():
    entries = [SuiteMaturity("x", "dev", 2, 0.4, 0.1, "flaky")]
    out = format_maturity_report(MaturityReport(entries=entries))
    assert "flaky" in out


def test_format_summary_counts():
    entries = [
        SuiteMaturity("a", "main", 5, 1.0, 0.05, "stable"),
        SuiteMaturity("b", "main", 5, 0.5, 0.05, "flaky"),
    ]
    out = format_maturity_report(MaturityReport(entries=entries))
    assert "stable=1" in out
    assert "flaky=1" in out
