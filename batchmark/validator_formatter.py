"""Formats ValidationReport for terminal output."""
from __future__ import annotations

from batchmark.validator import ValidationReport


def _color(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_validation_report(report: ValidationReport) -> str:
    lines: list[str] = []

    if report.passed:
        lines.append(_color(32, "✔ All validation rules passed."))
        return "\n".join(lines)

    lines.append(_color(31, f"✘ Validation failed — {len(report.violations)} violation(s):"))
    lines.append("")

    header = f"  {'Suite':<24} {'Branch':<16} {'Rule':<22} Detail"
    lines.append(_color(1, header))
    lines.append("  " + "-" * 74)

    for v in report.violations:
        suite = v.suite[:23].ljust(24)
        branch = v.branch[:15].ljust(16)
        rule = v.rule[:21].ljust(22)
        lines.append(f"  {_color(33, suite)} {branch} {_color(36, rule)} {v.detail}")

    return "\n".join(lines)
