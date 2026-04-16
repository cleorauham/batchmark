"""Format comparison reports for terminal output."""
from __future__ import annotations

from typing import List

from batchmark.comparator import ComparisonReport, SuiteComparison

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _color(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{RESET}" if use_color else text


def format_comparison_row(c: SuiteComparison, use_color: bool = True) -> str:
    sign = "-" if c.improved else "+"
    color = GREEN if c.improved else RED
    delta_str = _color(f"{sign}{abs(c.delta_pct):.2f}%", color, use_color)
    return (
        f"  {c.suite_name:<30} "
        f"{c.baseline_duration:>8.3f}s  "
        f"{c.compare_duration:>8.3f}s  "
        f"{delta_str:>12}"
    )


def format_report(report: ComparisonReport, use_color: bool = True) -> str:
    lines: List[str] = []

    header = _color(
        f"Benchmark comparison: {report.baseline_branch} → {report.compare_branch}",
        BOLD,
        use_color,
    )
    lines.append(header)
    lines.append("-" * 70)

    col_header = (
        f"  {'Suite':<30} {'Baseline':>9}  {'Compare':>9}  {'Delta':>12}"
    )
    lines.append(_color(col_header, BOLD, use_color))
    lines.append("-" * 70)

    if not report.comparisons:
        lines.append("  No comparable results found.")
    (report.comparisons, key=lambda x: x.delta_pct):
            lines.append(format_comparison_row(c, use_color))

    lines.append("-" * 70)
    n_imp = len(report.improvements)
    n_reg = len(report.regressions)
    summary = f"  {n_imp} improvement(s), {n_reg} regression(s)"
    lines.append(_color(summary, YELLOW, use_color))

    return "\n".join(lines)
