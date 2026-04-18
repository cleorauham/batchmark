"""Per-suite timing profiler that tracks run durations across branches."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import statistics


@dataclass
class ProfileEntry:
    suite: str
    branch: str
    durations: List[float] = field(default_factory=list)

    @property
    def mean(self) -> float:
        return statistics.mean(self.durations) if self.durations else 0.0

    @property
    def stdev(self) -> float:
        return statistics.stdev(self.durations) if len(self.durations) > 1 else 0.0

    @property
    def min(self) -> float:
        return min(self.durations) if self.durations else 0.0

    @property
    def max(self) -> float:
        return max(self.durations) if self.durations else 0.0


@dataclass
class ProfileReport:
    entries: List[ProfileEntry] = field(default_factory=list)

    def get(self, suite: str, branch: str) -> ProfileEntry | None:
        for e in self.entries:
            if e.suite == suite and e.branch == branch:
                return e
        return None


def build_profile(results: list) -> ProfileReport:
    """Build a ProfileReport from a list of BenchmarkResult objects."""
    index: Dict[tuple, ProfileEntry] = {}
    for r in results:
        if not r.success:
            continue
        key = (r.suite, r.branch)
        if key not in index:
            index[key] = ProfileEntry(suite=r.suite, branch=r.branch)
        index[key].durations.append(r.duration)
    return ProfileReport(entries=list(index.values()))
