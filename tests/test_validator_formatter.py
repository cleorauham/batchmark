"""Tests for batchmark.validator_formatter."""
from __future__ import annotations

from batchmark.validator import ValidationReport, ValidationViolation
from batchmark.validator_formatter import format_validation_report


def _violation(suite: str = "bench_a", rule: str = "max_duration") -> ValidationViolation:
    return ValidationViolation(
        suite=suite,
        branch="main",
        rule=rule,
        detail="5.000s exceeds limit 2.000s",
    )


def test_format_passed_shows_success():
    report = ValidationReport(violations=[])
    out = format_validation_report(report)
    assert "passed" in out.lower()


def test_format_failed_shows_violation_count():
    report = ValidationReport(violations=[_violation(), _violation(suite="bench_b")])
    out = format_validation_report(report)
    assert "2" in out


def test_format_shows_suite_name():
    report = ValidationReport(violations=[_violation(suite="my_suite")])
    out = format_validation_report(report)
    assert "my_suite" in out


def test_format_shows_rule_name():
    report = ValidationReport(violations=[_violation(rule="max_regression_pct")])
    out = format_validation_report(report)
    assert "max_regression_pct" in out


def test_format_shows_detail():
    report = ValidationReport(violations=[_violation()])
    out = format_validation_report(report)
    assert "exceeds limit" in out
