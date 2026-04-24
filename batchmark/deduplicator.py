"""Deduplicator: remove duplicate benchmark results keeping the latest run."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from batchmark.runner import BenchmarkResult


@dataclass
class DeduplicateReport:
    """Summary of a deduplication pass over a list of results."""
    kept: List[BenchmarkResult] = field(default_factory=list)
    removed: List[BenchmarkResult] = field(default_factory=list)

    @property
    def total_removed(self) -> int:
        return len(self.removed)

    @property
    def total_kept(self) -> int:
        return len(self.kept)


def _result_key(result: BenchmarkResult) -> Tuple[str, str]:
    """Return a (suite_name, branch) key used to identify duplicates."""
    return (result.suite_name, result.branch)


def deduplicate(
    results: List[BenchmarkResult],
    *,
    keep: str = "latest",
) -> DeduplicateReport:
    """Deduplicate *results* so that only one entry per (suite, branch) is kept.

    Parameters
    ----------
    results:
        Flat list of :class:`BenchmarkResult` objects, possibly containing
        duplicates.
    keep:
        Strategy for choosing which duplicate to keep.  Currently only
        ``"latest"`` is supported (keeps the result with the highest
        ``timestamp`` value; falls back to last-seen order when timestamps
        are equal).

    Returns
    -------
    DeduplicateReport
        Contains the deduplicated ``kept`` list and the discarded ``removed``
        list.
    """
    if keep != "latest":
        raise ValueError(f"Unsupported keep strategy: {keep!r}. Use 'latest'.")

    best: Dict[Tuple[str, str], BenchmarkResult] = {}
    order: List[Tuple[str, str]] = []

    for result in results:
        key = _result_key(result)
        if key not in best:
            order.append(key)
            best[key] = result
        else:
            existing = best[key]
            existing_ts = getattr(existing, "timestamp", 0.0) or 0.0
            new_ts = getattr(result, "timestamp", 0.0) or 0.0
            if new_ts >= existing_ts:
                best[key] = result

    kept = [best[k] for k in order]
    kept_ids = {id(r) for r in kept}
    removed = [r for r in results if id(r) not in kept_ids]

    return DeduplicateReport(kept=kept, removed=removed)
