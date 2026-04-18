"""Tests for batchmark.trend and batchmark.trend_formatter."""
import pytest
from unittest.mock import patch
from batchmark.runner import BenchmarkResult
from batchmark.trend import build_trend, SuiteTrend, TrendReport
from batchmark.trend_formatter import format_trend


def _result(suite, branch, duration, success=True):
    return BenchmarkResult(suite=suite, branch=branch, duration=duration, success=success, output="")


@patch("batchmark.trend.list_baselines", return_value=[])
@patch("batchmark.trend.load_baseline")
def test_build_trend_no_baselines(mock_load, mock_list):
    report = build_trend("/fake", "main")
    assert report.baselines == []
    assert report.trends == []


@patch("batchmark.trend.list_baselines", return_value=["v1", "v2"])
@patch("batchmark.trend.load_baseline")
def test_build_trend_collects_points(mock_load, mock_list):
    mock_load.side_effect = [
        [_result("bench_a", "main", 1.0), _result("bench_a", "main", 1.2)],
        [_result("bench_a", "main", 2.0)],
    ]
    report = build_trend("/fake", "main")
    assert report.baselines == ["v1", "v2"]
    assert len(report.trends) == 1
    trend = report.trends[0]
    assert trend.suite == "bench_a"
    assert len(trend.points) == 2
    assert trend.points[0].mean_duration == pytest.approx(1.1)
    assert trend.points[1].mean_duration == pytest.approx(2.0)


@patch("batchmark.trend.list_baselines", return_value=["v1", "v2"])
@patch("batchmark.trend.load_baseline")
def test_build_trend_excludes_failed(mock_load, mock_list):
    mock_load.side_effect = [
        [_result("bench_a", "main", 1.0, success=False)],
        [_result("bench_a", "main", 2.0)],
    ]
    report = build_trend("/fake", "main")
    assert len(report.trends[0].points) == 1


def test_slope_improving():
    trend = SuiteTrend(suite="s")
    from batchmark.trend import TrendPoint
    trend.points = [TrendPoint("v1", 3.0), TrendPoint("v2", 2.0), TrendPoint("v3", 1.0)]
    assert trend.verdict == "improving"
    assert trend.slope is not None and trend.slope < 0


def test_slope_degrading():
    trend = SuiteTrend(suite="s")
    from batchmark.trend import TrendPoint
    trend.points = [TrendPoint("v1", 1.0), TrendPoint("v2", 2.0), TrendPoint("v3", 3.0)]
    assert trend.verdict == "degrading"


def test_slope_insufficient():
    trend = SuiteTrend(suite="s")
    assert trend.verdict == "insufficient data"
    assert trend.slope is None


def test_format_trend_empty():
    report = TrendReport(baselines=[], trends=[])
    out = format_trend(report, "main")
    assert "main" in out
    assert "No trend data available" in out


def test_format_trend_shows_suite():
    from batchmark.trend import TrendPoint
    trend = SuiteTrend(suite="bench_x")
    trend.points = [TrendPoint("v1", 1.0), TrendPoint("v2", 1.1)]
    report = TrendReport(baselines=["v1", "v2"], trends=[trend])
    out = format_trend(report, "main")
    assert "bench_x" in out
    assert "stable" in out or "degrading" in out or "improving" in out
