"""Format a MergeReport for terminal output."""

from __future__ import annotations

from typing import List

from batchmark.merger import MergeReport
from batchmark.comparator import SuiteComparison


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _verdict(cmp: SuiteComparison) -> str:
    if cmp.delta_pct is None:
        return _color("N/A", "33")
    if cmp.delta_pct < -0.01:
        return _color(f"{cmp.delta_pct:+.1%}", "32")
    if cmp.delta_pct > 0.01:
        return _color(f"{cmp.delta_pct:+.1%}", "31")
    return _color(f"{cmp.delta_pct:+.1%}", "37")


def format_merge_report(report: MergeReport) -> str:
    lines: List[str] = []
    branches_str = ", ".join(report.branches)
    lines.append(_color(f"Merged report — branches: {branches_str}", "1"))
    lines.append(f"  Total unique suites: {report.total_suites()}")
    lines.append("")

    for suite_name in report.all_suite_names():
        lines.append(_color(f"  Suite: {suite_name}", "1;34"))
        for cmp in report.comparisons_for(suite_name):
            branch_label = " vs ".join(cmp.branches) if hasattr(cmp, "branches") else ""
            verdict = _verdict(cmp)
            baseline = f"{cmp.baseline_duration:.3f}s" if cmp.baseline_duration is not None else "N/A"
            candidate = f"{cmp.candidate_duration:.3f}s" if cmp.candidate_duration is not None else "N/A"
            lines.append(f"    {branch_label:<30} baseline={baseline}  candidate={candidate}  delta={verdict}")
        lines.append("")

    return "\n".join(lines)
