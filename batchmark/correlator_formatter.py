"""Format CorrelationReport for terminal output."""
from __future__ import annotations

from batchmark.correlator import CorrelationReport


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _verdict_color(verdict: str) -> str:
    if verdict == "strong-positive":
        return _color(verdict, "32")
    if verdict == "moderate-positive":
        return _color(verdict, "36")
    if verdict == "strong-negative":
        return _color(verdict, "31")
    if verdict == "moderate-negative":
        return _color(verdict, "33")
    return _color(verdict, "37")


def format_correlation_report(report: CorrelationReport) -> str:
    lines = []
    lines.append(_color(f"Correlation Report — branch: {report.branch}", "1"))

    if not report.pairs:
        lines.append("  (no suite pairs to correlate)")
        return "\n".join(lines)

    header = f"  {'Suite A':<28} {'Suite B':<28} {'Coeff':>7}  Verdict"
    lines.append(header)
    lines.append("  " + "-" * 72)

    for pair in sorted(report.pairs, key=lambda p: -abs(p.coefficient)):
        verdict_str = _verdict_color(pair.verdict)
        lines.append(
            f"  {pair.suite_a:<28} {pair.suite_b:<28} {pair.coefficient:>7.4f}  {verdict_str}"
        )

    strong = report.strong_pairs()
    lines.append("")
    lines.append(f"  Strong correlations (|r| >= 0.8): {len(strong)}")
    return "\n".join(lines)
