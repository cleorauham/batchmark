"""Format ClassifyReport for terminal output."""
from __future__ import annotations

from typing import List

from batchmark.classifier import ClassifyReport, TIERS

_TIER_COLORS = {
    "fast": "\033[32m",      # green
    "moderate": "\033[36m",  # cyan
    "slow": "\033[33m",      # yellow
    "critical": "\033[31m",  # red
}
_RESET = "\033[0m"


def _color(tier: str, text: str) -> str:
    return f"{_TIER_COLORS.get(tier, '')}{text}{_RESET}"


def format_classify_report(report: ClassifyReport, *, color: bool = True) -> str:
    lines: List[str] = []
    lines.append("Benchmark Classification Report")
    lines.append(
        f"  Thresholds — fast: {report.thresholds['fast']}s  "
        f"moderate: {report.thresholds['moderate']}s  "
        f"slow: {report.thresholds['slow']}s"
    )
    lines.append("")

    for tier in TIERS:
        bucket = report.buckets[tier]
        header = f"[{tier.upper()}]  ({len(bucket)} result(s))"
        lines.append(_color(tier, header) if color else header)
        if not bucket.results:
            lines.append("    (none)")
        else:
            for cr in sorted(bucket.results, key=lambda x: x.duration):
                row = f"    {cr.suite:<30} {cr.branch:<20} {cr.duration:.4f}s"
                lines.append(row)
        lines.append("")

    lines.append(f"Total classified: {report.total()}")
    return "\n".join(lines)
