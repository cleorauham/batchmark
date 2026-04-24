"""Tests for batchmark.normalizer."""
import pytest

from batchmark.normalizer import NormalizerError, normalize


class _FakeResult:
    def __init__(self, suite, branch, duration, success=True):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def _r(suite, branch, duration, success=True):
    return _FakeResult(suite, branch, duration, success)


def test_normalize_empty_returns_empty_report():
    report = normalize([], reference_branch="main")
    assert report.results == []
    assert report.reference_branch == "main"


def test_normalize_ratio_one_for_reference_branch():
    results = [_r("bench_a", "main", 2.0)]
    report = normalize(results, reference_branch="main")
    assert len(report.results) == 1
    assert report.results[0].ratio == pytest.approx(1.0)


def test_normalize_ratio_relative_to_reference():
    results = [
        _r("bench_a", "main", 2.0),
        _r("bench_a", "feature", 4.0),
    ]
    report = normalize(results, reference_branch="main")
    feature_result = [r for r in report.results if r.branch == "feature"][0]
    assert feature_result.ratio == pytest.approx(2.0)


def test_normalize_uses_mean_of_reference_runs():
    results = [
        _r("bench_a", "main", 2.0),
        _r("bench_a", "main", 4.0),  # mean = 3.0
        _r("bench_a", "feature", 3.0),
    ]
    report = normalize(results, reference_branch="main")
    feature_result = [r for r in report.results if r.branch == "feature"][0]
    assert feature_result.reference_duration == pytest.approx(3.0)
    assert feature_result.ratio == pytest.approx(1.0)


def test_normalize_missing_reference_raises():
    results = [_r("bench_a", "feature", 1.0)]
    with pytest.raises(NormalizerError, match="reference branch 'main'"):
        normalize(results, reference_branch="main")


def test_normalize_excludes_failed_results():
    results = [
        _r("bench_a", "main", 2.0),
        _r("bench_a", "feature", 4.0, success=False),
    ]
    report = normalize(results, reference_branch="main")
    branches = {r.branch for r in report.results}
    assert "feature" not in branches


def test_normalize_skips_suite_missing_from_reference():
    results = [
        _r("bench_a", "main", 2.0),
        _r("bench_b", "feature", 5.0),  # bench_b not in reference
    ]
    report = normalize(results, reference_branch="main")
    suites = {r.suite for r in report.results}
    assert "bench_b" not in suites


def test_by_branch_filters_correctly():
    results = [
        _r("bench_a", "main", 2.0),
        _r("bench_a", "dev", 3.0),
    ]
    report = normalize(results, reference_branch="main")
    dev_results = report.by_branch("dev")
    assert all(r.branch == "dev" for r in dev_results)


def test_by_suite_filters_correctly():
    results = [
        _r("bench_a", "main", 2.0),
        _r("bench_b", "main", 1.0),
    ]
    report = normalize(results, reference_branch="main")
    suite_results = report.by_suite("bench_a")
    assert all(r.suite == "bench_a" for r in suite_results)
