"""Format replay reports for terminal output."""
from __future__ import annotations

from batchmark.replayer import ReplayReport


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_replay_report(report: ReplayReport, *, color: bool = True) -> str:
    lines: list[str] = []
    src = report.source
    header = f"Replay [{src.kind}] — {src.name}  ({len(report.results)} results)"
    lines.append(_color(header, "1;36") if color else header)
    lines.append("")

    if not report.results:
        lines.append("  (no results)")
        return "\n".join(lines)

    col_w = max(len(r.suite) for r in report.results) + 2
    lines.append(f"  {'Suite':<{col_w}} {'Branch':<20} {'Duration':>10}  Status")
    lines.append("  " + "-" * (col_w + 20 + 10 + 12))

    for r in report.results:
        status = _color("OK", "32") if r.success else _color("FAIL", "31")
        if not color:
            status = "OK" if r.success else "FAIL"
        dur = f"{r.duration:.4f}s" if r.duration is not None else "N/A"
        lines.append(f"  {r.suite:<{col_w}} {r.branch:<20} {dur:>10}  {status}")

    lines.append("")
    ok = len(report.succeeded)
    fail = len(report.failed)
    summary = f"Summary: {ok} ok, {fail} failed"
    lines.append(_color(summary, "1") if color else summary)
    return "\n".join(lines)
