"""Heatmap: build a 2-D duration grid (suite × branch) for visualisation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.runner import BenchmarkResult


@dataclass
class HeatmapCell:
    suite: str
    branch: str
    mean_duration: float
    sample_count: int


@dataclass
class HeatmapReport:
    suites: List[str]
    branches: List[str]
    # cells[suite][branch] = HeatmapCell | None
    cells: Dict[str, Dict[str, Optional[HeatmapCell]]] = field(default_factory=dict)

    def get(self, suite: str, branch: str) -> Optional[HeatmapCell]:
        return self.cells.get(suite, {}).get(branch)


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_heatmap(results: List[BenchmarkResult]) -> HeatmapReport:
    """Aggregate *successful* results into a HeatmapReport."""
    # Collect raw durations keyed by (suite, branch)
    raw: Dict[tuple, List[float]] = {}
    suite_set: set = set()
    branch_set: set = set()

    for r in results:
        if not r.success:
            continue
        key = (r.suite, r.branch)
        raw.setdefault(key, []).append(r.duration)
        suite_set.add(r.suite)
        branch_set.add(r.branch)

    suites = sorted(suite_set)
    branches = sorted(branch_set)

    cells: Dict[str, Dict[str, Optional[HeatmapCell]]] = {
        s: {b: None for b in branches} for s in suites
    }

    for (suite, branch), durations in raw.items():
        cells[suite][branch] = HeatmapCell(
            suite=suite,
            branch=branch,
            mean_duration=_mean(durations),
            sample_count=len(durations),
        )

    return HeatmapReport(suites=suites, branches=branches, cells=cells)
