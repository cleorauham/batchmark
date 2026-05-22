"""Tests for batchmark.audit_formatter."""
from __future__ import annotations

from batchmark.auditor import AuditEntry, AuditReport
from batchmark.audit_formatter import format_audit_list, format_audit_report


def _entry(suite="s1", branch="main", success=True, duration=1.0):
    return AuditEntry(suite=suite, branch=branch, timestamp=0.0,
                      duration=duration, success=success)


def test_format_list_empty():
    result = format_audit_list([])
    assert "No audit" in result


def test_format_list_shows_names():
    result = format_audit_list(["run1", "run2"])
    assert "run1" in result
    assert "run2" in result


def test_format_report_empty():
    report = AuditReport(entries=[])
    result = format_audit_report(report)
    assert "empty" in result.lower()


def test_format_report_shows_suite_name():
    report = AuditReport(entries=[_entry("bench_alpha", "main")])
    result = format_audit_report(report)
    assert "bench_alpha" in result


def test_format_report_shows_branch_name():
    report = AuditReport(entries=[_entry(suite="s", branch="feature-x")])
    result = format_audit_report(report)
    assert "feature-x" in result


def test_format_report_shows_pass_fail_counts():
    report = AuditReport(entries=[
        _entry("s1", "main", True),
        _entry("s2", "main", False),
    ])
    result = format_audit_report(report)
    assert "1 passed" in result
    assert "1 failed" in result


def test_format_report_shows_name_in_header():
    report = AuditReport(entries=[_entry()])
    result = format_audit_report(report, name="weekly")
    assert "weekly" in result


def test_format_report_summary_totals():
    report = AuditReport(entries=[
        _entry(success=True),
        _entry(success=True),
        _entry(success=False),
    ])
    result = format_audit_report(report)
    assert "3 entries" in result
    assert "1 failed" in result
