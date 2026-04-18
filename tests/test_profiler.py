"""Tests for batchmark.profiler and batchmark.profiler_formatter."""
import pytest
from batchmark.profiler import ProfileEntry, ProfileReport, build_profile
from batchmark.profiler_formatter import format_profile


class _FakeResult:
    def __init__(self, suite, branch, duration, success=True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _results():
    return [
        _FakeResult("suite_a", "main", 1.0),
        _FakeResult("suite_a", "main", 3.0),
        _FakeResult("suite_a", "dev", 2.0),
        _FakeResult("suite_b", "main", 0.5),
        _FakeResult("suite_b", "main", 0.0, success=False),  # excluded
    ]


def test_build_profile_groups_by_suite_and_branch():
    report = build_profile(_results())
    assert len(report.entries) == 3


def test_build_profile_excludes_failed():
    report = build_profile(_results())
    entry = report.get("suite_b", "main")
    assert entry is not None
    assert len(entry.durations) == 1


def test_entry_mean():
    report = build_profile(_results())
    entry = report.get("suite_a", "main")
    assert entry.mean == pytest.approx(2.0)


def test_entry_stdev():
    report = build_profile(_results())
    entry = report.get("suite_a", "main")
    assert entry.stdev == pytest.approx(1.4142, rel=1e-3)


def test_entry_min_max():
    report = build_profile(_results())
    entry = report.get("suite_a", "main")
    assert entry.min == 1.0
    assert entry.max == 3.0


def test_get_missing_returns_none():
    report = build_profile(_results())
    assert report.get("nonexistent", "main") is None


def test_format_profile_contains_suite_name():
    report = build_profile(_results())
    output = format_profile(report)
    assert "suite_a" in output
    assert "suite_b" in output


def test_format_profile_empty():
    output = format_profile(ProfileReport())
    assert "No profiling data" in output


def test_format_profile_contains_branch():
    report = build_profile(_results())
    output = format_profile(report)
    assert "main" in output
    assert "dev" in output
