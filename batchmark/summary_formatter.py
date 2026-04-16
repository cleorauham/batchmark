"""Format a summarized benchmark report as a text table."""
from typing import List
from batchmark.summarizer import SuiteSummaryRow, summary_counts

_VERDICT_COLOR = {
    "improved": "\033[32m",
    "regressed": "\033[31m",
    "unchanged": "\033[0m",
    "missing": "\033[33m",
}
_RESET = "\033[0m"


def _colorize(text: str, verdict: str, color: bool) -> str:
    if not color:
        return text
    code = _VERDICT_COLOR.get(verdict, "")
    return f"{code}{text}{_RESET}"


def _fmt_float(value) -> str:
    return f"{value:.4f}s" if value is not None else "N/A"


def _fmt_delta(value) -> str:
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def format_summary(rows: List[SuiteSummaryRow], color: bool = True) -> str:
    header = f"{'Suite':<30} {'Baseline':>10} {'Candidate':>10} {'Delta':>10} {'Verdict':<12}"
    sep = "-" * len(header)
    lines = [header, sep]

    for row in rows:
        verdict_str = _colorize(row.verdict.upper(), row.verdict, color)
        line = (
            f"{row.suite:<30} "
            f"{_fmt_float(row.baseline_mean):>10} "
            f"{_fmt_float(row.candidate_mean):>10} "
            f"{_fmt_delta(row.delta_pct):>10} "
            f"{verdict_str:<12}"
        )
        lines.append(line)

    lines.append(sep)
    counts = summary_counts(rows)
    lines.append(
        f"Summary: {counts['improved']} improved, "
        f"{counts['regressed']} regressed, "
        f"{counts['unchanged']} unchanged, "
        f"{counts['missing']} missing"
    )
    return "\n".join(lines)
