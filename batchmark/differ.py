"""Diff two benchmark reports to produce a structured delta summary."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.comparator import ComparisonReport, SuiteComparison


@dataclass
class SuiteDelta:
    suite_name: str
    baseline_mean: Optional[float]
    candidate_mean: Optional[float]
    delta_pct: Optional[float]  # positive = slower, negative = faster
    only_in_baseline: bool = False
    only_in_candidate: bool = False


@dataclass
class ReportDiff:
    baseline_branch: str
    candidate_branch: str
    deltas: List[SuiteDelta] = field(default_factory=list)

    @property
    def regressions(self) -> List[SuiteDelta]:
        return [d for d in self.deltas if d.delta_pct is not None and d.delta_pct > 0]

    @property
    def improvements(self) -> List[SuiteDelta]:
        return [d for d in self.deltas if d.delta_pct is not None and d.delta_pct < 0]


def _mean(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def diff_reports(report: ComparisonReport) -> ReportDiff:
    """Build a ReportDiff from a ComparisonReport."""
    result = ReportDiff(
        baseline_branch=report.baseline_branch,
        candidate_branch=report.candidate_branch,
    )

    for suite_name, comparison in report.comparisons.items():
        baseline_times = [
            r.duration_s for r in comparison.baseline_results if r.success
        ]
        candidate_times = [
            r.duration_s for r in comparison.candidate_results if r.success
        ]

        b_mean = _mean(baseline_times)
        c_mean = _mean(candidate_times)

        only_baseline = bool(baseline_times) and not candidate_times
        only_candidate = bool(candidate_times) and not baseline_times

        if b_mean is not None and c_mean is not None:
            delta_pct = ((c_mean - b_mean) / b_mean) * 100.0
        else:
            delta_pct = None

        result.deltas.append(
            SuiteDelta(
                suite_name=suite_name,
                baseline_mean=b_mean,
                candidate_mean=c_mean,
                delta_pct=delta_pct,
                only_in_baseline=only_baseline,
                only_in_candidate=only_candidate,
            )
        )

    return result
