"""Execution trace recorder — captures per-suite timing spans across branches."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time


@dataclass
class TraceSpan:
    suite: str
    branch: str
    start: float
    end: float
    success: bool

    @property
    def duration(self) -> float:
        return self.end - self.start

    def __str__(self) -> str:
        status = "ok" if self.success else "fail"
        return f"[{self.branch}] {self.suite} {self.duration:.3f}s ({status})"


@dataclass
class TraceReport:
    spans: List[TraceSpan] = field(default_factory=list)

    def by_branch(self) -> Dict[str, List[TraceSpan]]:
        out: Dict[str, List[TraceSpan]] = {}
        for span in self.spans:
            out.setdefault(span.branch, []).append(span)
        return out

    def by_suite(self) -> Dict[str, List[TraceSpan]]:
        out: Dict[str, List[TraceSpan]] = {}
        for span in self.spans:
            out.setdefault(span.suite, []).append(span)
        return out

    def total_duration(self) -> float:
        return sum(s.duration for s in self.spans)

    def failed_spans(self) -> List[TraceSpan]:
        return [s for s in self.spans if not s.success]

    def has_failures(self) -> bool:
        return any(not s.success for s in self.spans)


class Tracer:
    """Context-manager-friendly tracer that records spans."""

    def __init__(self) -> None:
        self._report = TraceReport()
        self._active: Optional[dict] = None

    def start(self, suite: str, branch: str) -> None:
        self._active = {"suite": suite, "branch": branch, "start": time.monotonic()}

    def finish(self, success: bool = True) -> None:
        if self._active is None:
            raise RuntimeError("finish() called without a matching start()")
        end = time.monotonic()
        span = TraceSpan(
            suite=self._active["suite"],
            branch=self._active["branch"],
            start=self._active["start"],
            end=end,
            success=success,
        )
        self._report.spans.append(span)
        self._active = None

    @property
    def report(self) -> TraceReport:
        return self._report


def build_trace(results: list) -> TraceReport:
    """Build a TraceReport from a list of BenchmarkResult-like objects."""
    report = TraceReport()
    for r in results:
        span = TraceSpan(
            suite=r.suite,
            branch=r.branch,
            start=0.0,
            end=r.duration if r.success else 0.0,
            success=r.success,
        )
        report.spans.append(span)
    return report
