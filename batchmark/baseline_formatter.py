"""Format a list of baselines or baseline results for CLI display."""

from __future__ import annotations

from batchmark.runner import BenchmarkResult

_GREEN = "\033[32m"
_RED = "\033[31m"
_RESET = "\033[0m"
_BOLD = "\033[1m"


def _color(text: str, code: str, *, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{code}{text}{_RESET}"


def format_baseline_list(names: list[str], *, use_color: bool = True) -> str:
    if not names:
        return "No baselines saved."
    header = _color("Saved baselines:", _BOLD, use_color=use_color)
    rows = [f"  • {name}" for name in names]
    return "\n".join([header] + rows)


def format_baseline_results(
    results: list[BenchmarkResult],
    name: str,
    *,
    use_color: bool = True,
) -> str:
    header = _color(f"Baseline: {name}", _BOLD, use_color=use_color)
    if not results:
        return f"{header}\n  (no results)"

    lines = [header]
    col_w = max(len(r.suite) for r in results)
    for r in results:
        if r.success:
            status = _color("OK", _GREEN, use_color=use_color)
            dur = f"{r.duration:.4f}s"
        else:
            status = _color("FAIL", _RED, use_color=use_color)
            dur = r.error or "unknown error"
        suite_col = r.suite.ljust(col_w)
        lines.append(f"  {suite_col}  [{r.branch}]  {status}  {dur}")
    return "\n".join(lines)
