"""Isolate benchmark results by branch and suite, detecting anomalies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class IsolatedSuite:
    suite: str
    branch: str
    durations: List[float]
    mean: float
    stdev: float
    is_anomalous: bool


@dataclass
class IsolateReport:
    branch_a: str
    branch_b: str
    suites: List[IsolatedSuite] = field(default_factory=list)

    def anomalous(self) -> List[IsolatedSuite]:
        return [s for s in self.suites if s.is_anomalous]

    def by_suite(self, name: str) -> List[IsolatedSuite]:
        return [s for s in self.suites if s.suite == name]


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _stdev(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    variance = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return variance ** 0.5


def isolate(results: list, branch_a: str, branch_b: str, threshold: float = 0.2) -> IsolateReport:
    """Group results by suite/branch and flag suites whose mean differs by > threshold."""
    from collections import defaultdict

    buckets: Dict[tuple, List[float]] = defaultdict(list)
    for r in results:
        if getattr(r, "success", False):
            key = (getattr(r, "suite", ""), getattr(r, "branch", ""))
            buckets[key].append(getattr(r, "duration", 0.0))

    suite_names = {k[0] for k in buckets}
    report = IsolateReport(branch_a=branch_a, branch_b=branch_b)

    for suite in sorted(suite_names):
        durs_a = buckets.get((suite, branch_a), [])
        durs_b = buckets.get((suite, branch_b), [])
        if not durs_a or not durs_b:
            continue
        mean_a = _mean(durs_a)
        mean_b = _mean(durs_b)
        diff = abs(mean_a - mean_b) / mean_a if mean_a else 0.0
        is_anomalous = diff > threshold
        for branch, durs in ((branch_a, durs_a), (branch_b, durs_b)):
            report.suites.append(IsolatedSuite(
                suite=suite,
                branch=branch,
                durations=durs,
                mean=_mean(durs),
                stdev=_stdev(durs),
                is_anomalous=is_anomalous,
            ))

    return report
