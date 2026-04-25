"""Tests for batchmark.evolver."""
import pytest
from unittest.mock import MagicMock

from batchmark.evolver import (
    EvolutionPoint,
    SuiteEvolution,
    EvolveReport,
    build_evolution,
)


def _result(success=True, duration=100.0):
    r = MagicMock()
    r.success = success
    r.duration_ms = duration
    return r


def _suite_cmp(candidate_results, regressions=(), improvements=()):
    cmp = MagicMock()
    cmp.candidate_results = candidate_results
    cmp.regressions.return_value = list(regressions)
    cmp.improvements.return_value = list(improvements)
    return cmp


def _comp_report(suites_dict):
    r = MagicMock()
    r.comparisons = suites_dict
    return r


def test_build_evolution_empty():
    report = build_evolution([])
    assert report.all_suite_names() == []


def test_build_evolution_single_snapshot():
    cmp = _suite_cmp([_result(duration=200.0), _result(duration=100.0)])
    comp = _comp_report({"suite_a": cmp})
    report = build_evolution([("v1", comp)])
    assert "suite_a" in report.suites
    evo = report.suites["suite_a"]
    assert len(evo.points) == 1
    assert evo.points[0].label == "v1"
    assert evo.points[0].mean_duration == pytest.approx(150.0)


def test_build_evolution_two_snapshots_net_change():
    cmp1 = _suite_cmp([_result(duration=200.0)])
    cmp2 = _suite_cmp([_result(duration=100.0)])
    comp1 = _comp_report({"suite_a": cmp1})
    comp2 = _comp_report({"suite_a": cmp2})
    report = build_evolution([("v1", comp1), ("v2", comp2)])
    evo = report.suites["suite_a"]
    assert evo.net_change() == pytest.approx(-100.0)
    assert evo.verdict() == "improving"


def test_build_evolution_degrading():
    cmp1 = _suite_cmp([_result(duration=50.0)])
    cmp2 = _suite_cmp([_result(duration=150.0)])
    comp1 = _comp_report({"s": cmp1})
    comp2 = _comp_report({"s": cmp2})
    report = build_evolution([("a", comp1), ("b", comp2)])
    assert report.suites["s"].verdict() == "degrading"


def test_build_evolution_excludes_failed_results():
    cmp = _suite_cmp([_result(success=False, duration=9999.0), _result(duration=100.0)])
    comp = _comp_report({"suite_x": cmp})
    report = build_evolution([("v1", comp)])
    assert report.suites["suite_x"].points[0].mean_duration == pytest.approx(100.0)


def test_suite_evolution_single_point_net_change_is_none():
    evo = SuiteEvolution(suite_name="s", points=[EvolutionPoint("v1", 100.0, 0, 0)])
    assert evo.net_change() is None
    assert evo.verdict() == "unknown"


def test_suite_evolution_stable():
    evo = SuiteEvolution(
        suite_name="s",
        points=[
            EvolutionPoint("v1", 100.0, 0, 0),
            EvolutionPoint("v2", 100.0, 0, 0),
        ],
    )
    assert evo.verdict() == "stable"
    assert evo.net_change() == pytest.approx(0.0)
