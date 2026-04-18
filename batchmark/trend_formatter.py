"""Format trend reports for terminal output."""
from batchmark.trend import TrendReport, SuiteTrend

_RESET = "\033[0m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _color(text: str, verdict: str) -> str:
    c = {"degrading": _RED, "improving": _GREEN, "stable": _YELLOW}.get(verdict, "")
    return f"{c}{text}{_RESET}" if c else text


def _fmt_slope(slope) -> str:
    if slope is None:
        return "   n/a"
    sign = "+" if slope >= 0 else ""
    return f"{sign}{slope:.3f}s"


def format_trend(report: TrendReport, branch: str) -> str:
    lines = []
    lines.append(f"{_BOLD}Trend report — branch: {branch}{_RESET}")
    lines.append(f"Baselines analysed: {len(report.baselines)}")
    if report.baselines:
        lines.append("  " + ", ".join(report.baselines))
    lines.append("")

    if not report.trends:
        lines.append("  No trend data available.")
        return "\n".join(lines)

    header = f"  {'Suite':<28} {'Slope':>10}  {'Verdict'}"
    lines.append(header)
    lines.append("  " + "-" * 52)

    for trend in sorted(report.trends, key=lambda t: t.suite):
        slope_str = _fmt_slope(trend.slope)
        verdict = trend.verdict
        row = f"  {trend.suite:<28} {slope_str:>10}  {_color(verdict, verdict)}"
        lines.append(row)

    return "\n".join(lines)
