"""Notification hooks for benchmark run events."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List, Optional
from batchmark.comparator import ComparisonReport


@dataclass
class NotifyEvent:
    report: ComparisonReport
    regressions: int
    improvements: int
    branches: List[str]


NotifyHook = Callable[[NotifyEvent], None]


class Notifier:
    def __init__(self) -> None:
        self._hooks: List[NotifyHook] = []

    def register(self, hook: NotifyHook) -> None:
        self._hooks.append(hook)

    def notify(self, event: NotifyEvent) -> None:
        for hook in self._hooks:
            hook(event)


def build_event(report: ComparisonReport) -> NotifyEvent:
    reg = sum(1 for sc in report.comparisons if sc.summary() == "regression")
    imp = sum(1 for sc in report.comparisons if sc.summary() == "improvement")
    return NotifyEvent(
        report=report,
        regressions=reg,
        improvements=imp,
        branches=report.branches,
    )


def stdout_hook(event: NotifyEvent) -> None:
    print(
        f"[batchmark] run complete: {event.regressions} regression(s), "
        f"{event.improvements} improvement(s) across branches {event.branches}"
    )


def threshold_hook(max_regressions: int = 0) -> NotifyHook:
    def _hook(event: NotifyEvent) -> None:
        if event.regressions > max_regressions:
            raise RuntimeError(
                f"Regression threshold exceeded: {event.regressions} > {max_regressions}"
            )
    return _hook
