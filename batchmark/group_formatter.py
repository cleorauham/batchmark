"""Format a GroupReport for terminal output."""
from __future__ import annotations
from batchmark.grouper import GroupReport, ResultGroup


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _fmt_group(group: ResultGroup) -> str:
    lines = []
    header = _color(f"[{group.key}]", "1;36")
    lines.append(header)
    lines.append(f"  Suites   : {len(group.comparisons)}")
    reg = group.regression_count
    imp = group.improvement_count
    reg_str = _color(str(reg), "31") if reg else str(reg)
    imp_str = _color(str(imp), "32") if imp else str(imp)
    lines.append(f"  Regressions : {reg_str}")
    lines.append(f"  Improvements: {imp_str}")
    for cmp in group.comparisons:
        verdict = cmp.summary
        if verdict == "regression":
            verdict = _color(verdict, "31")
        elif verdict == "improvement":
            verdict = _color(verdict, "32")
        lines.append(f"    - {cmp.suite}: {verdict}")
    return "\n".join(lines)


def format_group_report(report: GroupReport) -> str:
    if not report.groups:
        return "No groups found."
    sections = [_fmt_group(report.groups[k]) for k in sorted(report.keys())]
    return "\n\n".join(sections)
