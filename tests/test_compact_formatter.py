"""Tests for batchmark.compact_formatter."""
from batchmark.compactor import CompactEntry, CompactReport
from batchmark.compact_formatter import format_compact_report


def _entry(suite: str = "suite_a", branch: str = "main", duration: float = 0.5, passed: bool = True) -> CompactEntry:
    return CompactEntry(suite=suite, branch=branch, duration=duration, passed=passed, timestamp="2024-01-01T00:00:00")


def _report(entries=None, sources=1, removed=0) -> CompactReport:
    return CompactReport(entries=entries or [], sources_merged=sources, total_removed=removed)


def test_format_empty_returns_warning():
    out = format_compact_report(_report())
    assert "No entries" in out


def test_format_shows_sources_merged():
    r = _report(entries=[_entry()], sources=3, removed=2)
    out = format_compact_report(r)
    assert "3" in out


def test_format_shows_suite_name():
    r = _report(entries=[_entry(suite="my_bench")])
    out = format_compact_report(r)
    assert "my_bench" in out


def test_format_shows_branch_name():
    r = _report(entries=[_entry(branch="feature-x")])
    out = format_compact_report(r)
    assert "feature-x" in out


def test_format_shows_duration():
    r = _report(entries=[_entry(duration=1.2345)])
    out = format_compact_report(r)
    assert "1.2345s" in out


def test_format_shows_pass_status():
    r = _report(entries=[_entry(passed=True)])
    out = format_compact_report(r)
    assert "PASS" in out


def test_format_shows_fail_status():
    r = _report(entries=[_entry(passed=False)])
    out = format_compact_report(r)
    assert "FAIL" in out


def test_format_shows_removed_count():
    r = _report(entries=[_entry()], removed=7)
    out = format_compact_report(r)
    assert "7" in out
