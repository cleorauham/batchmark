"""Tests for batchmark.bucket_formatter."""
from __future__ import annotations

from batchmark.bucketer import bucket_results
from batchmark.bucket_formatter import format_bucket_report


class _FR:
    def __init__(self, suite: str, duration: float, branch: str = "main"):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = True


def _report(results=None, branch="main"):
    if results is None:
        results = []
    return bucket_results(results, branch=branch)


def test_format_empty_shows_no_results():
    out = format_bucket_report(_report(), color=False)
    assert "no results" in out


def test_format_shows_branch_name():
    out = format_bucket_report(_report(branch="feature-x"), color=False)
    assert "feature-x" in out


def test_format_shows_bucket_labels():
    results = [_FR("s1", 0.05), _FR("s2", 0.5)]
    out = format_bucket_report(_report(results), color=False)
    assert "fast" in out
    assert "moderate" in out


def test_format_shows_suite_name_preview():
    results = [_FR("my_suite", 0.05)]
    out = format_bucket_report(_report(results), color=False)
    assert "my_suite" in out


def test_format_shows_total_count():
    results = [_FR(f"s{i}", 0.05) for i in range(4)]
    out = format_bucket_report(_report(results), color=False)
    assert "4" in out


def test_format_truncates_long_suite_list():
    results = [_FR(f"suite_{i}", 0.05) for i in range(6)]
    out = format_bucket_report(_report(results), color=False)
    assert "+3 more" in out
