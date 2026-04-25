"""Classify benchmark results into performance tiers based on duration thresholds."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


TIERS = ("fast", "moderate", "slow", "critical")


@dataclass
class ClassifiedResult:
    suite: str
    branch: str
    duration: float
    tier: str


@dataclass
class TierBucket:
    label: str
    results: List[ClassifiedResult] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.results)

    def suite_names(self) -> List[str]:
        return sorted({r.suite for r in self.results})


@dataclass
class ClassifyReport:
    thresholds: Dict[str, float]
    buckets: Dict[str, TierBucket]

    def by_tier(self, tier: str) -> Optional[TierBucket]:
        return self.buckets.get(tier)

    def total(self) -> int:
        return sum(len(b) for b in self.buckets.values())


class ClassifierError(Exception):
    pass


def _assign_tier(duration: float, thresholds: Dict[str, float]) -> str:
    """Return the tier label for a given duration."""
    if duration <= thresholds.get("fast", 0.5):
        return "fast"
    if duration <= thresholds.get("moderate", 2.0):
        return "moderate"
    if duration <= thresholds.get("slow", 10.0):
        return "slow"
    return "critical"


def classify(results, thresholds: Optional[Dict[str, float]] = None) -> ClassifyReport:
    """Classify a list of BenchmarkResult objects into performance tiers."""
    thresholds = thresholds or {"fast": 0.5, "moderate": 2.0, "slow": 10.0}
    for key in ("fast", "moderate", "slow"):
        if key not in thresholds:
            raise ClassifierError(f"Missing threshold for tier: {key!r}")

    buckets: Dict[str, TierBucket] = {t: TierBucket(label=t) for t in TIERS}

    for r in results:
        if not getattr(r, "success", False):
            continue
        tier = _assign_tier(r.duration, thresholds)
        buckets[tier].results.append(
            ClassifiedResult(
                suite=r.suite,
                branch=r.branch,
                duration=r.duration,
                tier=tier,
            )
        )

    return ClassifyReport(thresholds=thresholds, buckets=buckets)
