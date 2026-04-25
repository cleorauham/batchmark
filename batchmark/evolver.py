"""Tracks how benchmark results evolve across multiple report snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EvolutionPoint:
    label: str
    mean_duration: float
    regression_count: int
    improvement_count: int


@dataclass
class SuiteEvolution:
    suite_name: str
    points: List[EvolutionPoint] = field(default_factory=list)

    def first(self) -> Optional[EvolutionPoint]:
        return self.points[0] if self.points else None

    def last(self) -> Optional[EvolutionPoint]:
        return self.points[-1] if self.points else None

    def net_change(self) -> Optional[float]:
        if len(self.points) < 2:
            return None
        return self.last().mean_duration - self.first().mean_duration  # type: ignore[union-attr]

    def verdict(self) -> str:
        delta = self.net_change()
        if delta is None:
            return "unknown"
        if delta < 0:
            return "improving"
        if delta > 0:
            return "degrading"
        return "stable"


@dataclass
class EvolveReport:
    suites: Dict[str, SuiteEvolution] = field(default_factory=dict)

    def all_suite_names(self) -> List[str]:
        return sorted(self.suites.keys())


def build_evolution(labeled_reports: List[tuple]) -> EvolveReport:
    """Build an evolution report from a list of (label, ComparisonReport) tuples."""
    report = EvolveReport()
    for label, comp_report in labeled_reports:
        for suite_name, suite_cmp in comp_report.comparisons.items():
            if suite_name not in report.suites:
                report.suites[suite_name] = SuiteEvolution(suite_name=suite_name)
            durations = [
                r.duration_ms
                for r in suite_cmp.candidate_results
                if r.success
            ]
            mean_dur = sum(durations) / len(durations) if durations else 0.0
            point = EvolutionPoint(
                label=label,
                mean_duration=mean_dur,
                regression_count=len(suite_cmp.regressions()),
                improvement_count=len(suite_cmp.improvements()),
            )
            report.suites[suite_name].points.append(point)
    return report
