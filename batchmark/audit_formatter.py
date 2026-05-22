"""Formatter for AuditReport output."""
from __future__ import annotations

from batchmark.auditor import AuditReport


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _ok(s: str) -> str:
    return _color(s, "32")


def _fail(s: str) -> str:
    return _color(s, "31")


def _bold(s: str) -> str:
    return _color(s, "1")


def format_audit_list(names: list[str]) -> str:
    if not names:
        return _color("No audit records found.", "33")
    lines = [_bold("Audit records:")]
    for name in names:
        lines.append(f"  {name}")
    return "\n".join(lines)


def format_audit_report(report: AuditReport, name: str = "") -> str:
    if not report.entries:
        return _color("Audit report is empty.", "33")

    header = _bold(f"Audit: {name}") if name else _bold("Audit Report")
    lines = [header, ""]

    branches = report.branches()
    for branch in branches:
        entries = report.by_branch(branch)
        total = len(entries)
        failed = sum(1 for e in entries if not e.success)
        passed = total - failed
        branch_label = _bold(f"Branch: {branch}")
        lines.append(f"  {branch_label}  ({passed} passed, {failed} failed)")
        for e in entries:
            status = _ok("OK") if e.success else _fail("FAIL")
            lines.append(f"    [{status}] {e.suite:<30} {e.duration:.4f}s")
        lines.append("")

    total = len(report.entries)
    total_failed = len(report.failed())
    summary = f"Total: {total} entries, {total_failed} failed"
    lines.append(_bold(summary))
    return "\n".join(lines)
