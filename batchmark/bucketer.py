"""Bucket benchmark results into performance tiers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.runner import BenchmarkResult


@dataclass
class Bucket:
    label: str
    min_duration: float  # seconds, inclusive
    max_duration: float  # seconds, exclusive (use inf for unbounded)
    results: List[BenchmarkResult] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.results)

    @property
    def suite_names(self) -> List[str]:
        return [r.suite for r in self.results]


@dataclass
class BucketReport:
    buckets: List[Bucket]
    branch: str
    total_results: int

    def by_label(self, label: str) -> Optional[Bucket]:
        for b in self.buckets:
            if b.label == label:
                return b
        return None

    def non_empty(self) -> List[Bucket]:
        return [b for b in self.buckets if len(b) > 0]


class BucketerError(Exception):
    pass


_DEFAULT_THRESHOLDS: List[tuple] = [
    ("fast", 0.0, 0.1),
    ("moderate", 0.1, 1.0),
    ("slow", 1.0, 10.0),
    ("very_slow", 10.0, float("inf")),
]


def bucket_results(
    results: List[BenchmarkResult],
    branch: str,
    thresholds: Optional[List[tuple]] = None,
) -> BucketReport:
    """Group successful results for *branch* into duration buckets.

    Each threshold tuple is ``(label, min_seconds, max_seconds)``.
    Results that failed are silently excluded.
    """
    if thresholds is None:
        thresholds = _DEFAULT_THRESHOLDS

    if not thresholds:
        raise BucketerError("At least one threshold bucket must be provided.")

    buckets = [Bucket(label=t[0], min_duration=t[1], max_duration=t[2]) for t in thresholds]
    branch_results = [r for r in results if r.branch == branch and r.success]

    for result in branch_results:
        for bucket in buckets:
            if bucket.min_duration <= result.duration < bucket.max_duration:
                bucket.results.append(result)
                break

    return BucketReport(
        buckets=buckets,
        branch=branch,
        total_results=len(branch_results),
    )
