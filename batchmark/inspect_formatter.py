"""Format InspectReport for terminal output."""
from __future__ import annotations
from batchmark.inspector import InspectReport, SuiteInspection


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _fmt(val: float | None) -> str:
    return f"{val:.4f}s" if val is not None else "n/a"


def _fmt_row(label: str, value: str, width: int = 20) -> str:
    return f"  {label:<{width}} {value}"


def format_inspection(ins: SuiteInspection) -> str:
    lines = [_color(f"Suite: {ins.suite}", "1;36")]
    for branch in ins.branches:
        result = ins.get(branch)
        if result is None:
            lines.append(_fmt_row(branch, _color("missing", "33")))
        elif not result.success:
            lines.append(_fmt_row(branch, _color("failed", "31")))
        else:
            lines.append(_fmt_row(branch, _fmt(result.duration)))
    fastest = ins.fastest()
    slowest = ins.slowest()
    spread = ins.spread()
    if fastest:
        lines.append(_fmt_row("fastest:", _color(fastest, "32")))
    if slowest:
        lines.append(_fmt_row("slowest:", _color(slowest, "31")))
    if spread is not None:
        lines.append(_fmt_row("spread:", _fmt(spread)))
    return "\n".join(lines)


def format_inspect_report(report: InspectReport) -> str:
    if not report.inspections:
        return _color("No results to inspect.", "33")
    sections = [format_inspection(ins) for ins in report.inspections]
    return "\n\n".join(sections)
