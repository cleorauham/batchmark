"""Track consecutive regression/improvement streaks across benchmark runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from batchmark.comparator import SuiteComparison
from batchmark.comparator import ComparisonReport


@dataclass
class StreakEntry:
    suite: str
    branch: str
    kind: str          # "regression" | "improvement" | "unchanged"
    length: int

    def __str__(self) -> str:
        return f"{self.suite}@{self.branch}: {self.kind} x{self.length}"


@dataclass
class StreakReport:
    entries: List[StreakEntry] = field(default_factory=list)

    def regressions(self) -> List[StreakEntry]:
        return [e for e in self.entries if e.kind == "regression"]

    def improvements(self) -> List[StreakEntry]:
        return [e for e in self.entries if e.kind == "improvement"]

    def longest(self) -> StreakEntry | None:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.length)


def _classify(cmp: SuiteComparison) -> str:
    if cmp.baseline_mean is None or cmp.candidate_mean is None:
        return "unchanged"
    delta = cmp.candidate_mean - cmp.baseline_mean
    if delta > 0:
        return "regression"
    if delta < 0:
        return "improvement"
    return "unchanged"


def build_streaks(reports: List[ComparisonReport]) -> StreakReport:
    """Given an ordered list of ComparisonReports (oldest first),
    compute the current consecutive streak for each (suite, branch) pair."""
    if not reports:
        return StreakReport()

    # state[(suite, branch)] = (current_kind, current_length)
    state: Dict[tuple, tuple] = {}

    for report in reports:
        for cmp in report.comparisons:
            key = (cmp.suite, report.candidate_branch)
            kind = _classify(cmp)
            if key in state:
                prev_kind, prev_len = state[key]
                if kind == prev_kind:
                    state[key] = (kind, prev_len + 1)
                else:
                    state[key] = (kind, 1)
            else:
                state[key] = (kind, 1)

    entries = [
        StreakEntry(suite=suite, branch=branch, kind=kind, length=length)
        for (suite, branch), (kind, length) in sorted(state.items())
    ]
    return StreakReport(entries=entries)
