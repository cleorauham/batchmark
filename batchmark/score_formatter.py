from __future__ import annotations

from batchmark.scorer import ScoreReport


def _color(text: str, code: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def _score_color(score: float, enabled: bool) -> str:
    if score >= 0.9:
        return _color(f"{score:.4f}", "32", enabled)  # green
    if score >= 0.7:
        return _color(f"{score:.4f}", "33", enabled)  # yellow
    return _color(f"{score:.4f}", "31", enabled)  # red


def format_score_report(report: ScoreReport, *, color: bool = True) -> str:
    if not report.by_branch:
        return _color("No score data available.", "33", color)

    lines = [_color("Branch Scores", "1", color), ""]
    header = f"  {'Branch':<24} {'Score':>10} {'Suites':>8} {'Mean (s)':>12}"
    lines.append(header)
    lines.append("  " + "-" * 56)

    ranked = sorted(report.by_branch.items(), key=lambda kv: kv[1].total, reverse=True)
    for branch, suite_score in ranked:
        score_str = _score_color(suite_score.total, color)
        row = (
            f"  {branch:<24} {score_str:>10} "
            f"{len(suite_score.suite_scores):>8} "
            f"{suite_score.mean_duration:>12.4f}"
        )
        lines.append(row)

    lines.append("")
    best = report.best_branch
    if best:
        lines.append(
            "  Best branch: " + _color(best, "32;1", color)
        )
    return "\n".join(lines)
