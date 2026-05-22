"""Formatter for ReduceReport."""
from __future__ import annotations

from batchmark.reducer import ReduceReport


def _color(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _fmt_float(v: float) -> str:
    return f"{v:.4f}s"


def format_reduce_report(report: ReduceReport) -> str:
    if not report.results:
        return _color(33, "(no results to display)")

    lines = [
        _color(1, f"Reduce Report  [strategy={report.strategy}]"),
        "",
    ]

    header = f"  {'Suite':<30} {'Branch':<20} {'Duration':>12} {'N':>6}"
    lines.append(_color(4, header))

    for r in report.results:
        duration_str = _fmt_float(r.duration)
        line = f"  {r.suite:<30} {r.branch:<20} {duration_str:>12} {r.sample_size:>6}"
        lines.append(line)

    lines.append("")
    total = len(report.results)
    branches = len(report.branches)
    suites = len(report.suite_names)
    lines.append(
        _color(2, f"  {total} reduced result(s) across {suites} suite(s), {branches} branch(es).")
    )
    return "\n".join(lines)
