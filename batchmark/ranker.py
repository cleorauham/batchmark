"""Rank branches by aggregate benchmark performance."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from batchmark.comparator import ComparisonReport


@dataclass
class BranchRank:
    branch: str
    mean_duration: float
    suite_count: int
    rank: int = 0


@dataclass
class RankReport:
    branches: List[BranchRank] = field(default_factory=list)

    def best(self) -> BranchRank | None:
        return self.branches[0] if self.branches else None

    def worst(self) -> BranchRank | None:
        return self.branches[-1] if self.branches else None


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def rank_report(report: ComparisonReport) -> RankReport:
    """Compute per-branch mean duration across all successful suite results."""
    durations: Dict[str, List[float]] = {}

    for branch in report.branches:
        durations[branch] = []

    for cmp in report.comparisons:
        for branch, result in cmp.results.items():
            if result.success:
                durations.setdefault(branch, []).append(result.duration)

    ranks: List[BranchRank] = []
    for branch, durs in durations.items():
        ranks.append(BranchRank(
            branch=branch,
            mean_duration=_mean(durs),
            suite_count=len(durs),
        ))

    ranks.sort(key=lambda r: r.mean_duration)
    for i, r in enumerate(ranks):
        r.rank = i + 1

    return RankReport(branches=ranks)
