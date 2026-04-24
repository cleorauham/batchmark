"""Watchdog: monitor benchmark runs and emit alerts on threshold breaches."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from batchmark.comparator import ComparisonReport


@dataclass
class WatchdogRule:
    suite: str
    max_regression_pct: float = 10.0
    max_duration_s: float | None = None


@dataclass
class WatchdogAlert:
    suite: str
    reason: str
    value: float
    threshold: float

    def __str__(self) -> str:
        return f"[ALERT] {self.suite}: {self.reason} ({self.value:.2f} vs limit {self.threshold:.2f})"


@dataclass
class WatchdogReport:
    alerts: List[WatchdogAlert] = field(default_factory=list)

    @property
    def has_alerts(self) -> bool:
        return bool(self.alerts)

    def alerts_for_suite(self, suite: str) -> List[WatchdogAlert]:
        """Return all alerts belonging to the given suite name."""
        return [a for a in self.alerts if a.suite == suite]


def evaluate(report: ComparisonReport, rules: List[WatchdogRule]) -> WatchdogReport:
    """Check a ComparisonReport against watchdog rules and return alerts.

    Args:
        report: The comparison report produced by the comparator.
        rules: A list of WatchdogRule objects defining per-suite thresholds.

    Returns:
        A WatchdogReport containing any threshold breaches found.
    """
    rule_map: Dict[str, WatchdogRule] = {r.suite: r for r in rules}
    alerts: List[WatchdogAlert] = []

    for cmp in report.comparisons:
        rule = rule_map.get(cmp.suite)
        if rule is None:
            continue

        if cmp.baseline_mean is not None and cmp.candidate_mean is not None:
            if cmp.baseline_mean > 0:
                pct = (cmp.candidate_mean - cmp.baseline_mean) / cmp.baseline_mean * 100
                if pct > rule.max_regression_pct:
                    alerts.append(WatchdogAlert(
                        suite=cmp.suite,
                        reason="regression_pct",
                        value=pct,
                        threshold=rule.max_regression_pct,
                    ))

        if rule.max_duration_s is not None and cmp.candidate_mean is not None:
            if cmp.candidate_mean > rule.max_duration_s:
                alerts.append(WatchdogAlert(
                    suite=cmp.suite,
                    reason="max_duration_s",
                    value=cmp.candidate_mean,
                    threshold=rule.max_duration_s,
                ))

    return WatchdogReport(alerts=alerts)
