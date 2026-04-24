"""Format AggregateReport for terminal display."""

from __future__ import annotations

from typing import List

from batchmark.aggregator import AggregateReport, AggregatedSuite


def _color(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _fmt(value: float, decimals: int = 3) -> str:
    return f"{value:.{decimals}f}s"


def _success_color(rate: float) -> str:
    if rate >= 1.0:
        return _color(32, f"{rate:.0%}")
    if rate >= 0.5:
        return _color(33, f"{rate:.0%}")
    return _color(31, f"{rate:.0%}")


def _header() -> str:
    cols = [
        f"{'suite':<24}",
        f"{'branch':<16}",
        f"{'runs':>5}",
        f"{'mean':>10}",
        f"{'median':>10}",
        f"{'stdev':>10}",
        f"{'min':>10}",
        f"{'max':>10}",
        f"{'ok%':>6}",
    ]
    return "  ".join(cols)


def _row(entry: AggregatedSuite) -> str:
    cols = [
        f"{entry.suite:<24}",
        f"{entry.branch:<16}",
        f"{entry.runs:>5}",
        f"{_fmt(entry.mean):>10}",
        f"{_fmt(entry.median):>10}",
        f"{_fmt(entry.stdev):>10}",
        f"{_fmt(entry.min_duration):>10}",
        f"{_fmt(entry.max_duration):>10}",
        f"{_success_color(entry.success_rate):>6}",
    ]
    return "  ".join(cols)


def format_aggregate_report(report: AggregateReport) -> str:
    if not report.entries:
        return _color(33, "No aggregated results to display.")
    lines: List[str] = [
        _color(1, "Aggregate Report"),
        _color(90, "-" * 100),
        _color(90, _header()),
        _color(90, "-" * 100),
    ]
    for entry in report.entries:
        lines.append(_row(entry))
    lines.append(_color(90, "-" * 100))
    lines.append(
        f"  {len(report.entries)} suite/branch combination(s) across "
        f"{len(report.branches())} branch(es)."
    )
    return "\n".join(lines)
