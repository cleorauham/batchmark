"""Load balancer: distribute benchmark suites across workers evenly."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from batchmark.config import BenchmarkSuite


class BalancerError(Exception):
    pass


@dataclass
class WorkerSlice:
    worker_id: int
    suites: List[BenchmarkSuite] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.suites)

    def suite_names(self) -> List[str]:
        return [s.name for s in self.suites]

    def estimated_weight(self) -> float:
        """Sum of suite timeouts as a proxy for expected work."""
        return sum(getattr(s, "timeout", 60) for s in self.suites)


@dataclass
class BalanceReport:
    workers: List[WorkerSlice]

    @property
    def total_suites(self) -> int:
        return sum(len(w) for w in self.workers)

    def by_worker(self, worker_id: int) -> WorkerSlice:
        for w in self.workers:
            if w.worker_id == worker_id:
                return w
        raise KeyError(f"worker {worker_id} not found")

    def most_loaded(self) -> WorkerSlice:
        return max(self.workers, key=lambda w: w.estimated_weight())

    def least_loaded(self) -> WorkerSlice:
        return min(self.workers, key=lambda w: w.estimated_weight())


def balance(
    suites: Sequence[BenchmarkSuite],
    num_workers: int,
    *,
    strategy: str = "round_robin",
) -> BalanceReport:
    """Distribute *suites* across *num_workers* workers.

    Strategies
    ----------
    round_robin  – assign suites in rotation (default)
    weighted     – greedy least-loaded assignment based on timeout weight
    """
    if num_workers < 1:
        raise BalancerError("num_workers must be >= 1")
    if not suites:
        return BalanceReport(workers=[WorkerSlice(i) for i in range(num_workers)])

    workers = [WorkerSlice(i) for i in range(num_workers)]

    if strategy == "round_robin":
        for idx, suite in enumerate(suites):
            workers[idx % num_workers].suites.append(suite)
    elif strategy == "weighted":
        for suite in sorted(suites, key=lambda s: getattr(s, "timeout", 60), reverse=True):
            lightest = min(workers, key=lambda w: w.estimated_weight())
            lightest.suites.append(suite)
    else:
        raise BalancerError(f"unknown strategy: {strategy!r}")

    return BalanceReport(workers=workers)
