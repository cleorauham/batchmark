"""Tests for batchmark.watchdog."""
import pytest
from unittest.mock import MagicMock
from batchmark.watchdog import WatchdogRule, evaluate, WatchdogReport


def _cmp(suite, baseline_mean, candidate_mean):
    c = MagicMock()
    c.suite = suite
    c.baseline_mean = baseline_mean
    c.candidate_mean = candidate_mean
    return c


def _report(*cmps):
    r = MagicMock()
    r.comparisons = list(cmps)
    return r


def test_no_alerts_when_within_threshold():
    report = _report(_cmp("suite_a", 1.0, 1.05))
    rules = [WatchdogRule(suite="suite_a", max_regression_pct=10.0)]
    wd = evaluate(report, rules)
    assert not wd.has_alerts


def test_regression_pct_alert():
    report = _report(_cmp("suite_a", 1.0, 1.20))
    rules = [WatchdogRule(suite="suite_a", max_regression_pct=10.0)]
    wd = evaluate(report, rules)
    assert wd.has_alerts
    assert wd.alerts[0].reason == "regression_pct"
    assert wd.alerts[0].suite == "suite_a"


def test_max_duration_alert():
    report = _report(_cmp("suite_b", 1.0, 6.0))
    rules = [WatchdogRule(suite="suite_b", max_duration_s=5.0)]
    wd = evaluate(report, rules)
    assert wd.has_alerts
    assert wd.alerts[0].reason == "max_duration_s"
    assert wd.alerts[0].value == pytest.approx(6.0)


def test_no_rule_no_alert():
    report = _report(_cmp("suite_x", 1.0, 9999.0))
    wd = evaluate(report, [])
    assert not wd.has_alerts


def test_multiple_alerts():
    report = _report(
        _cmp("a", 1.0, 2.0),
        _cmp("b", 1.0, 10.0),
    )
    rules = [
        WatchdogRule(suite="a", max_regression_pct=5.0),
        WatchdogRule(suite="b", max_regression_pct=5.0, max_duration_s=3.0),
    ]
    wd = evaluate(report, rules)
    assert len(wd.alerts) == 3


def test_alert_str():
    report = _report(_cmp("s", 1.0, 1.5))
    rules = [WatchdogRule(suite="s", max_regression_pct=10.0)]
    wd = evaluate(report, rules)
    assert "ALERT" in str(wd.alerts[0])
    assert "s" in str(wd.alerts[0])
