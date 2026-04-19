"""Group benchmark results by arbitrary keys for aggregated analysis."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List
from batchmark.runner import BenchmarkResult
from batchmark.comparator import ComparisonReport, SuiteComparison


@dataclass
class ResultGroup:
    key: str
    comparisons: List[SuiteComparison] = field(default_factory=list)

    @property
    def suite_names(self) -> List[str]:
        return [c.suite for c in self.comparisons]

    @property
    def regression_count(self) -> int:
        return sum(1 for c in self.comparisons if c.summary == "regression")

    @property
    def improvement_count(self) -> int:
        return sum(1 for c in self.comparisons if c.summary == "improvement")


@dataclass
class GroupReport:
    groups: Dict[str, ResultGroup] = field(default_factory=dict)

    def keys(self) -> List[str]:
        return list(self.groups.keys())

    def get(self, key: str) -> ResultGroup | None:
        return self.groups.get(key)


def group_by(report: ComparisonReport, key_fn: Callable[[SuiteComparison], str]) -> GroupReport:
    """Group comparisons in a report by a user-supplied key function."""
    groups: Dict[str, ResultGroup] = {}
    for suite_cmp in report.comparisons:
        k = key_fn(suite_cmp)
        if k not in groups:
            groups[k] = ResultGroup(key=k)
        groups[k].comparisons.append(suite_cmp)
    return GroupReport(groups=groups)


def group_by_prefix(report: ComparisonReport, sep: str = "_") -> GroupReport:
    """Group suites by the first segment of their name split by `sep`."""
    def _key(c: SuiteComparison) -> str:
        return c.suite.split(sep)[0]
    return group_by(report, _key)


def group_by_branch(report: ComparisonReport) -> GroupReport:
    """Group comparisons by the candidate branch name."""
    def _key(c: SuiteComparison) -> str:
        if c.candidate and c.candidate.branch:
            return c.candidate.branch
        return "unknown"
    return group_by(report, _key)
