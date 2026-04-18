"""Tests for batchmark.cache."""

import pytest
from pathlib import Path

from batchmark.cache import save_result, load_result, clear_cache, cache_path, CacheError
from batchmark.runner import BenchmarkResult


@pytest.fixture
def cache_dir(tmp_path):
    return tmp_path / "cache"


def _result(suite="bench_a", duration=1.23, success=True, output="ok"):
    return BenchmarkResult(suite=suite, duration=duration, success=success, output=output)


def test_save_creates_file(cache_dir):
    result = _result()
    path = save_result(result, branch="main", commit="abc123", cache_dir=cache_dir)
    assert path.exists()


def test_save_and_load_roundtrip(cache_dir):
    result = _result(suite="bench_x", duration=4.56)
    save_result(result, branch="feature", commit="def456", cache_dir=cache_dir)
    loaded = load_result("feature", "bench_x", "def456", cache_dir=cache_dir)
    assert loaded is not None
    assert loaded.suite == "bench_x"
    assert abs(loaded.duration - 4.56) < 1e-6
    assert loaded.success is True


def test_load_missing_returns_none(cache_dir):
    result = load_result("main", "nonexistent", "000", cache_dir=cache_dir)
    assert result is None


def test_load_corrupt_raises(cache_dir):
    path = cache_path(cache_dir, "main", "bad_suite", "zzz")
    cache_dir.mkdir(parents=True, exist_ok=True)
    path.write_text("{invalid json")
    with pytest.raises(CacheError):
        load_result("main", "bad_suite", "zzz", cache_dir=cache_dir)


def test_clear_cache_removes_files(cache_dir):
    save_result(_result(suite="a"), branch="main", commit="1", cache_dir=cache_dir)
    save_result(_result(suite="b"), branch="main", commit="2", cache_dir=cache_dir)
    removed = clear_cache(cache_dir=cache_dir)
    assert removed == 2
    assert list(cache_dir.glob("*.json")) == []


def test_clear_cache_nonexistent_dir(tmp_path):
    removed = clear_cache(cache_dir=tmp_path / "no_such_dir")
    assert removed == 0


def test_different_commits_produce_different_files(cache_dir):
    r = _result()
    p1 = save_result(r, branch="main", commit="aaa", cache_dir=cache_dir)
    p2 = save_result(r, branch="main", commit="bbb", cache_dir=cache_dir)
    assert p1 != p2
