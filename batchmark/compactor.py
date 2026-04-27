"""Compactor: merge and deduplicate results across multiple archives into a single compacted store."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class CompactEntry:
    suite: str
    branch: str
    duration: float
    passed: bool
    timestamp: str


@dataclass
class CompactReport:
    entries: List[CompactEntry] = field(default_factory=list)
    sources_merged: int = 0
    total_removed: int = 0

    @property
    def total_kept(self) -> int:
        return len(self.entries)

    def by_branch(self) -> Dict[str, List[CompactEntry]]:
        out: Dict[str, List[CompactEntry]] = {}
        for e in self.entries:
            out.setdefault(e.branch, []).append(e)
        return out

    def by_suite(self) -> Dict[str, List[CompactEntry]]:
        out: Dict[str, List[CompactEntry]] = {}
        for e in self.entries:
            out.setdefault(e.suite, []).append(e)
        return out


class CompactError(Exception):
    pass


def _entry_key(e: CompactEntry) -> Tuple[str, str]:
    return (e.suite, e.branch)


def compact(result_lists: List[List[CompactEntry]]) -> CompactReport:
    """Merge multiple lists of CompactEntry, keeping only the latest per (suite, branch)."""
    if not result_lists:
        raise CompactError("No result lists provided to compact.")

    seen: Dict[Tuple[str, str], CompactEntry] = {}
    total_in = 0

    for lst in result_lists:
        for entry in lst:
            total_in += 1
            key = _entry_key(entry)
            existing = seen.get(key)
            if existing is None or entry.timestamp >= existing.timestamp:
                seen[key] = entry

    kept = list(seen.values())
    kept.sort(key=lambda e: (e.branch, e.suite))

    return CompactReport(
        entries=kept,
        sources_merged=len(result_lists),
        total_removed=total_in - len(kept),
    )
