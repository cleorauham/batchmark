"""Tests for batchmark.segmenter."""
from __future__ import annotations

import pytest
from dataclasses import dataclass
from batchmark.segmenter import (
    segment_by_count,
    segment_by_branch,
    SegmentError,
    SegmentReport,
)


@dataclass
class _FakeResult:
    suite: str
    branch: str
    duration: float = 1.0
    success: bool = True


def _r(suite: str, branch: str) -> _FakeResult:
    return _FakeResult(suite=suite, branch=branch)


def test_segment_by_count_empty():
    report = segment_by_count([], 3)
    assert report.total_segments == 0
    assert report.total_results == 0


def test_segment_by_count_single_segment():
    results = [_r("a", "main"), _r("b", "main")]
    report = segment_by_count(results, 5)
    assert report.total_segments == 1
    assert report.total_results == 2


def test_segment_by_count_splits_correctly():
    results = [_r(f"s{i}", "main") for i in range(7)]
    report = segment_by_count(results, 3)
    assert report.total_segments == 3
    assert len(report.segments[0]) == 3
    assert len(report.segments[1]) == 3
    assert len(report.segments[2]) == 1


def test_segment_by_count_labels():
    results = [_r("a", "main"), _r("b", "main"), _r("c", "main")]
    report = segment_by_count(results, 2)
    assert report.segments[0].label == "seg-1"
    assert report.segments[1].label == "seg-2"


def test_segment_by_count_invalid_size():
    with pytest.raises(SegmentError):
        segment_by_count([_r("a", "main")], 0)


def test_segment_by_branch_empty():
    report = segment_by_branch([])
    assert isinstance(report, SegmentReport)
    assert report.total_segments == 0


def test_segment_by_branch_groups_correctly():
    results = [
        _r("a", "main"),
        _r("b", "dev"),
        _r("c", "main"),
    ]
    report = segment_by_branch(results)
    assert report.total_segments == 2
    dev_seg = report.by_label("dev")
    assert dev_seg is not None
    assert len(dev_seg) == 1


def test_segment_by_label_missing_returns_none():
    results = [_r("a", "main")]
    report = segment_by_branch(results)
    assert report.by_label("nonexistent") is None


def test_segment_suite_and_branch_names():
    results = [_r("suite-x", "feat"), _r("suite-y", "feat")]
    report = segment_by_count(results, 10)
    seg = report.segments[0]
    assert "suite-x" in seg.suite_names
    assert "feat" in seg.branch_names
