"""Format NotifyEvent summaries for display."""
from __future__ import annotations
from batchmark.notifier import NotifyEvent

_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_BOLD = "\033[1m"


def _color(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}"


def format_event_summary(event: NotifyEvent) -> str:
    lines = []
    branches_str = " vs ".join(event.branches)
    lines.append(f"{_BOLD}Benchmark run:{_RESET} {branches_str}")

    reg_str = str(event.regressions)
    imp_str = str(event.improvements)

    if event.regressions > 0:
        reg_str = _color(reg_str, _RED)
    if event.improvements > 0:
        imp_str = _color(imp_str, _GREEN)

    lines.append(f"  Regressions : {reg_str}")
    lines.append(f"  Improvements: {imp_str}")

    total = len(event.report.comparisons)
    neutral = total - event.regressions - event.improvements
    lines.append(f"  Neutral     : {neutral}")
    lines.append(f"  Total suites: {total}")
    return "\n".join(lines)
