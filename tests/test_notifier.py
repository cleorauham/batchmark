"""Tests for batchmark.notifier."""
from __future__ import annotations
import pytest
from unittest.mock import MagicMock
from batchmark.notifier import (
    Notifier, NotifyEvent, build_event, stdout_hook, threshold_hook
)
from batchmark.comparator import ComparisonReport, SuiteComparison
from batchmark.runner import BenchmarkResult


def _result(name: str, duration: float) -> BenchmarkResult:
    r = BenchmarkResult(suite=name, branch="b", duration=duration, exit_code=0, output="")
    return r


def _report(pairs):
    comparisons = []
    for suite, base_d, cmp_d in pairs:
        baseline = _result(suite, base_d)
        candidate = _result(suite, cmp_d)
        comparisons.append(SuiteComparison(suite=suite, baseline=baseline, candidate=candidate))
    return ComparisonReport(branches=["main", "dev"], comparisons=comparisons)


def test_build_event_counts_regressions():
    report = _report([("s1", 1.0, 2.0), ("s2", 1.0, 0.5)])
    event = build_event(report)
    assert event.regressions == 1
    assert event.improvements == 1


def test_build_event_branches():
    report = _report([("s1", 1.0, 1.0)])
    event = build_event(report)
    assert event.branches == ["main", "dev"]


def test_notifier_calls_hooks():
    report = _report([("s1", 1.0, 1.0)])
    event = build_event(report)
    hook = MagicMock()
    n = Notifier()
    n.register(hook)
    n.notify(event)
    hook.assert_called_once_with(event)


def test_threshold_hook_raises_on_excess():
    report = _report([("s1", 1.0, 2.0), ("s2", 1.0, 3.0)])
    event = build_event(report)
    hook = threshold_hook(max_regressions=1)
    with pytest.raises(RuntimeError, match="threshold exceeded"):
        hook(event)


def test_threshold_hook_passes_within_limit():
    report = _report([("s1", 1.0, 2.0)])
    event = build_event(report)
    hook = threshold_hook(max_regressions=1)
    hook(event)  # should not raise


def test_stdout_hook_prints(capsys):
    report = _report([("s1", 1.0, 1.0)])
    event = build_event(report)
    stdout_hook(event)
    captured = capsys.readouterr()
    assert "batchmark" in captured.out
