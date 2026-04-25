"""Format a HeatmapReport as a coloured ASCII table."""
from __future__ import annotations

from typing import List, Optional

from batchmark.heatmap import HeatmapReport

_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_GREY = "\033[90m"

_COL_W = 12
_LABEL_W = 20


def _color(value: float, lo: float, hi: float) -> str:
    """Return ANSI colour based on relative position in [lo, hi]."""
    if hi == lo:
        return _YELLOW
    ratio = (value - lo) / (hi - lo)
    if ratio < 0.33:
        return _GREEN
    if ratio < 0.66:
        return _YELLOW
    return _RED


def _fmt(value: Optional[float]) -> str:
    if value is None:
        return "-".center(_COL_W)
    return f"{value:.3f}s".center(_COL_W)


def format_heatmap(report: HeatmapReport) -> str:
    if not report.suites or not report.branches:
        return "No heatmap data available.\n"

    # Determine global min/max for colouring
    all_vals = [
        report.cells[s][b].mean_duration
        for s in report.suites
        for b in report.branches
        if report.cells[s][b] is not None
    ]
    lo, hi = (min(all_vals), max(all_vals)) if all_vals else (0.0, 1.0)

    lines: List[str] = []
    header = " " * _LABEL_W + "".join(
        f"{_BOLD}{b[:_COL_W].center(_COL_W)}{_RESET}" for b in report.branches
    )
    lines.append(header)
    lines.append("-" * (_LABEL_W + _COL_W * len(report.branches)))

    for suite in report.suites:
        row = f"{suite[:_LABEL_W]:<{_LABEL_W}}"
        for branch in report.branches:
            cell = report.cells[suite][branch]
            if cell is None:
                row += _GREY + _fmt(None) + _RESET
            else:
                c = _color(cell.mean_duration, lo, hi)
                row += c + _fmt(cell.mean_duration) + _RESET
        lines.append(row)

    return "\n".join(lines) + "\n"
