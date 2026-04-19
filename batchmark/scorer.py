"""Score benchmark results into a single weighted value per branch."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from batchmark.comparator import ComparisonReport, SuiteComparison


@dataclass
class SuiteScore:
    suite: str
    branch: str
    mean_duration: float
    weight: float
    weighted_score: float


@dataclass
class ScoreReport:
    branches: List[str]
    scores: List[SuiteScore] = field(default_factory=list)

    def total(self, branch: str) -> float:
        return sum(s.weighted_score for s in self.scores if s.branch == branch)

    def by_branch(self) -> Dict[str, float]:
        return {b: self.total(b) for b in self.branches}


def _mean(values: List[float]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def score_report(
    report: ComparisonReport,
    weights: Optional[Dict[str, float]] = None,
) -> ScoreReport:
    """Compute weighted scores for each branch across all suites.

    Lower duration = better score (score = 1 / mean_duration).
    weights maps suite name -> float multiplier (default 1.0).
    """
    weights = weights or {}
    score_report_obj = ScoreReport(branches=list(report.branches))

    for cmp in report.comparisons:
        weight = weights.get(cmp.suite, 1.0)
        for branch, results in cmp.results_by_branch.items():
            durations = [r.duration for r in results if r.success]
            mean = _mean(durations)
            if mean is None or mean == 0:
                continue
            raw = 1.0 / mean
            score_report_obj.scores.append(
                SuiteScore(
                    suite=cmp.suite,
                    branch=branch,
                    mean_duration=mean,
                    weight=weight,
                    weighted_score=raw * weight,
                )
            )

    return score_report_obj
