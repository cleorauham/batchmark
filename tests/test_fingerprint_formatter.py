"""Tests for batchmark.fingerprint_formatter."""
import pytest
from batchmark.fingerprinter import build_fingerprints
from batchmark.fingerprint_formatter import format_fingerprint_report


class _FR:
    def __init__(self, suite, branch, duration=1.0, success=True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _report(*results):
    return build_fingerprints(results)


def test_format_empty_returns_warning():
    out = format_fingerprint_report(_report())
    assert "no fingerprint" in out


def test_format_shows_branch_name():
    out = format_fingerprint_report(_report(_FR("a", "main")))
    assert "main" in out


def test_format_shows_suite_name():
    out = format_fingerprint_report(_report(_FR("bench_z", "main")))
    assert "bench_z" in out


def test_format_shows_fingerprint_hex():
    out = format_fingerprint_report(_report(_FR("a", "main", duration=3.14)))
    # fingerprint is 16 hex chars
    import re
    assert re.search(r"[0-9a-f]{16}", out)


def test_format_shows_total_entries():
    results = [_FR("a", "main"), _FR("b", "dev")]
    out = format_fingerprint_report(_report(*results))
    assert "Total entries: 2" in out
