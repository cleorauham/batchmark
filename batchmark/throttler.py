"""Throttler: limit the number of benchmark results processed per branch/suite."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from batchmark.runner import BenchmarkResult


class ThrottleError(Exception):
    """Raised when throttle configuration is invalid."""


@dataclass
class ThrottleReport:
    kept: List[BenchmarkResult] = field(default_factory=list)
    dropped: List[BenchmarkResult] = field(default_factory=list)

    @property
    def total_kept(self) -> int:
        return len(self.kept)

    @property
    def total_dropped(self) -> int:
        return len(self.dropped)

    def by_branch(self) -> Dict[str, List[BenchmarkResult]]:
        groups: Dict[str, List[BenchmarkResult]] = {}
        for r in self.kept:
            groups.setdefault(r.branch, []).append(r)
        return groups

    def by_suite(self) -> Dict[str, List[BenchmarkResult]]:
        groups: Dict[str, List[BenchmarkResult]] = {}
        for r in self.kept:
            groups.setdefault(r.suite, []).append(r)
        return groups

    def summary(self) -> str:
        """Return a human-readable one-line summary of the report."""
        total = self.total_kept + self.total_dropped
        return (
            f"{self.total_kept}/{total} results kept, "
            f"{self.total_dropped} dropped "
            f"({len(self.by_branch())} branch(es), {len(self.by_suite())} suite(s))"
        )


def throttle(
    results: Sequence[BenchmarkResult],
    max_per_branch: int | None = None,
    max_per_suite: int | None = None,
) -> ThrottleReport:
    """Keep at most *max_per_branch* results per branch and *max_per_suite* per suite.

    Results are processed in the order supplied; earlier entries take priority.
    Raises ThrottleError if limits are not positive integers.
    """
    if max_per_branch is not None and max_per_branch < 1:
        raise ThrottleError("max_per_branch must be a positive integer")
    if max_per_suite is not None and max_per_suite < 1:
        raise ThrottleError("max_per_suite must be a positive integer")

    branch_counts: Dict[str, int] = {}
    suite_counts: Dict[str, int] = {}
    report = ThrottleReport()

    for result in results:
        b_count = branch_counts.get(result.branch, 0)
        s_count = suite_counts.get(result.suite, 0)

        over_branch = max_per_branch is not None and b_count >= max_per_branch
        over_suite = max_per_suite is not None and s_count >= max_per_suite

        if over_branch or over_suite:
            report.dropped.append(result)
        else:
            report.kept.append(result)
            branch_counts[result.branch] = b_count + 1
            suite_counts[result.suite] = s_count + 1

    return report
