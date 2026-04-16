"""Summarize benchmark results across branches into a flat statistics table."""
from dataclasses import dataclass
from typing import List, Dict, Optional
from batchmark.comparator import ComparisonReport, SuiteComparison


@dataclass
class SuiteSummaryRow:
    suite: str
    baseline_mean: Optional[float]
    candidate_mean: Optional[float]
    delta_pct: Optional[float]
    verdict: str  # 'improved', 'regressed', 'unchanged', 'missing'


def _mean(values: List[float]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def _verdict(delta_pct: Optional[float], threshold: float = 5.0) -> str:
    if delta_pct is None:
        return "missing"
    if delta_pct <= -threshold:
        return "improved"
    if delta_pct >= threshold:
        return "regressed"
    return "unchanged"


def summarize_report(report: ComparisonReport, threshold: float = 5.0) -> List[SuiteSummaryRow]:
    """Convert a ComparisonReport into a list of SuiteSummaryRows."""
    rows: List[SuiteSummaryRow] = []
    for cmp in report.comparisons:
        baseline_times = [r.elapsed for r in cmp.baseline_results if r.success]
        candidate_times = [r.elapsed for r in cmp.candidate_results if r.success]

        b_mean = _mean(baseline_times)
        c_mean = _mean(candidate_times)

        if b_mean is not None and c_mean is not None and b_mean > 0:
            delta_pct = ((c_mean - b_mean) / b_mean) * 100.0
        else:
            delta_pct = None

        rows.append(SuiteSummaryRow(
            suite=cmp.suite,
            baseline_mean=b_mean,
            candidate_mean=c_mean,
            delta_pct=delta_pct,
            verdict=_verdict(delta_pct, threshold),
        ))
    return rows


def summary_counts(rows: List[SuiteSummaryRow]) -> Dict[str, int]:
    counts: Dict[str, int] = {"improved": 0, "regressed": 0, "unchanged": 0, "missing": 0}
    for row in rows:
        counts[row.verdict] = counts.get(row.verdict, 0) + 1
    return counts
