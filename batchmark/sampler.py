"""Sampler: randomly sample a subset of benchmark results for analysis."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.runner import BenchmarkResult


class SamplerError(Exception):
    pass


@dataclass
class SampleReport:
    branch: str
    suite: str
    results: List[BenchmarkResult] = field(default_factory=list)
    total_available: int = 0

    @property
    def sample_size(self) -> int:
        return len(self.results)

    @property
    def mean_duration(self) -> Optional[float]:
        durations = [r.duration for r in self.results if r.success and r.duration is not None]
        if not durations:
            return None
        return sum(durations) / len(durations)


def sample(
    results: List[BenchmarkResult],
    n: int,
    *,
    seed: Optional[int] = None,
) -> List[SampleReport]:
    """Sample up to *n* results per (branch, suite) group.

    Args:
        results: flat list of BenchmarkResult objects.
        n: maximum number of results to keep per group.
        seed: optional random seed for reproducibility.

    Returns:
        List of SampleReport, one per (branch, suite) pair.
    """
    if n <= 0:
        raise SamplerError(f"Sample size must be positive, got {n}")

    rng = random.Random(seed)

    groups: dict[tuple[str, str], List[BenchmarkResult]] = {}
    for r in results:
        key = (r.branch, r.suite)
        groups.setdefault(key, []).append(r)

    reports: List[SampleReport] = []
    for (branch, suite), group in sorted(groups.items()):
        total = len(group)
        chosen = rng.sample(group, min(n, total))
        reports.append(
            SampleReport(
                branch=branch,
                suite=suite,
                results=chosen,
                total_available=total,
            )
        )
    return reports
