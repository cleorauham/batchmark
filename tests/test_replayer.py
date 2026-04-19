import pytest
from unittest.mock import patch
from batchmark.replayer import (
    replay_from_baseline,
    replay_from_cache,
    ReplayError,
)
from batchmark.runner import BenchmarkResult


def _result(suite: str, branch: str = "main", success: bool = True) -> BenchmarkResult:
    return BenchmarkResult(suite=suite, branch=branch, duration=1.0, success=success, output="")


def test_replay_from_baseline_ok(tmp_path):
    results = [_result("bench_a"), _result("bench_b")]
    with patch("batchmark.replayer.load_baseline", return_value=results):
        report = replay_from_baseline("v1", str(tmp_path))
    assert len(report.results) == 2
    assert report.source.kind == "baseline"
    assert report.source.name == "v1"
    assert set(report.source.suite_names) == {"bench_a", "bench_b"}


def test_replay_from_baseline_missing_raises(tmp_path):
    from batchmark.baseline import BaselineError
    with patch("batchmark.replayer.load_baseline", side_effect=BaselineError("nope")):
        with pytest.raises(ReplayError, match="nope"):
            replay_from_baseline("ghost", str(tmp_path))


def test_replay_from_cache_ok(tmp_path):
    r = _result("bench_a")
    with patch("batchmark.replayer.load_result", return_value=r):
        report = replay_from_cache("main", ["bench_a"], str(tmp_path))
    assert len(report.results) == 1
    assert report.source.kind == "cache"
    assert report.source.name == "main"


def test_replay_from_cache_missing_raises(tmp_path):
    with patch("batchmark.replayer.load_result", return_value=None):
        with pytest.raises(ReplayError, match="bench_x"):
            replay_from_cache("main", ["bench_x"], str(tmp_path))


def test_replay_succeeded_failed_split(tmp_path):
    results = [_result("a", success=True), _result("b", success=False)]
    with patch("batchmark.replayer.load_baseline", return_value=results):
        report = replay_from_baseline("v1", str(tmp_path))
    assert len(report.succeeded) == 1
    assert len(report.failed) == 1
