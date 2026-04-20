"""Outlier detection for benchmark results.

Identifies suites whose durations deviate significantly from the mean
across branches, using a configurable z-score threshold.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.comparator import ComparisonReport, SuiteComparison


_DEFAULT_THRESHOLD = 2.0  # z-score threshold for flagging outliers


@dataclass
class OutlierEntry:
    """A single suite flagged as an outlier."""

    suite_name: str
    branch: str
    duration: float
    mean: float
    stdev: float
    z_score: float

    @property
    def direction(self) -> str:
        """Return 'slow' if above mean, 'fast' if below."""
        return "slow" if self.duration > self.mean else "fast"


@dataclass
class OutlierReport:
    """Collection of outlier entries detected across all branches."""

    entries: List[OutlierEntry] = field(default_factory=list)
    threshold: float = _DEFAULT_THRESHOLD

    @property
    def has_outliers(self) -> bool:
        return len(self.entries) > 0

    def by_branch(self, branch: str) -> List[OutlierEntry]:
        """Return all outliers for a specific branch."""
        return [e for e in self.entries if e.branch == branch]

    def by_suite(self, suite_name: str) -> List[OutlierEntry]:
        """Return all outliers for a specific suite."""
        return [e for e in self.entries if e.suite_name == suite_name]


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _stdev(values: List[float], mean: float) -> float:
    if len(values) < 2:
        return 0.0
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(variance)


def _collect_durations(report: ComparisonReport) -> Dict[str, Dict[str, float]]:
    """Build a mapping of {suite_name: {branch: duration}} from a report."""
    data: Dict[str, Dict[str, float]] = {}
    for suite_name, comparison in report.comparisons.items():
        branch_durations: Dict[str, float] = {}
        if comparison.baseline is not None and comparison.baseline.success:
            branch_durations[report.baseline_branch] = comparison.baseline.duration
        if comparison.candidate is not None and comparison.candidate.success:
            branch_durations[report.candidate_branch] = comparison.candidate.duration
        if branch_durations:
            data[suite_name] = branch_durations
    return data


def detect_outliers(
    report: ComparisonReport,
    threshold: float = _DEFAULT_THRESHOLD,
) -> OutlierReport:
    """Detect benchmark outliers in a comparison report.

    For each suite, collects durations across branches and flags any branch
    whose duration deviates from the cross-branch mean by more than
    `threshold` standard deviations.

    Args:
        report: The comparison report to analyse.
        threshold: Z-score threshold above which a result is flagged.

    Returns:
        An OutlierReport containing all flagged entries.
    """
    outlier_report = OutlierReport(threshold=threshold)
    data = _collect_durations(report)

    for suite_name, branch_durations in data.items():
        values = list(branch_durations.values())
        if len(values) < 2:
            # Cannot compute z-score with a single data point
            continue

        mu = _mean(values)
        sigma = _stdev(values, mu)

        if sigma == 0.0:
            continue

        for branch, duration in branch_durations.items():
            z = abs(duration - mu) / sigma
            if z >= threshold:
                outlier_report.entries.append(
                    OutlierEntry(
                        suite_name=suite_name,
                        branch=branch,
                        duration=duration,
                        mean=mu,
                        stdev=sigma,
                        z_score=z,
                    )
                )

    # Sort by descending z-score so the most extreme outliers appear first
    outlier_report.entries.sort(key=lambda e: e.z_score, reverse=True)
    return outlier_report
