"""Trend analysis across multiple baseline snapshots."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from batchmark.baseline import load_baseline, list_baselines, BaselineError


@dataclass
class TrendPoint:
    name: str
    mean_duration: float


@dataclass
class SuiteTrend:
    suite: str
    points: List[TrendPoint] = field(default_factory=list)

    @property
    def slope(self) -> Optional[float]:
        """Simple linear slope over points (duration per step)."""
        n = len(self.points)
        if n < 2:
            return None
        xs = list(range(n))
        ys = [p.mean_duration for p in self.points]
        x_mean = sum(xs) / n
        y_mean = sum(ys) / n
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        den = sum((x - x_mean) ** 2 for x in xs)
        return num / den if den else 0.0

    @property
    def verdict(self) -> str:
        s = self.slope
        if s is None:
            return "insufficient data"
        if s > 0.05:
            return "degrading"
        if s < -0.05:
            return "improving"
        return "stable"


@dataclass
class TrendReport:
    baselines: List[str]
    trends: List[SuiteTrend]


def build_trend(baseline_dir: str, branch: str) -> TrendReport:
    names = list_baselines(baseline_dir)
    if not names:
        return TrendReport(baselines=[], trends=[])

    suite_data: Dict[str, SuiteTrend] = {}
    used: List[str] = []

    for name in names:
        try:
            results = load_baseline(baseline_dir, name)
        except BaselineError:
            continue
        branch_results = [r for r in results if r.branch == branch and r.success]
        if not branch_results:
            continue
        used.append(name)
        by_suite: Dict[str, list] = {}
        for r in branch_results:
            by_suite.setdefault(r.suite, []).append(r.duration)
        for suite, durations in by_suite.items():
            mean_dur = sum(durations) / len(durations)
            if suite not in suite_data:
                suite_data[suite] = SuiteTrend(suite=suite)
            suite_data[suite].points.append(TrendPoint(name=name, mean_duration=mean_dur))

    return TrendReport(baselines=used, trends=list(suite_data.values()))
