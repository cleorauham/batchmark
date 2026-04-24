"""Tests for batchmark.sampler."""

from __future__ import annotations

import pytest

from batchmark.sampler import SampleReport, SamplerError, sample


class _FakeResult:
    def __init__(self, branch: str, suite: str, duration: float, success: bool = True):
        self.branch = branch
        self.suite = suite
        self.duration = duration
        self.success = success


def _r(branch="main", suite="bench_a", duration=1.0, success=True):
    return _FakeResult(branch=branch, suite=suite, duration=duration, success=success)


def test_sample_invalid_n_raises():
    with pytest.raises(SamplerError):
        sample([], n=0)


def test_sample_negative_n_raises():
    with pytest.raises(SamplerError):
        sample([], n=-1)


def test_sample_empty_input_returns_empty():
    result = sample([], n=5)
    assert result == []


def test_sample_groups_by_branch_and_suite():
    results = [
        _r(branch="main", suite="a"),
        _r(branch="main", suite="b"),
        _r(branch="dev", suite="a"),
    ]
    reports = sample(results, n=10)
    keys = {(r.branch, r.suite) for r in reports}
    assert keys == {("main", "a"), ("main", "b"), ("dev", "a")}


def test_sample_respects_n_limit():
    results = [_r(duration=float(i)) for i in range(20)]
    reports = sample(results, n=5, seed=42)
    assert len(reports) == 1
    assert reports[0].sample_size == 5
    assert reports[0].total_available == 20


def test_sample_all_when_fewer_than_n():
    results = [_r(duration=float(i)) for i in range(3)]
    reports = sample(results, n=10)
    assert reports[0].sample_size == 3
    assert reports[0].total_available == 3


def test_sample_seed_reproducible():
    results = [_r(duration=float(i)) for i in range(50)]
    r1 = sample(results, n=10, seed=7)
    r2 = sample(results, n=10, seed=7)
    assert [x.duration for x in r1[0].results] == [x.duration for x in r2[0].results]


def test_mean_duration_excludes_failed():
    results = [
        _r(duration=2.0, success=True),
        _r(duration=4.0, success=True),
        _r(duration=99.0, success=False),
    ]
    reports = sample(results, n=10)
    assert reports[0].mean_duration == pytest.approx(3.0)


def test_mean_duration_none_when_all_failed():
    results = [_r(duration=1.0, success=False)]
    reports = sample(results, n=10)
    assert reports[0].mean_duration is None
