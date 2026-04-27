"""Maturity scoring: assess how stable/reliable a suite is across runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from batchmark.aggregator import AggregateReport


@dataclass
class SuiteMaturity:
    suite: str
    branch: str
    run_count: int
    success_rate: float  # 0.0 – 1.0
    cv: float            # coefficient of variation (stdev/mean); lower = more stable
    verdict: str         # "stable" | "unstable" | "flaky"


@dataclass
class MaturityReport:
    entries: List[SuiteMaturity] = field(default_factory=list)

    def stable(self) -> List[SuiteMaturity]:
        return [e for e in self.entries if e.verdict == "stable"]

    def unstable(self) -> List[SuiteMaturity]:
        return [e for e in self.entries if e.verdict == "unstable"]

    def flaky(self) -> List[SuiteMaturity]:
        return [e for e in self.entries if e.verdict == "flaky"]


def _stdev(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return variance ** 0.5


def _verdict(success_rate: float, cv: float) -> str:
    if success_rate < 0.7:
        return "flaky"
    if cv > 0.25:
        return "unstable"
    return "stable"


def build_maturity_report(aggregate: AggregateReport) -> MaturityReport:
    """Derive maturity from an AggregateReport."""
    entries: List[SuiteMaturity] = []
    for agg in aggregate.suites:
        durations = [r for r in agg.durations if r > 0]
        mean_dur = sum(durations) / len(durations) if durations else 0.0
        cv = (_stdev(durations) / mean_dur) if mean_dur > 0 else 0.0
        entries.append(
            SuiteMaturity(
                suite=agg.suite,
                branch=agg.branch,
                run_count=agg.total_runs,
                success_rate=agg.success_rate,
                cv=round(cv, 4),
                verdict=_verdict(agg.success_rate, cv),
            )
        )
    return MaturityReport(entries=entries)
