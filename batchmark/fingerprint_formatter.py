"""Formatter for FingerprintReport."""
from __future__ import annotations

from batchmark.fingerprinter import FingerprintReport


def _color(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_fingerprint_report(report: FingerprintReport) -> str:
    if not report.entries:
        return _color(33, "(no fingerprint entries)")

    lines = [_color(1, "Fingerprint Report"), ""]
    by_branch = report.by_branch()

    for branch, entries in sorted(by_branch.items()):
        lines.append(_color(36, f"  Branch: {branch}"))
        for e in sorted(entries, key=lambda x: x.suite):
            lines.append(f"    {e.suite:<30}  {_color(33, e.fingerprint)}")
        lines.append("")

    total = len(report.entries)
    lines.append(_color(2, f"  Total entries: {total}"))
    return "\n".join(lines)
