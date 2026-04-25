"""Tests for batchmark.segment_formatter."""
from __future__ import annotations

from dataclasses import dataclass
from batchmark.segmenter import segment_by_count, segment_by_branch
from batchmark.segment_formatter import format_segment_report


@dataclass
class _FR:
    suite: str
    branch: str
    duration: float = 1.0
    success: bool = True


def _r(suite: str, branch: str) -> _FR:
    return _FR(suite=suite, branch=branch)


def _report(results=None, size: int = 5):
    if results is None:
        results = [
            _r("bench-a", "main"),
            _r("bench-b", "dev"),
            _r("bench-c", "main"),
        ]
    return segment_by_count(results, size)


def test_format_empty_returns_warning():
    report = segment_by_count([], 3)
    out = format_segment_report(report)
    assert "No segments" in out


def test_format_shows_segment_label():
    report = segment_by_count([_r("a", "main"), _r("b", "main")], 1)
    out = format_segment_report(report)
    assert "seg-1" in out
    assert "seg-2" in out


def test_format_shows_result_count():
    results = [_r(f"s{i}", "main") for i in range(6)]
    report = segment_by_count(results, 3)
    out = format_segment_report(report)
    assert "3" in out


def test_format_shows_header():
    report = _report()
    out = format_segment_report(report)
    assert "Segment" in out
    assert "Results" in out


def test_format_branch_segments_show_branch_as_label():
    results = [_r("a", "main"), _r("b", "dev")]
    report = segment_by_branch(results)
    out = format_segment_report(report)
    assert "main" in out
    assert "dev" in out
