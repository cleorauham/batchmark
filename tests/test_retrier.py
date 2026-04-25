"""Tests for batchmark.retrier and batchmark.retry_formatter."""
from __future__ import annotations

import pytest

from batchmark.retrier import (
    RetryError,
    RetryRecord,
    RetryReport,
    retry_run,
)
from batchmark.retry_formatter import format_retry_report


class _FakeResult:
    def __init__(self, success: bool, duration_s: float | None = 1.0):
        self.success = success
        self.duration_s = duration_s


def test_retry_succeeds_first_attempt():
    calls = []

    def run():
        calls.append(1)
        return _FakeResult(success=True, duration_s=0.5)

    rec = retry_run(run, suite="bench", branch="main", max_attempts=3)
    assert rec.attempts == 1
    assert rec.succeeded is True
    assert len(calls) == 1


def test_retry_retries_on_failure():
    results = [_FakeResult(False, 1.0), _FakeResult(False, 1.1), _FakeResult(True, 0.9)]
    idx = [0]

    def run():
        r = results[idx[0]]
        idx[0] += 1
        return r

    rec = retry_run(run, suite="bench", branch="main", max_attempts=3)
    assert rec.attempts == 3
    assert rec.succeeded is True
    assert len(rec.all_durations) == 3


def test_retry_exhausts_attempts():
    def run():
        return _FakeResult(success=False, duration_s=2.0)

    rec = retry_run(run, suite="slow", branch="dev", max_attempts=2)
    assert rec.attempts == 2
    assert rec.succeeded is False


def test_retry_no_retry_on_failure():
    calls = []

    def run():
        calls.append(1)
        return _FakeResult(success=False)

    rec = retry_run(run, suite="x", branch="y", max_attempts=5, retry_on_failure=False)
    assert rec.attempts == 1
    assert len(calls) == 1


def test_retry_invalid_max_attempts_raises():
    with pytest.raises(RetryError):
        retry_run(lambda: None, suite="x", branch="y", max_attempts=0)


def test_retry_report_counts():
    rec1 = RetryRecord("a", "main", 1, _FakeResult(True), [1.0])
    rec2 = RetryRecord("b", "main", 3, _FakeResult(False), [2.0, 2.1, 2.2])
    report = RetryReport(records=[rec1, rec2])
    assert report.total_retried == 1
    assert report.total_failed == 1
    assert report.total_succeeded == 1


def test_format_empty_report():
    out = format_retry_report(RetryReport())
    assert "No retry records" in out


def test_format_report_shows_suite_name():
    rec = RetryRecord("mybench", "main", 2, _FakeResult(True), [0.5, 0.6])
    out = format_retry_report(RetryReport(records=[rec]))
    assert "mybench" in out
    assert "main" in out


def test_format_report_shows_counts():
    rec = RetryRecord("s", "b", 1, _FakeResult(True), [1.0])
    out = format_retry_report(RetryReport(records=[rec]))
    assert "Suites" in out
    assert "Retried" in out
