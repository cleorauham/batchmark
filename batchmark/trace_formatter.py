"""Formatter for TraceReport — renders timing spans as a readable table."""
from __future__ import annotations

from batchmark.tracer import TraceReport


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _fmt_duration(seconds: float) -> str:
    if seconds >= 1.0:
        return f"{seconds:.3f}s"
    return f"{seconds * 1000:.1f}ms"


def _status(success: bool) -> str:
    if success:
        return _color("PASS", "32")
    return _color("FAIL", "31")


def format_trace_report(report: TraceReport, *, color: bool = True) -> str:
    if not report.spans:
        return _color("No trace spans recorded.", "33") if color else "No trace spans recorded."

    lines = []
    header = f"{'Branch':<20} {'Suite':<30} {'Duration':>12}  Status"
    lines.append(_color(header, "1") if color else header)
    lines.append("-" * len(header))

    for branch, spans in sorted(report.by_branch().items()):
        for span in spans:
            dur = _fmt_duration(span.duration)
            status = _status(span.success) if color else ("PASS" if span.success else "FAIL")
            lines.append(f"{branch:<20} {span.suite:<30} {dur:>12}  {status}")

    total = _fmt_duration(report.total_duration())
    failed = len(report.failed_spans())
    summary = f"\nTotal: {total}  |  Spans: {len(report.spans)}  |  Failed: {failed}"
    lines.append(_color(summary, "36") if color else summary)
    return "\n".join(lines)
