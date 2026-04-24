"""splitter.py – split a ComparisonReport into per-branch sub-reports."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from batchmark.comparator import ComparisonReport, SuiteComparison


class SplitError(Exception):
    """Raised when splitting cannot be performed."""


@dataclass
class BranchSlice:
    """A subset of comparisons that involve a specific branch."""

    branch: str
    comparisons: List[SuiteComparison] = field(default_factory=list)

    @property
    def suite_names(self) -> List[str]:
        return [c.suite_name for c in self.comparisons]

    @property
    def regression_count(self) -> int:
        return sum(
            1
            for c in self.comparisons
            if c.baseline is not None
            and c.candidate is not None
            and c.candidate.duration_s > c.baseline.duration_s
        )

    @property
    def improvement_count(self) -> int:
        return sum(
            1
            for c in self.comparisons
            if c.baseline is not None
            and c.candidate is not None
            and c.candidate.duration_s < c.baseline.duration_s
        )


@dataclass
class SplitReport:
    """Collection of per-branch slices derived from a single ComparisonReport."""

    baseline_branch: str
    candidate_branch: str
    slices: Dict[str, BranchSlice] = field(default_factory=dict)

    def for_branch(self, branch: str) -> BranchSlice:
        if branch not in self.slices:
            raise SplitError(f"Branch {branch!r} not found in split report.")
        return self.slices[branch]


def split_report(report: ComparisonReport) -> SplitReport:
    """Split *report* into one :class:`BranchSlice` per branch.

    Both the baseline branch and the candidate branch receive a slice that
    contains every :class:`SuiteComparison` from the original report.
    """
    if not report.comparisons:
        raise SplitError("Cannot split an empty ComparisonReport.")

    baseline_slice = BranchSlice(
        branch=report.baseline_branch, comparisons=list(report.comparisons)
    )
    candidate_slice = BranchSlice(
        branch=report.candidate_branch, comparisons=list(report.comparisons)
    )

    return SplitReport(
        baseline_branch=report.baseline_branch,
        candidate_branch=report.candidate_branch,
        slices={
            report.baseline_branch: baseline_slice,
            report.candidate_branch: candidate_slice,
        },
    )
