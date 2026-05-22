"""Tests for batchmark.auditor."""
from __future__ import annotations

import pytest
from pathlib import Path

from batchmark.auditor import (
    AuditEntry,
    AuditReport,
    AuditError,
    audit_path,
    save_audit,
    load_audit,
    list_audits,
    build_audit,
)


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "audits"


def _entry(suite="s1", branch="main", success=True, duration=1.0):
    return AuditEntry(suite=suite, branch=branch, timestamp=0.0,
                      duration=duration, success=success)


def test_save_creates_file(store):
    report = AuditReport(entries=[_entry()])
    path = save_audit(store, "run1", report)
    assert path.exists()


def test_save_and_load_roundtrip(store):
    entries = [
        _entry("bench_a", "main", True, 2.5),
        _entry("bench_b", "dev", False, 0.1),
    ]
    report = AuditReport(entries=entries)
    save_audit(store, "run1", report)
    loaded = load_audit(store, "run1")
    assert len(loaded.entries) == 2
    assert loaded.entries[0].suite == "bench_a"
    assert loaded.entries[1].success is False


def test_load_missing_raises(store):
    with pytest.raises(AuditError):
        load_audit(store, "nonexistent")


def test_list_empty(store):
    assert list_audits(store) == []


def test_list_shows_names(store):
    save_audit(store, "alpha", AuditReport(entries=[_entry()]))
    save_audit(store, "beta", AuditReport(entries=[_entry()]))
    names = list_audits(store)
    assert "alpha" in names
    assert "beta" in names


def test_by_branch_filters(store):
    report = AuditReport(entries=[
        _entry("s1", "main"),
        _entry("s2", "dev"),
    ])
    assert len(report.by_branch("main")) == 1
    assert report.by_branch("main")[0].suite == "s1"


def test_by_suite_filters():
    report = AuditReport(entries=[
        _entry("s1", "main"),
        _entry("s1", "dev"),
        _entry("s2", "main"),
    ])
    assert len(report.by_suite("s1")) == 2


def test_failed_returns_only_failures():
    report = AuditReport(entries=[
        _entry(success=True),
        _entry(success=False),
    ])
    assert len(report.failed()) == 1


def test_build_audit_from_results():
    class FakeResult:
        def __init__(self, suite, duration, success):
            self.suite = suite
            self.duration = duration
            self.success = success
            self.timestamp = 42.0

    results = [FakeResult("bench_x", 3.14, True), FakeResult("bench_y", 0.5, False)]
    report = build_audit(results, branch="feature")
    assert len(report.entries) == 2
    assert report.entries[0].branch == "feature"
    assert report.entries[1].success is False
