"""Tests for batchmark.heatmap_formatter."""
from batchmark.heatmap import build_heatmap
from batchmark.heatmap_formatter import format_heatmap


class _FakeResult:
    def __init__(self, suite, branch, duration, success=True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _r(suite, branch, duration):
    return _FakeResult(suite, branch, duration)


def test_format_empty_returns_warning():
    report = build_heatmap([])
    out = format_heatmap(report)
    assert "No heatmap data" in out


def test_format_shows_branch_name():
    report = build_heatmap([_r("bench", "main", 1.0)])
    out = format_heatmap(report)
    assert "main" in out


def test_format_shows_suite_name():
    report = build_heatmap([_r("bench_alpha", "main", 1.0)])
    out = format_heatmap(report)
    assert "bench_alpha" in out


def test_format_shows_duration():
    report = build_heatmap([_r("bench", "main", 2.5)])
    out = format_heatmap(report)
    assert "2.500s" in out


def test_format_missing_cell_shows_dash():
    results = [
        _r("bench_a", "main", 1.0),
        _r("bench_b", "dev", 2.0),
    ]
    report = build_heatmap(results)
    out = format_heatmap(report)
    # There should be placeholder dashes for missing cells
    assert "-" in out


def test_format_multiple_branches_all_present():
    results = [
        _r("bench", "main", 1.0),
        _r("bench", "dev", 3.0),
    ]
    report = build_heatmap(results)
    out = format_heatmap(report)
    assert "main" in out
    assert "dev" in out
    assert "1.000s" in out
    assert "3.000s" in out
