"""Segment benchmark results into time-based windows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Segment:
    label: str
    results: list = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.results)

    @property
    def suite_names(self) -> List[str]:
        return sorted({r.suite for r in self.results})

    @property
    def branch_names(self) -> List[str]:
        return sorted({r.branch for r in self.results})


@dataclass
class SegmentReport:
    segments: List[Segment] = field(default_factory=list)

    @property
    def total_segments(self) -> int:
        return len(self.segments)

    @property
    def total_results(self) -> int:
        return sum(len(s) for s in self.segments)

    def by_label(self, label: str) -> Segment | None:
        for seg in self.segments:
            if seg.label == label:
                return seg
        return None


class SegmentError(Exception):
    pass


def segment_by_count(results: list, size: int) -> SegmentReport:
    """Split results into fixed-size segments."""
    if size <= 0:
        raise SegmentError(f"Segment size must be positive, got {size}")
    if not results:
        return SegmentReport()
    segments = []
    for i in range(0, len(results), size):
        chunk = results[i : i + size]
        label = f"seg-{i // size + 1}"
        segments.append(Segment(label=label, results=chunk))
    return SegmentReport(segments=segments)


def segment_by_branch(results: list) -> SegmentReport:
    """Group results into one segment per branch."""
    if not results:
        return SegmentReport()
    buckets: Dict[str, list] = {}
    for r in results:
        buckets.setdefault(r.branch, []).append(r)
    segments = [
        Segment(label=branch, results=items)
        for branch, items in sorted(buckets.items())
    ]
    return SegmentReport(segments=segments)
