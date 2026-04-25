"""Tests for batchmark.heatmap."""
import pytest

from batchmark.heatmap import HeatmapCell, HeatmapReport, build_heatmap


class _FakeResult:
    def __init__(self, suite, branch, duration, success=True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _r(suite, branch, duration, success=True):
    return _FakeResult(suite, branch, duration, success)


def test_build_heatmap_empty():
    report = build_heatmap([])
    assert report.suites == []
    assert report.branches == []


def test_build_heatmap_single_result():
    report = build_heatmap([_r("bench_a", "main", 1.5)])
    assert report.suites == ["bench_a"]
    assert report.branches == ["main"]
    cell = report.get("bench_a", "main")
    assert cell is not None
    assert cell.mean_duration == pytest.approx(1.5)
    assert cell.sample_count == 1


def test_build_heatmap_averages_multiple_runs():
    results = [
        _r("bench_a", "main", 1.0),
        _r("bench_a", "main", 3.0),
    ]
    report = build_heatmap(results)
    cell = report.get("bench_a", "main")
    assert cell is not None
    assert cell.mean_duration == pytest.approx(2.0)
    assert cell.sample_count == 2


def test_build_heatmap_excludes_failed():
    results = [
        _r("bench_a", "main", 1.0, success=True),
        _r("bench_a", "main", 99.0, success=False),
    ]
    report = build_heatmap(results)
    cell = report.get("bench_a", "main")
    assert cell is not None
    assert cell.mean_duration == pytest.approx(1.0)


def test_build_heatmap_missing_cell_is_none():
    results = [
        _r("bench_a", "main", 1.0),
        _r("bench_b", "dev", 2.0),
    ]
    report = build_heatmap(results)
    assert report.get("bench_a", "dev") is None
    assert report.get("bench_b", "main") is None


def test_build_heatmap_sorted_axes():
    results = [
        _r("z_suite", "b_branch", 1.0),
        _r("a_suite", "a_branch", 2.0),
    ]
    report = build_heatmap(results)
    assert report.suites == ["a_suite", "z_suite"]
    assert report.branches == ["a_branch", "b_branch"]
