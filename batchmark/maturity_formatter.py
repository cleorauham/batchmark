"""Formatter for MaturityReport."""
from __future__ import annotations

from batchmark.maturity import MaturityReport, SuiteMaturity

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_BOLD = "\033[1m"


def _color(verdict: str) -> str:
    return {"stable": _GREEN, "unstable": _YELLOW, "flaky": _RED}.get(verdict, _RESET)


def _row(e: SuiteMaturity) -> str:
    col = _color(e.verdict)
    verdict_str = f"{col}{e.verdict:<10}{_RESET}"
    return (
        f"  {e.suite:<30} {e.branch:<20} "
        f"runs={e.run_count:<4} "
        f"ok={e.success_rate * 100:5.1f}%  "
        f"cv={e.cv:.3f}  "
        f"{verdict_str}"
    )


def format_maturity_report(report: MaturityReport) -> str:
    if not report.entries:
        return "  (no maturity data)"

    lines = [
        f"{_BOLD}Maturity Report{_RESET}",
        f"  {'Suite':<30} {'Branch':<20} {'Runs':<9} {'OK%':<9} {'CV':<8} Verdict",
        "  " + "-" * 80,
    ]
    for e in sorted(report.entries, key=lambda x: (x.branch, x.suite)):
        lines.append(_row(e))

    stable_n = len(report.stable())
    unstable_n = len(report.unstable())
    flaky_n = len(report.flaky())
    lines.append("  " + "-" * 80)
    lines.append(
        f"  Summary: "
        f"{_GREEN}stable={stable_n}{_RESET}  "
        f"{_YELLOW}unstable={unstable_n}{_RESET}  "
        f"{_RED}flaky={flaky_n}{_RESET}"
    )
    return "\n".join(lines)
