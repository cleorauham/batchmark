"""Formatter for IsolateReport."""

from __future__ import annotations

from .isolator import IsolateReport, IsolatedSuite


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _fmt(value: float) -> str:
    return f"{value:.4f}s"


def _row(s: IsolatedSuite) -> str:
    flag = _color(" [ANOMALY]", "31") if s.is_anomalous else ""
    return (
        f"  {s.suite:<30} {s.branch:<20} "
        f"mean={_fmt(s.mean)}  stdev={_fmt(s.stdev)}{flag}"
    )


def format_isolate_report(report: IsolateReport) -> str:
    if not report.suites:
        return _color("No isolation data available.", "33")

    lines = [
        _color(
            f"Isolation Report  [{report.branch_a}] vs [{report.branch_b}]",
            "1",
        ),
        "",
        f"  {'Suite':<30} {'Branch':<20} {'Stats'}",
        "  " + "-" * 70,
    ]

    for s in report.suites:
        lines.append(_row(s))

    anomalous = report.anomalous()
    lines.append("")
    if anomalous:
        unique = {a.suite for a in anomalous}
        lines.append(
            _color(f"  {len(unique)} anomalous suite(s) detected.", "31")
        )
    else:
        lines.append(_color("  No anomalies detected.", "32"))

    return "\n".join(lines)
