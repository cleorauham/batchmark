"""Merge multiple ComparisonReports into a single unified report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from batchmark.comparator import ComparisonReport, SuiteComparison


class MergeError(Exception):
    pass


@dataclass
class MergeReport:
    branches: List[str]
    suites: Dict[str, List[SuiteComparison]] = field(default_factory=dict)

    def all_suite_names(self) -> List[str]:
        return sorted(self.suites.keys())

    def comparisons_for(self, suite_name: str) -> List[SuiteComparison]:
        return self.suites.get(suite_name, [])

    def total_suites(self) -> int:
        return len(self.suites)


def merge_reports(reports: List[ComparisonReport]) -> MergeReport:
    """Merge a list of ComparisonReports into one MergeReport.

    Each report may cover different branches; suites are grouped by name
    and all comparisons collected.
    """
    if not reports:
        raise MergeError("Cannot merge empty list of reports")

    seen_branches: List[str] = []
    for report in reports:
        for b in report.branches:
            if b not in seen_branches:
                seen_branches.append(b)

    merged_suites: Dict[str, List[SuiteComparison]] = {}
    for report in reports:
        for cmp in report.comparisons:
            merged_suites.setdefault(cmp.suite_name, []).append(cmp)

    return MergeReport(branches=seen_branches, suites=merged_suites)
