"""Aggregate benchmark results across multiple runs into statistical summaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import statistics

from batchmark.runner import BenchmarkResult


@dataclass
class AggregatedSuite:
    suite: str
    branch: str
    runs: int
    mean: float
    median: float
    stdev: float
    min_duration: float
    max_duration: float
    failed_runs: int

    @property
    def success_rate(self) -> float:
        total = self.runs + self.failed_runs
        return self.runs / total if total > 0 else 0.0


@dataclass
class AggregateReport:
    entries: List[AggregatedSuite] = field(default_factory=list)

    def by_branch(self, branch: str) -> List[AggregatedSuite]:
        return [e for e in self.entries if e.branch == branch]

    def by_suite(self, suite: str) -> List[AggregatedSuite]:
        return [e for e in self.entries if e.suite == suite]

    def branches(self) -> List[str]:
        return sorted({e.branch for e in self.entries})

    def suite_names(self) -> List[str]:
        return sorted({e.suite for e in self.entries})


def aggregate(results: List[BenchmarkResult]) -> AggregateReport:
    """Group results by (suite, branch) and compute statistics."""
    groups: Dict[tuple, Dict[str, list]] = {}

    for r in results:
        key = (r.suite, r.branch)
        if key not in groups:
            groups[key] = {"ok": [], "failed": 0}
        if r.success and r.duration is not None:
            groups[key]["ok"].append(r.duration)
        else:
            groups[key]["failed"] += 1

    entries: List[AggregatedSuite] = []
    for (suite, branch), data in sorted(groups.items()):
        durations = data["ok"]
        failed = data["failed"]
        if not durations:
            entries.append(AggregatedSuite(
                suite=suite, branch=branch, runs=0,
                mean=0.0, median=0.0, stdev=0.0,
                min_duration=0.0, max_duration=0.0,
                failed_runs=failed,
            ))
            continue
        entries.append(AggregatedSuite(
            suite=suite,
            branch=branch,
            runs=len(durations),
            mean=statistics.mean(durations),
            median=statistics.median(durations),
            stdev=statistics.stdev(durations) if len(durations) > 1 else 0.0,
            min_duration=min(durations),
            max_duration=max(durations),
            failed_runs=failed,
        ))
    return AggregateReport(entries=entries)
