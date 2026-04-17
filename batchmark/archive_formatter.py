"""Format archive listings and archive report details."""

from __future__ import annotations

from typing import List

from batchmark.archiver import ArchiveEntry


def _color(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_archive_list(entries: List[ArchiveEntry]) -> str:
    if not entries:
        return _color(33, "No archives saved.")
    lines = [_color(1, "Saved archives:")]
    for e in entries:
        branches = ", ".join(e.branches) if e.branches else "unknown"
        lines.append(f"  {_color(36, e.name)}  [{e.created_at}]  branches: {branches}")
    return "\n".join(lines)


def format_archive_detail(payload: dict) -> str:
    name = payload.get("name", "?")
    created = payload.get("created_at", "?")
    report = payload.get("report", {})
    branches = ", ".join(report.get("branches", []))
    suites = report.get("suites", [])

    lines = [
        _color(1, f"Archive: {name}"),
        f"  Created : {created}",
        f"  Branches: {branches}",
        f"  Suites  : {len(suites)}",
    ]
    for s in suites:
        suite_name = s.get("suite", "?")
        verdict = s.get("verdict", "?")
        delta = s.get("delta_pct")
        delta_str = f"{delta:+.1f}%" if delta is not None else "n/a"
        color = 32 if verdict == "improvement" else 31 if verdict == "regression" else 37
        lines.append(f"    {suite_name:<30} {_color(color, verdict):<20} {delta_str}")
    return "\n".join(lines)
