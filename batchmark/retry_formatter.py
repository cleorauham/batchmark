"""Formatter for RetryReport output."""
from __future__ import annotations

from batchmark.retrier import RetryRecord, RetryReport


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _fmt_float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}s"


def _fmt_record(rec: RetryRecord) -> str:
    status = _color("OK", "32") if rec.succeeded else _color("FAIL", "31")
    attempts_str = (
        _color(str(rec.attempts), "33") if rec.attempts > 1 else str(rec.attempts)
    )
    mean = _fmt_float(rec.mean_duration)
    return (
        f"  [{status}] {rec.suite} @ {rec.branch} "
        f"attempts={attempts_str} mean={mean}"
    )


def format_retry_report(report: RetryReport) -> str:
    """Return a human-readable string summarising the retry report."""
    if not report.records:
        return _color("No retry records.", "90")

    lines = [_color("Retry Report", "1")]
    lines.append(
        f"  Suites: {len(report.records)}  "
        f"Retried: {report.total_retried}  "
        f"Succeeded: {_color(str(report.total_succeeded), '32')}  "
        f"Failed: {_color(str(report.total_failed), '31')}"
    )
    lines.append("")
    for rec in report.records:
        lines.append(_fmt_record(rec))
    return "\n".join(lines)
