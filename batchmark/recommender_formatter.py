"""Formatter for RecommendationReport."""
from __future__ import annotations

from batchmark.recommender import RecommendationReport

_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _color(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}"


_KIND_COLOR = {
    "investigate": _RED,
    "promote": _GREEN,
    "skip": _YELLOW,
}


def format_recommendation_report(report: RecommendationReport) -> str:
    """Format a RecommendationReport as a human-readable, color-coded string.

    Args:
        report: The RecommendationReport to format.

    Returns:
        A multi-line string with ANSI color codes suitable for terminal output.
    """
    if not report.recommendations:
        return _color("No recommendations.", _BOLD)

    lines = [_color("Recommendations", _BOLD)]
    lines.append("-" * 60)

    for kind in ("investigate", "promote", "skip"):
        items = report.by_kind(kind)
        if not items:
            continue
        color = _KIND_COLOR.get(kind, "")
        lines.append(_color(f"  {kind.upper()} ({len(items)})", color))
        for rec in items:
            lines.append(f"    {rec.branch}/{rec.suite}  —  {rec.reason}")

    lines.append("-" * 60)
    total = len(report.recommendations)
    inv = len(report.investigate)
    pro = len(report.promote)
    skp = len(report.skip)
    lines.append(
        f"Total: {total}  "
        f"investigate={_color(str(inv), _RED)}  "
        f"promote={_color(str(pro), _GREEN)}  "
        f"skip={_color(str(skp), _YELLOW)}"
    )
    return "\n".join(lines)


def format_recommendation_report_plain(report: RecommendationReport) -> str:
    """Format a RecommendationReport as plain text without ANSI color codes.

    Useful for writing output to log files or non-terminal consumers.

    Args:
        report: The RecommendationReport to format.

    Returns:
        A multi-line plain-text string with no ANSI escape sequences.
    """
    if not report.recommendations:
        return "No recommendations."

    lines = ["Recommendations", "-" * 60]

    for kind in ("investigate", "promote", "skip"):
        items = report.by_kind(kind)
        if not items:
            continue
        lines.append(f"  {kind.upper()} ({len(items)})")
        for rec in items:
            lines.append(f"    {rec.branch}/{rec.suite}  —  {rec.reason}")

    lines.append("-" * 60)
    total = len(report.recommendations)
    inv = len(report.investigate)
    pro = len(report.promote)
    skp = len(report.skip)
    lines.append(
        f"Total: {total}  investigate={inv}  promote={pro}  skip={skp}"
    )
    return "\n".join(lines)
