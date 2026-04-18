"""Formatter for ProfileReport output."""
from __future__ import annotations
from batchmark.profiler import ProfileReport

_RESET = "\033[0m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"


def _header() -> str:
    return f"{_BOLD}{'Suite':<30} {'Branch':<20} {'Mean':>10} {'Min':>10} {'Max':>10} {'Stdev':>10}{_RESET}"


def _row(entry) -> str:
    return (
        f"{_CYAN}{entry.suite:<30}{_RESET} "
        f"{_YELLOW}{entry.branch:<20}{_RESET} "
        f"{entry.mean:>10.4f} "
        f"{entry.min:>10.4f} "
        f"{entry.max:>10.4f} "
        f"{entry.stdev:>10.4f}"
    )


def format_profile(report: ProfileReport) -> str:
    if not report.entries:
        return "No profiling data available."
    lines = [_header(), "-" * 92]
    # Group by suite for readability
    suites: dict[str, list] = {}
    for e in report.entries:
        suites.setdefault(e.suite, []).append(e)
    for suite_entries in suites.values():
        for e in suite_entries:
            lines.append(_row(e))
    return "\n".join(lines)
