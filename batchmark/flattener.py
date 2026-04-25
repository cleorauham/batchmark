"""Flatten a ComparisonReport into a list of plain dicts for tabular output."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.comparator import ComparisonReport, SuiteComparison


@dataclass
class FlatRow:
    suite: str
    baseline_branch: str
    candidate_branch: str
    baseline_mean: Optional[float]
    candidate_mean: Optional[float]
    delta_pct: Optional[float]
    verdict: str  # 'improvement', 'regression', 'unchanged', 'missing'

    def to_dict(self) -> dict:
        return {
            "suite": self.suite,
            "baseline_branch": self.baseline_branch,
            "candidate_branch": self.candidate_branch,
            "baseline_mean": self.baseline_mean,
            "candidate_mean": self.candidate_mean,
            "delta_pct": self.delta_pct,
            "verdict": self.verdict,
        }


@dataclass
class FlatReport:
    rows: List[FlatRow]

    def to_dicts(self) -> List[dict]:
        return [r.to_dict() for r in self.rows]

    def filter_verdict(self, verdict: str) -> "FlatReport":
        return FlatReport([r for r in self.rows if r.verdict == verdict])


def _verdict(cmp: SuiteComparison) -> str:
    if cmp.baseline_mean is None or cmp.candidate_mean is None:
        return "missing"
    if cmp.delta_pct is None:
        return "unchanged"
    if cmp.delta_pct < -0.01:
        return "improvement"
    if cmp.delta_pct > 0.01:
        return "regression"
    return "unchanged"


def flatten_report(report: ComparisonReport) -> FlatReport:
    """Convert a ComparisonReport into a FlatReport of FlatRow objects."""
    rows: List[FlatRow] = []
    for cmp in report.comparisons:
        rows.append(
            FlatRow(
                suite=cmp.suite_name,
                baseline_branch=report.baseline_branch,
                candidate_branch=report.candidate_branch,
                baseline_mean=cmp.baseline_mean,
                candidate_mean=cmp.candidate_mean,
                delta_pct=cmp.delta_pct,
                verdict=_verdict(cmp),
            )
        )
    return FlatReport(rows)
