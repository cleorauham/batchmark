"""Correlate benchmark results across suites to find co-varying patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class CorrelationPair:
    suite_a: str
    suite_b: str
    coefficient: float  # -1.0 to 1.0

    @property
    def verdict(self) -> str:
        if self.coefficient >= 0.8:
            return "strong-positive"
        if self.coefficient >= 0.4:
            return "moderate-positive"
        if self.coefficient <= -0.8:
            return "strong-negative"
        if self.coefficient <= -0.4:
            return "moderate-negative"
        return "weak"


@dataclass
class CorrelationReport:
    branch: str
    pairs: List[CorrelationPair] = field(default_factory=list)

    def strong_pairs(self, threshold: float = 0.8) -> List[CorrelationPair]:
        return [p for p in self.pairs if abs(p.coefficient) >= threshold]


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _pearson(xs: List[float], ys: List[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return 0.0
    mx, my = _mean(xs), _mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denom_x = sum((x - mx) ** 2 for x in xs) ** 0.5
    denom_y = sum((y - my) ** 2 for y in ys) ** 0.5
    if denom_x == 0 or denom_y == 0:
        return 0.0
    return num / (denom_x * denom_y)


def correlate(results: list, branch: str) -> CorrelationReport:
    """Build a CorrelationReport for a given branch from a list of BenchmarkResults."""
    branch_results = [r for r in results if r.branch == branch and r.success]

    suite_durations: Dict[str, List[float]] = {}
    for r in branch_results:
        suite_durations.setdefault(r.suite, []).append(r.duration)

    suites = sorted(suite_durations.keys())
    pairs: List[CorrelationPair] = []

    for i, sa in enumerate(suites):
        for sb in suites[i + 1 :]:
            xs = suite_durations[sa]
            ys = suite_durations[sb]
            min_len = min(len(xs), len(ys))
            coeff = _pearson(xs[:min_len], ys[:min_len])
            pairs.append(CorrelationPair(suite_a=sa, suite_b=sb, coefficient=round(coeff, 4)))

    return CorrelationReport(branch=branch, pairs=pairs)
