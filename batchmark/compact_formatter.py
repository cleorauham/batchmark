"""Formatter for CompactReport output."""
from __future__ import annotations

from batchmark.compactor import CompactReport


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _fmt_float(v: float) -> str:
    return f"{v:.4f}s"


def format_compact_report(report: CompactReport) -> str:
    if not report.entries:
        return _color("No entries in compacted report.", "33")

    lines = [
        _color("Compact Report", "1"),
        f"  Sources merged : {report.sources_merged}",
        f"  Entries kept   : {report.total_kept}",
        f"  Entries removed: {report.total_removed}",
        "",
    ]

    header = f"  {'Suite':<28} {'Branch':<20} {'Duration':>10}  {'Status'}"
    lines.append(header)
    lines.append("  " + "-" * 68)

    for entry in report.entries:
        status = _color("PASS", "32") if entry.passed else _color("FAIL", "31")
        dur = _fmt_float(entry.duration)
        lines.append(f"  {entry.suite:<28} {entry.branch:<20} {dur:>10}  {status}")

    lines.append("")
    lines.append(
        f"  Compacted {report.total_kept} unique (suite, branch) pairs "
        f"from {report.sources_merged} source(s), "
        f"dropped {report.total_removed} duplicate(s)."
    )
    return "\n".join(lines)
