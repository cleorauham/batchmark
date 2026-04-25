"""Tests for batchmark.tracer and batchmark.trace_formatter."""
from __future__ import annotations

import pytest
from batchmark.tracer import TraceSpan, TraceReport, Tracer, build_trace
from batchmark.trace_formatter import format_trace_report


class _FakeResult:
    def __init__(self, suite: str, branch: str, duration: float, success: bool = True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _span(suite="s1", branch="main", duration=1.0, success=True) -> TraceSpan:
    return TraceSpan(suite=suite, branch=branch, start=0.0, end=duration, success=success)


# --- TraceSpan ---

def test_span_duration():
    s = TraceSpan(suite="s", branch="b", start=1.0, end=3.5, success=True)
    assert s.duration == pytest.approx(2.5)


def test_span_str_ok():
    s = _span(suite="bench", branch="main", duration=0.5)
    assert "main" in str(s)
    assert "bench" in str(s)
    assert "ok" in str(s)


def test_span_str_fail():
    s = _span(success=False)
    assert "fail" in str(s)


# --- TraceReport ---

def test_by_branch_groups_correctly():
    report = TraceReport(spans=[
        _span(branch="main"),
        _span(branch="dev"),
        _span(branch="main"),
    ])
    by_b = report.by_branch()
    assert len(by_b["main"]) == 2
    assert len(by_b["dev"]) == 1


def test_by_suite_groups_correctly():
    report = TraceReport(spans=[_span(suite="a"), _span(suite="b"), _span(suite="a")])
    assert len(report.by_suite()["a"]) == 2


def test_total_duration_sums_all():
    report = TraceReport(spans=[_span(duration=1.0), _span(duration=2.5)])
    assert report.total_duration() == pytest.approx(3.5)


def test_failed_spans_filters():
    report = TraceReport(spans=[_span(success=True), _span(success=False)])
    assert len(report.failed_spans()) == 1
    assert report.has_failures()


def test_no_failures():
    report = TraceReport(spans=[_span(success=True)])
    assert not report.has_failures()


# --- Tracer ---

def test_tracer_records_span():
    t = Tracer()
    t.start("suite_a", "main")
    t.finish(success=True)
    assert len(t.report.spans) == 1
    assert t.report.spans[0].suite == "suite_a"


def test_tracer_finish_without_start_raises():
    t = Tracer()
    with pytest.raises(RuntimeError):
        t.finish()


# --- build_trace ---

def test_build_trace_from_results():
    results = [_FakeResult("s1", "main", 1.2), _FakeResult("s2", "dev", 0.4, success=False)]
    report = build_trace(results)
    assert len(report.spans) == 2
    assert report.has_failures()


# --- format_trace_report ---

def test_format_empty_report():
    out = format_trace_report(TraceReport(), color=False)
    assert "No trace" in out


def test_format_shows_branch_and_suite():
    report = TraceReport(spans=[_span(suite="my_bench", branch="feature")])
    out = format_trace_report(report, color=False)
    assert "feature" in out
    assert "my_bench" in out


def test_format_shows_total():
    report = TraceReport(spans=[_span(duration=2.0), _span(duration=1.0)])
    out = format_trace_report(report, color=False)
    assert "Total" in out
    assert "3" in out
