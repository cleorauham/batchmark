"""Tests for batchmark.fingerprinter."""
import pytest
from batchmark.fingerprinter import (
    build_fingerprints,
    FingerprintEntry,
    FingerprintReport,
)


class _FakeResult:
    def __init__(self, suite, branch, duration, success=True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _r(suite="suite_a", branch="main", duration=1.0, success=True):
    return _FakeResult(suite, branch, duration, success)


def test_build_fingerprints_empty():
    report = build_fingerprints([])
    assert report.entries == []


def test_build_fingerprints_excludes_failed():
    results = [_r(success=False), _r(success=True)]
    report = build_fingerprints(results)
    assert len(report.entries) == 1


def test_build_fingerprints_entry_fields():
    r = _r(suite="bench_x", branch="dev", duration=2.5)
    report = build_fingerprints([r])
    assert len(report.entries) == 1
    e = report.entries[0]
    assert e.suite == "bench_x"
    assert e.branch == "dev"
    assert len(e.fingerprint) == 16


def test_fingerprint_is_deterministic():
    r = _r()
    r1 = build_fingerprints([r])
    r2 = build_fingerprints([r])
    assert r1.entries[0].fingerprint == r2.entries[0].fingerprint


def test_fingerprint_differs_on_duration():
    r1 = build_fingerprints([_r(duration=1.0)])
    r2 = build_fingerprints([_r(duration=2.0)])
    assert r1.entries[0].fingerprint != r2.entries[0].fingerprint


def test_get_returns_none_for_missing():
    report = build_fingerprints([_r(suite="a", branch="main")])
    assert report.get("main", "missing") is None


def test_get_returns_fingerprint():
    r = _r(suite="a", branch="main")
    report = build_fingerprints([r])
    fp = report.get("main", "a")
    assert fp is not None and len(fp) == 16


def test_matches_identical_reports():
    results = [_r(suite="a"), _r(suite="b")]
    r1 = build_fingerprints(results)
    r2 = build_fingerprints(results)
    assert r1.matches(r2)


def test_matches_returns_false_on_difference():
    r1 = build_fingerprints([_r(duration=1.0)])
    r2 = build_fingerprints([_r(duration=9.9)])
    assert not r1.matches(r2)


def test_by_branch_groups_correctly():
    results = [
        _r(suite="a", branch="main"),
        _r(suite="b", branch="dev"),
        _r(suite="c", branch="main"),
    ]
    report = build_fingerprints(results)
    by_branch = report.by_branch()
    assert len(by_branch["main"]) == 2
    assert len(by_branch["dev"]) == 1
