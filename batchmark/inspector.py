"""Inspect individual benchmark results across branches for a given suite."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from batchmark.runner import BenchmarkResult


@dataclass
class SuiteInspection:
    suite: str
    branches: List[str]
    results: Dict[str, BenchmarkResult]  # branch -> result

    def get(self, branch: str) -> Optional[BenchmarkResult]:
        return self.results.get(branch)

    def fastest(self) -> Optional[str]:
        times = {
            b: r.duration
            for b, r in self.results.items()
            if r.success and r.duration is not None
        }
        return min(times, key=times.__getitem__) if times else None

    def slowest(self) -> Optional[str]:
        times = {
            b: r.duration
            for b, r in self.results.items()
            if r.success and r.duration is not None
        }
        return max(times, key=times.__getitem__) if times else None

    def spread(self) -> Optional[float]:
        times = [
            r.duration
            for r in self.results.values()
            if r.success and r.duration is not None
        ]
        if len(times) < 2:
            return None
        return max(times) - min(times)


@dataclass
class InspectReport:
    inspections: List[SuiteInspection] = field(default_factory=list)

    def for_suite(self, suite: str) -> Optional[SuiteInspection]:
        for ins in self.inspections:
            if ins.suite == suite:
                return ins
        return None


def inspect_report(results: List[BenchmarkResult], branches: List[str]) -> InspectReport:
    """Group results by suite and build an InspectReport."""
    by_suite: Dict[str, Dict[str, BenchmarkResult]] = {}
    for r in results:
        by_suite.setdefault(r.suite, {})[r.branch] = r
    inspections = [
        SuiteInspection(suite=suite, branches=branches, results=branch_map)
        for suite, branch_map in sorted(by_suite.items())
    ]
    return InspectReport(inspections=inspections)
