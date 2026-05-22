"""Reduce multiple benchmark results into a single representative result per suite/branch."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from batchmark.runner import BenchmarkResult


class ReducerError(Exception):
    pass


_STRATEGIES: Dict[str, Callable[[List[float]], float]] = {
    "mean": lambda vs: sum(vs) / len(vs),
    "median": lambda vs: sorted(vs)[len(vs) // 2],
    "min": min,
    "max": max,
}


@dataclass
class ReducedResult:
    suite: str
    branch: str
    duration: float
    strategy: str
    sample_size: int

    @property
    def success(self) -> bool:
        return True


@dataclass
class ReduceReport:
    strategy: str
    results: List[ReducedResult] = field(default_factory=list)

    def by_branch(self, branch: str) -> List[ReducedResult]:
        return [r for r in self.results if r.branch == branch]

    def by_suite(self, suite: str) -> List[ReducedResult]:
        return [r for r in self.results if r.suite == suite]

    @property
    def branches(self) -> List[str]:
        seen: List[str] = []
        for r in self.results:
            if r.branch not in seen:
                seen.append(r.branch)
        return seen

    @property
    def suite_names(self) -> List[str]:
        seen: List[str] = []
        for r in self.results:
            if r.suite not in seen:
                seen.append(r.suite)
        return seen


def reduce(
    results: List[BenchmarkResult],
    strategy: str = "mean",
) -> ReduceReport:
    """Reduce a flat list of results by (suite, branch) using the given strategy."""
    if strategy not in _STRATEGIES:
        raise ReducerError(
            f"Unknown strategy '{strategy}'. Choose from: {', '.join(_STRATEGIES)}"
        )

    fn = _STRATEGIES[strategy]
    groups: Dict[tuple, List[float]] = {}

    for r in results:
        if not r.success:
            continue
        key = (r.suite, r.branch)
        groups.setdefault(key, []).append(r.duration)

    reduced: List[ReducedResult] = [
        ReducedResult(
            suite=suite,
            branch=branch,
            duration=fn(durations),
            strategy=strategy,
            sample_size=len(durations),
        )
        for (suite, branch), durations in groups.items()
    ]

    return ReduceReport(strategy=strategy, results=reduced)
