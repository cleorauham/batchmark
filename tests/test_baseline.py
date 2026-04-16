"""Tests for batchmark.baseline module."""

import pytest

from batchmark.baseline import (
    BaselineError,
    list_baselines,
    load_baseline,
    save_baseline,
)
from batchmark.runner import BenchmarkResult


def _result(suite: str, branch: str = "main", duration: float = 1.0, success: bool = True):
    return BenchmarkResult(suite=suite, branch=branch, duration=duration, success=success)


@pytest.fixture()
def baseline_dir(tmp_path):
    return str(tmp_path / "baselines")


def test_save_and_load_roundtrip(baseline_dir):
    results = [_result("suite_a"), _result("suite_b", duration=2.5)]
    save_baseline(results, "my_baseline", directory=baseline_dir)
    loaded = load_baseline("my_baseline", directory=baseline_dir)
    assert len(loaded) == 2
    assert loaded[0].suite == "suite_a"
    assert loaded[1].duration == pytest.approx(2.5)


def test_save_creates_file(baseline_dir, tmp_path):
    path = save_baseline([_result("s")], "v1", directory=baseline_dir)
    assert path.exists()


def test_load_missing_raises(baseline_dir):
    with pytest.raises(BaselineError, match="not found"):
        load_baseline("nonexistent", directory=baseline_dir)


def test_list_baselines_empty(baseline_dir):
    assert list_baselines(baseline_dir) == []


def test_list_baselines_returns_names(baseline_dir):
    save_baseline([_result("s")], "alpha", directory=baseline_dir)
    save_baseline([_result("s")], "beta", directory=baseline_dir)
    names = list_baselines(baseline_dir)
    assert names == ["alpha", "beta"]


def test_failed_result_preserved(baseline_dir):
    r = BenchmarkResult(suite="s", branch="main", duration=0.0, success=False, error="timeout")
    save_baseline([r], "fail_base", directory=baseline_dir)
    loaded = load_baseline("fail_base", directory=baseline_dir)
    assert not loaded[0].success
    assert loaded[0].error == "timeout"
