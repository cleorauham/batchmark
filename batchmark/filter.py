"""Filtering utilities for benchmark suites and results."""

from __future__ import annotations

from typing import List, Optional

from batchmark.config import BenchmarkSuite
from batchmark.comparator import ComparisonReport, SuiteComparison


def filter_suites(
    suites: List[BenchmarkSuite],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> List[BenchmarkSuite]:
    """Return suites matching include/exclude name filters."""
    result = suites
    if include:
        include_set = set(include)
        result = [s for s in result if s.name in include_set]
    if exclude:
        exclude_set = set(exclude)
        result = [s for s in result if s.name not in exclude_set]
    return result


def filter_report(
    report: ComparisonReport,
    only_regressions: bool = False,
    only_improvements: bool = False,
    min_delta_pct: float = 0.0,
) -> ComparisonReport:
    """Return a new ComparisonReport with comparisons filtered by criteria.

    Args:
        report: The comparison report to filter.
        only_regressions: If True, keep only comparisons where performance got worse
            (positive delta_pct).
        only_improvements: If True, keep only comparisons where performance improved
            (negative delta_pct).
        min_delta_pct: Minimum absolute percentage change to include. Comparisons
            with a delta below this threshold are excluded.

    Returns:
        A new ComparisonReport containing only the comparisons that match the
        specified criteria.

    Raises:
        ValueError: If both only_regressions and only_improvements are True.
    """
    comparisons = report.comparisons

    if only_regressions and only_improvements:
        raise ValueError("Cannot filter for both regressions and improvements simultaneously.")

    if only_regressions:
        comparisons = [c for c in comparisons if c.delta_pct is not None and c.delta_pct > 0]
    elif only_improvements:
        comparisons = [c for c in comparisons if c.delta_pct is not None and c.delta_pct < 0]

    if min_delta_pct > 0.0:
        comparisons = [
            c for c in comparisons
            if c.delta_pct is not None and abs(c.delta_pct) >= min_delta_pct
        ]

    return ComparisonReport(
        baseline_branch=report.baseline_branch,
        candidate_branch=report.candidate_branch,
        comparisons=comparisons,
    )
