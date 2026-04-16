"""Format a ReportDiff for terminal output."""
from __future__ import annotations

from batchmark.differ import ReportDiff, SuiteDelta
from batchmark.formatter import _color

_COL = (28, 12, 12, 10)


def _row(suite: str, base: str, cand: str, delta: str, color_fn=None) -> str:
    row = f"{suite:<{_COL[0]}}{base:<{_COL[1]}}{cand:<{_COL[2]}}{delta:<{_COL[3]}}"
    return color_fn(row) if color_fn else row


def format_diff(diff: ReportDiff) -> str:
    lines: list[str] = []
    lines.append(
        f"Diff: {diff.baseline_branch!r} → {diff.candidate_branch!r}"
    )
    lines.append("-" * sum(_COL))
    lines.append(
        _row("Suite", "Baseline(s)", "Candidate(s)", "Δ %")
    )
    lines.append("-" * sum(_COL))

    for delta in sorted(diff.deltas, key=lambda d: d.suite_name):
        base_str = f"{delta.baseline_mean:.4f}" if delta.baseline_mean is not None else "—"
        cand_str = f"{delta.candidate_mean:.4f}" if delta.candidate_mean is not None else "—"

        if delta.only_in_baseline:
            delta_str = "removed"
            color_fn = lambda s: _color(s, "yellow")
        elif delta.only_in_candidate:
            delta_str = "added"
            color_fn = lambda s: _color(s, "cyan")
        elif delta.delta_pct is not None:
            sign = "+" if delta.delta_pct >= 0 else ""
            delta_str = f"{sign}{delta.delta_pct:.2f}%"
            if delta.delta_pct > 0:
                color_fn = lambda s: _color(s, "red")
            elif delta.delta_pct < 0:
                color_fn = lambda s: _color(s, "green")
            else:
                color_fn = None
        else:
            delta_str = "n/a"
            color_fn = None

        lines.append(_row(delta.suite_name, base_str, cand_str, delta_str, color_fn))

    lines.append("-" * sum(_COL))
    reg = len(diff.regressions)
    imp = len(diff.improvements)
    lines.append(f"Regressions: {reg}  Improvements: {imp}")
    return "\n".join(lines)
