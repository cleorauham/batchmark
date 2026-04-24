"""Tests for batchmark.sampler_formatter."""

from __future__ import annotations

from batchmark.sampler import SampleReport
from batchmark.sampler_formatter import format_sample_report


class _FR:
    def __init__(self, duration: float, success: bool = True):
        self.duration = duration
        self.success = success
        self.branch = "main"
        self.suite = "bench_x"


def _report(branch="main", suite="bench_x", durations=None, total=None):
    durations = durations or [1.0, 2.0]
    results = [_FR(d) for d in durations]
    return SampleReport(
        branch=branch,
        suite=suite,
        results=results,
        total_available=total if total is not None else len(results),
    )


def test_format_empty_returns_warning():
    out = format_sample_report([], color=False)
    assert "No sample data" in out


def test_format_shows_branch_name():
    out = format_sample_report([_report(branch="feature-x")], color=False)
    assert "feature-x" in out


def test_format_shows_suite_name():
    out = format_sample_report([_report(suite="my_suite")], color=False)
    assert "my_suite" in out


def test_format_shows_sample_and_total():
    r = _report(durations=[1.0, 2.0], total=10)
    out = format_sample_report([r], color=False)
    assert "2" in out
    assert "10" in out


def test_format_shows_mean_duration():
    r = _report(durations=[2.0, 4.0])
    out = format_sample_report([r], color=False)
    assert "3.0000s" in out


def test_format_shows_totals_line():
    r1 = _report(branch="main", suite="a", durations=[1.0], total=5)
    r2 = _report(branch="dev", suite="a", durations=[1.0, 1.0], total=8)
    out = format_sample_report([r1, r2], color=False)
    assert "3 sampled from 13 available" in out
