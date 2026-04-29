"""Formatter for BalanceReport."""
from __future__ import annotations

from batchmark.balancer import BalanceReport


def _color(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_balance_report(report: BalanceReport, *, color: bool = True) -> str:
    if not report.workers:
        return _color(33, "(no workers)") if color else "(no workers)"

    lines: list[str] = []
    header = f"{'Worker':>8}  {'Suites':>6}  {'Est. Weight':>12}  Suite Names"
    lines.append(_color(1, header) if color else header)
    lines.append("-" * 60)

    for w in report.workers:
        weight = w.estimated_weight()
        names = ", ".join(w.suite_names()) if w.suite_names() else "(empty)"
        row = f"{w.worker_id:>8}  {len(w):>6}  {weight:>12.1f}  {names}"
        lines.append(row)

    lines.append("-" * 60)
    most = report.most_loaded()
    least = report.least_loaded()
    summary = (
        f"Total suites: {report.total_suites}  "
        f"Most loaded: worker {most.worker_id} ({most.estimated_weight():.1f})  "
        f"Least loaded: worker {least.worker_id} ({least.estimated_weight():.1f})"
    )
    lines.append(_color(36, summary) if color else summary)
    return "\n".join(lines)
