"""Suite scheduling: ordering and concurrency limits for benchmark runs."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from batchmark.config import BenchmarkSuite


@dataclass
class ScheduledBatch:
    index: int
    suites: List[BenchmarkSuite]

    @property
    def size(self) -> int:
        return len(self.suites)


class SchedulerError(Exception):
    pass


def schedule(suites: List[BenchmarkSuite], max_parallel: int = 1) -> List[ScheduledBatch]:
    """Partition suites into batches respecting max_parallel."""
    if max_parallel < 1:
        raise SchedulerError(f"max_parallel must be >= 1, got {max_parallel}")

    ordered = _priority_sort(suites)
    batches: List[ScheduledBatch] = []
    for i in range(0, len(ordered), max_parallel):
        chunk = ordered[i : i + max_parallel]
        batches.append(ScheduledBatch(index=len(batches), suites=chunk))
    return batches


def _priority_sort(suites: List[BenchmarkSuite]) -> List[BenchmarkSuite]:
    """Sort suites so those with a 'priority' env var come first (lower = earlier)."""
    def _key(s: BenchmarkSuite) -> int:
        env = s.env or {}
        try:
            return int(env.get("BATCHMARK_PRIORITY", 100))
        except (ValueError, TypeError):
            return 100

    return sorted(suites, key=_key)


def suite_names(batch: ScheduledBatch) -> List[str]:
    return [s.name for s in batch.suites]
