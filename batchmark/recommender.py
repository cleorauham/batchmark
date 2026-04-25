"""Recommender: suggest which branches or suites to investigate based on patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from batchmark.comparator import ComparisonReport, SuiteComparison


@dataclass
class Recommendation:
    kind: str          # 'investigate' | 'promote' | 'skip'
    branch: str
    suite: str
    reason: str

    def __str__(self) -> str:
        return f"[{self.kind.upper()}] {self.branch}/{self.suite}: {self.reason}"


@dataclass
class RecommendationReport:
    recommendations: List[Recommendation] = field(default_factory=list)

    def by_kind(self, kind: str) -> List[Recommendation]:
        return [r for r in self.recommendations if r.kind == kind]

    @property
    def investigate(self) -> List[Recommendation]:
        return self.by_kind("investigate")

    @property
    def promote(self) -> List[Recommendation]:
        return self.by_kind("promote")

    @property
    def skip(self) -> List[Recommendation]:
        return self.by_kind("skip")


def _pct_change(baseline: float, candidate: float) -> float:
    if baseline == 0:
        return 0.0
    return (candidate - baseline) / baseline * 100.0


def build_recommendations(
    report: ComparisonReport,
    investigate_threshold: float = 10.0,
    promote_threshold: float = -5.0,
) -> RecommendationReport:
    """Produce recommendations from a ComparisonReport.

    - 'investigate' when a suite regressed by more than *investigate_threshold* %.
    - 'promote'     when a suite improved by more than abs(*promote_threshold*) %.
    - 'skip'        when baseline or candidate result is missing / failed.
    """
    recs: List[Recommendation] = []

    for cmp in report.comparisons:
        baseline = cmp.baseline
        candidate = cmp.candidate
        suite = cmp.suite_name
        branch = report.candidate_branch

        if baseline is None or candidate is None:
            recs.append(Recommendation("skip", branch, suite, "missing result in one branch"))
            continue

        if not baseline.success or not candidate.success:
            recs.append(Recommendation("skip", branch, suite, "one or more runs failed"))
            continue

        pct = _pct_change(baseline.duration, candidate.duration)

        if pct >= investigate_threshold:
            recs.append(Recommendation(
                "investigate", branch, suite,
                f"duration increased by {pct:.1f}%"
            ))
        elif pct <= promote_threshold:
            recs.append(Recommendation(
                "promote", branch, suite,
                f"duration decreased by {abs(pct):.1f}%"
            ))

    return RecommendationReport(recommendations=recs)
