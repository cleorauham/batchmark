"""Formatter for SampleReport output."""

from __future__ import annotations

from typing import List

from batchmark.sampler import SampleReport


def _color(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _fmt_float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.4f}s"


def format_sample_report(reports: List[SampleReport], *, color: bool = True) -> str:
    """Return a human-readable table of sampled results."""
    if not reports:
        return _color("33", "No sample data.") if color else "No sample data."

    lines: List[str] = []
    header = f"{'Branch':<20} {'Suite':<30} {'Sampled':>8} {'Available':>10} {'Mean':>12}"
    sep = "-" * len(header)
    lines.append(sep)
    lines.append(header)
    lines.append(sep)

    for r in reports:
        mean_str = _fmt_float(r.mean_duration)
        branch_str = _color("36", r.branch) if color else r.branch
        suite_str = _color("34", r.suite) if color else r.suite
        lines.append(
            f"{branch_str:<20} {suite_str:<30} {r.sample_size:>8} {r.total_available:>10} {mean_str:>12}"
        )

    lines.append(sep)
    total_sampled = sum(r.sample_size for r in reports)
    total_available = sum(r.total_available for r in reports)
    lines.append(f"Total: {total_sampled} sampled from {total_available} available")
    return "\n".join(lines)
