"""Normalizer: scale benchmark durations relative to a reference suite or branch."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.runner import BenchmarkResult


class NormalizerError(Exception):
    pass


@dataclass
class NormalizedResult:
    suite: str
    branch: str
    raw_duration: float
    normalized_duration: float
    reference_duration: float

    @property
    def ratio(self) -> float:
        return self.normalized_duration


@dataclass
class NormalizeReport:
    reference_branch: str
    results: List[NormalizedResult] = field(default_factory=list)

    def by_branch(self, branch: str) -> List[NormalizedResult]:
        return [r for r in self.results if r.branch == branch]

    def by_suite(self, suite: str) -> List[NormalizedResult]:
        return [r for r in self.results if r.suite == suite]


def normalize(
    results: List[BenchmarkResult],
    reference_branch: str,
) -> NormalizeReport:
    """Normalize all result durations relative to the mean duration of the
    reference branch for each suite.  A ratio of 1.0 means equal to reference."""
    if not results:
        return NormalizeReport(reference_branch=reference_branch)

    # Build reference map: suite -> mean duration on reference branch
    ref_durations: Dict[str, List[float]] = {}
    for r in results:
        if r.branch == reference_branch and r.success and r.duration is not None:
            ref_durations.setdefault(r.suite, []).append(r.duration)

    if not ref_durations:
        raise NormalizerError(
            f"No successful results found for reference branch '{reference_branch}'"
        )

    ref_means: Dict[str, float] = {
        suite: sum(durations) / len(durations)
        for suite, durations in ref_durations.items()
    }

    normalized: List[NormalizedResult] = []
    for r in results:
        if not r.success or r.duration is None:
            continue
        ref = ref_means.get(r.suite)
        if ref is None or ref == 0.0:
            continue
        normalized.append(
            NormalizedResult(
                suite=r.suite,
                branch=r.branch,
                raw_duration=r.duration,
                normalized_duration=r.duration / ref,
                reference_duration=ref,
            )
        )

    return NormalizeReport(reference_branch=reference_branch, results=normalized)
