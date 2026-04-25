"""Retry logic for flaky benchmark runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.runner import BenchmarkResult


class RetryError(Exception):
    """Raised when retry configuration is invalid."""


@dataclass
class RetryRecord:
    suite: str
    branch: str
    attempts: int
    final: BenchmarkResult
    all_durations: List[float] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return self.final.success

    @property
    def mean_duration(self) -> Optional[float]:
        if not self.all_durations:
            return None
        return sum(self.all_durations) / len(self.all_durations)


@dataclass
class RetryReport:
    records: List[RetryRecord] = field(default_factory=list)

    @property
    def total_retried(self) -> int:
        return sum(1 for r in self.records if r.attempts > 1)

    @property
    def total_failed(self) -> int:
        return sum(1 for r in self.records if not r.succeeded)

    @property
    def total_succeeded(self) -> int:
        return sum(1 for r in self.records if r.succeeded)


def retry_run(
    run_fn,
    suite: str,
    branch: str,
    max_attempts: int = 3,
    retry_on_failure: bool = True,
) -> RetryRecord:
    """Run a benchmark with retry logic.

    Args:
        run_fn: Callable[[], BenchmarkResult]
        suite: Suite name (for record keeping).
        branch: Branch name (for record keeping).
        max_attempts: Maximum number of attempts (must be >= 1).
        retry_on_failure: If False, do not retry on failure.

    Returns:
        RetryRecord with the final result and attempt metadata.
    """
    if max_attempts < 1:
        raise RetryError(f"max_attempts must be >= 1, got {max_attempts}")

    durations: List[float] = []
    result: Optional[BenchmarkResult] = None

    for attempt in range(1, max_attempts + 1):
        result = run_fn()
        if result.duration_s is not None:
            durations.append(result.duration_s)
        if result.success or not retry_on_failure:
            break

    return RetryRecord(
        suite=suite,
        branch=branch,
        attempts=attempt,
        final=result,
        all_durations=durations,
    )
