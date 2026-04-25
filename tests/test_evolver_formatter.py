"""Tests for batchmark.evolver_formatter."""
from batchmark.evolver import EvolveReport, SuiteEvolution, EvolutionPoint
from batchmark.evolver_formatter import format_evolution_report


def _evo(name, points):
    return SuiteEvolution(suite_name=name, points=points)


def _pt(label, mean, reg=0, imp=0):
    return EvolutionPoint(label=label, mean_duration=mean, regression_count=reg, improvement_count=imp)


def test_format_empty_returns_warning():
    report = EvolveReport()
    out = format_evolution_report(report)
    assert "No evolution data" in out


def test_format_shows_suite_name():
    report = EvolveReport(suites={"my_suite": _evo("my_suite", [_pt("v1", 100.0)])})
    out = format_evolution_report(report)
    assert "my_suite" in out


def test_format_shows_verdict_improving():
    report = EvolveReport(
        suites={
            "s": _evo("s", [_pt("v1", 200.0), _pt("v2", 100.0)])
        }
    )
    out = format_evolution_report(report)
    assert "IMPROVING" in out


def test_format_shows_verdict_degrading():
    report = EvolveReport(
        suites={
            "s": _evo("s", [_pt("v1", 100.0), _pt("v2", 300.0)])
        }
    )
    out = format_evolution_report(report)
    assert "DEGRADING" in out


def test_format_shows_snapshot_labels():
    report = EvolveReport(
        suites={
            "s": _evo("s", [_pt("alpha", 50.0), _pt("beta", 60.0)])
        }
    )
    out = format_evolution_report(report)
    assert "alpha" in out
    assert "beta" in out


def test_format_shows_net_delta():
    report = EvolveReport(
        suites={
            "s": _evo("s", [_pt("v1", 100.0), _pt("v2", 150.0)])
        }
    )
    out = format_evolution_report(report)
    assert "Net" in out
    assert "50.00ms" in out
