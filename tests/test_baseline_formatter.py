"""Tests for batchmark.baseline_formatter."""

from batchmark.baseline_formatter import format_baseline_list, format_baseline_results
from batchmark.runner import BenchmarkResult


def _result(suite, success=True, duration=1.0, error=None):
    return BenchmarkResult(suite=suite, branch="main", duration=duration, success=success, error=error)


def test_format_list_empty():
    out = format_baseline_list([], use_color=False)
    assert "No baselines" in out


def test_format_list_shows_names():
    out = format_baseline_list(["v1", "v2"], use_color=False)
    assert "v1" in out
    assert "v2" in out


def test_format_results_shows_suite():
    out = format_baseline_results([_result("suite_a")], "my_base", use_color=False)
    assert "suite_a" in out
    assert "my_base" in out


def test_format_results_shows_duration():
    out = format_baseline_results([_result("s", duration=3.1415)], "b", use_color=False)
    assert "3.1415" in out


def test_format_results_failed_shows_error():
    r = _result("s", success=False, error="timeout")
    out = format_baseline_results([r], "b", use_color=False)
    assert "FAIL" in out
    assert "timeout" in out


def test_format_results_empty():
    out = format_baseline_results([], "empty_base", use_color=False)
    assert "empty_base" in out
    assert "no results" in out
