"""Replay stored benchmark results as if they were freshly run."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.runner import BenchmarkResult
from batchmark.cache import load_result, CacheError
from batchmark.baseline import load_baseline, BaselineError


class ReplayError(Exception):
    pass


@dataclass
class ReplaySource:
    kind: str          # 'cache' | 'baseline'
    name: str          # branch name or baseline label
    suite_names: List[str] = field(default_factory=list)


@dataclass
class ReplayReport:
    source: ReplaySource
    results: List[BenchmarkResult] = field(default_factory=list)

    @property
    def failed(self) -> List[BenchmarkResult]:
        return [r for r in self.results if not r.success]

    @property
    def succeeded(self) -> List[BenchmarkResult]:
        return [r for r in self.results if r.success]


def replay_from_baseline(label: str, store_dir: str) -> ReplayReport:
    """Load all results stored under a baseline label."""
    try:
        results = load_baseline(label, store_dir)
    except BaselineError as exc:
        raise ReplayError(str(exc)) from exc
    suite_names = list({r.suite for r in results})
    source = ReplaySource(kind="baseline", name=label, suite_names=suite_names)
    return ReplayReport(source=source, results=results)


def replay_from_cache(
    branch: str, suite_names: List[str], store_dir: str
) -> ReplayReport:
    """Load cached results for a branch + list of suites."""
    results: List[BenchmarkResult] = []
    missing: List[str] = []
    for suite in suite_names:
        result = load_result(branch, suite, store_dir)
        if result is None:
            missing.append(suite)
        else:
            results.append(result)
    if missing:
        raise ReplayError(
            f"No cached results for branch '{branch}', suites: {missing}"
        )
    source = ReplaySource(kind="cache", name=branch, suite_names=suite_names)
    return ReplayReport(source=source, results=results)
