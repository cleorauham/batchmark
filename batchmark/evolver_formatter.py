"""Formatter for EvolveReport."""
from __future__ import annotations

from batchmark.evolver import EvolveReport

_RESET = "\033[0m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _color(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}"


def _verdict_color(verdict: str) -> str:
    if verdict == "improving":
        return _GREEN
    if verdict == "degrading":
        return _RED
    return _YELLOW


def _fmt(val: float) -> str:
    return f"{val:.2f}ms"


def format_evolution_report(report: EvolveReport) -> str:
    if not report.suites:
        return _color("No evolution data available.", _YELLOW)

    lines = [_color("Evolution Report", _BOLD), ""]
    for suite_name in report.all_suite_names():
        evolution = report.suites[suite_name]
        verdict = evolution.verdict()
        col = _verdict_color(verdict)
        lines.append(_color(f"  Suite: {suite_name}", _BOLD))
        lines.append(f"    Verdict : {_color(verdict.upper(), col)}")
        net = evolution.net_change()
        if net is not None:
            sign = "+" if net >= 0 else ""
            lines.append(f"    Net Δ   : {_color(sign + _fmt(net), col)}")
        lines.append(f"    Snapshots:")
        for pt in evolution.points:
            reg = pt.regression_count
            imp = pt.improvement_count
            lines.append(
                f"      [{pt.label}] mean={_fmt(pt.mean_duration)}"
                f"  regressions={reg}  improvements={imp}"
            )
        lines.append("")
    return "\n".join(lines).rstrip()
