"""Compare benchmark results across branches."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.runner import BenchmarkResult


@dataclass
class SuiteComparison:
    suite_name: str
    baseline_branch: str
    compare_branch: str
    baseline_duration: float
    compare_duration: float
    delta_pct: float
    improved: bool

    @property
    def summary(self) -> str:
        direction = "improved" if self.improved else "regressed"
        return (
            f"{self.suite_name}: {direction} by {abs(self.delta_pct):.2f}% "
            f"({self.baseline_branch}: {self.baseline_duration:.3f}s → "
            f"{self.compare_branch}: {self.compare_duration:.3f}s)"
        )


@dataclass
class ComparisonReport:
    baseline_branch: str
    compare_branch: str
    comparisons: List[SuiteComparison] = field(default_factory=list)

    @property
    def regressions(self) -> List[SuiteComparison]:
        return [c for c in self.comparisons if not c.improved]

    @property
    def improvements(self) -> List[SuiteComparison]:
        return [c for c in self.comparisons if c.improved]


def compare_results(
    baseline: List[BenchmarkResult],
    compare: List[BenchmarkResult],
    baseline_branch: str,
    compare_branch: str,
) -> ComparisonReport:
    """Build a ComparisonReport from two lists of BenchmarkResult."""
    baseline_map: Dict[str, BenchmarkResult] = {r.suite_name: r for r in baseline}
    compare_map: Dict[str, BenchmarkResult] = {r.suite_name: r for r in compare}

    report = ComparisonReport(
        baseline_branch=baseline_branch,
        compare_branch=compare_branch,
    )

    for name, base_result in baseline_map.items():
        cmp_result = compare_map.get(name)
        if cmp_result is None or not base_result.success or not cmp_result.success:
            continue

        base_dur = base_result.duration_seconds
        cmp_dur = cmp_result.duration_seconds

        if base_dur == 0:
            continue

        delta_pct = ((cmp_dur - base_dur) / base_dur) * 100
        improved = delta_pct < 0

        report.comparisons.append(
            SuiteComparison(
                suite_name=name,
                baseline_branch=baseline_branch,
                compare_branch=compare_branch,
                baseline_duration=base_dur,
                compare_duration=cmp_dur,
                delta_pct=delta_pct,
                improved=improved,
            )
        )

    return report
