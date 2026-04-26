"""Dispatcher: route benchmark results to multiple registered sinks.

A sink is any callable that accepts a list of BenchmarkResult objects.
This allows results to be fanned out to the cache, archiver, notifier,
exporter, etc. in a single pass without coupling the runner to each consumer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from batchmark.runner import BenchmarkResult


# Type alias for a sink callable.
Sink = Callable[[List[BenchmarkResult]], None]


@dataclass
class DispatchError(Exception):
    """Raised when one or more sinks fail during dispatch."""

    failures: List[tuple[str, Exception]]

    def __str__(self) -> str:  # pragma: no cover
        lines = [f"Dispatch failed for {len(self.failures)} sink(s):"]
        for name, exc in self.failures:
            lines.append(f"  [{name}] {exc}")
        return "\n".join(lines)


@dataclass
class SinkRecord:
    """Metadata about a registered sink."""

    name: str
    sink: Sink
    enabled: bool = True


@dataclass
class DispatchReport:
    """Summary of a dispatch run."""

    total_results: int
    sinks_called: List[str] = field(default_factory=list)
    sinks_skipped: List[str] = field(default_factory=list)
    sinks_failed: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """True when no sinks failed."""
        return len(self.sinks_failed) == 0


class Dispatcher:
    """Fan-out dispatcher that forwards results to all registered sinks."""

    def __init__(self, raise_on_error: bool = False) -> None:
        self._sinks: List[SinkRecord] = []
        self._raise_on_error = raise_on_error

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, name: str, sink: Sink, *, enabled: bool = True) -> None:
        """Register a new sink under *name*."""
        if any(s.name == name for s in self._sinks):
            raise ValueError(f"Sink '{name}' is already registered.")
        self._sinks.append(SinkRecord(name=name, sink=sink, enabled=enabled))

    def enable(self, name: str) -> None:
        """Enable a previously disabled sink."""
        self._get(name).enabled = True

    def disable(self, name: str) -> None:
        """Disable a sink without removing it."""
        self._get(name).enabled = False

    def sink_names(self) -> List[str]:
        """Return names of all registered sinks."""
        return [s.name for s in self._sinks]

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def dispatch(
        self,
        results: List[BenchmarkResult],
        *,
        only: Optional[List[str]] = None,
    ) -> DispatchReport:
        """Send *results* to every enabled sink.

        Parameters
        ----------
        results:
            The benchmark results to forward.
        only:
            If provided, only sinks whose names appear in this list are called.
        """
        report = DispatchReport(total_results=len(results))
        failures: list[tuple[str, Exception]] = []

        for record in self._sinks:
            if only is not None and record.name not in only:
                report.sinks_skipped.append(record.name)
                continue
            if not record.enabled:
                report.sinks_skipped.append(record.name)
                continue
            try:
                record.sink(results)
                report.sinks_called.append(record.name)
            except Exception as exc:  # noqa: BLE001
                report.sinks_failed.append(record.name)
                failures.append((record.name, exc))

        if failures and self._raise_on_error:
            raise DispatchError(failures=failures)

        return report

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, name: str) -> SinkRecord:
        for record in self._sinks:
            if record.name == name:
                return record
        raise KeyError(f"No sink named '{name}' is registered.")
