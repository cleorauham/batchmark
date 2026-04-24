"""Validates benchmark results against configurable rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.runner import BenchmarkResult
from batchmark.comparator import ComparisonReport


@dataclass
class ValidationRule:
    suite: str
    max_duration: Optional[float] = None   # seconds
    max_regression_pct: Optional[float] = None  # e.g. 10.0 means 10%


@dataclass
class ValidationViolation:
    suite: str
    branch: str
    rule: str
    detail: str

    def __str__(self) -> str:
        return f"[{self.suite}@{self.branch}] {self.rule}: {self.detail}"


@dataclass
class ValidationReport:
    violations: List[ValidationViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    @property
    def failed(self) -> bool:
        return not self.passed


def validate_results(
    results: List[BenchmarkResult],
    rules: List[ValidationRule],
) -> ValidationReport:
    """Check raw results against max_duration rules."""
    rule_map = {r.suite: r for r in rules}
    violations: List[ValidationViolation] = []

    for res in results:
        if not res.success:
            continue
        rule = rule_map.get(res.suite)
        if rule is None:
            continue
        if rule.max_duration is not None and res.duration > rule.max_duration:
            violations.append(ValidationViolation(
                suite=res.suite,
                branch=res.branch,
                rule="max_duration",
                detail=f"{res.duration:.3f}s exceeds limit {rule.max_duration:.3f}s",
            ))

    return ValidationReport(violations=violations)


def validate_report(
    report: ComparisonReport,
    rules: List[ValidationRule],
) -> ValidationReport:
    """Check comparison report against max_regression_pct rules."""
    rule_map = {r.suite: r for r in rules}
    violations: List[ValidationViolation] = []

    for cmp in report.comparisons:
        rule = rule_map.get(cmp.suite)
        if rule is None or rule.max_regression_pct is None:
            continue
        if cmp.delta_pct is not None and cmp.delta_pct > rule.max_regression_pct:
            violations.append(ValidationViolation(
                suite=cmp.suite,
                branch="candidate",
                rule="max_regression_pct",
                detail=f"{cmp.delta_pct:.1f}% regression exceeds limit {rule.max_regression_pct:.1f}%",
            ))

    return ValidationReport(violations=violations)
