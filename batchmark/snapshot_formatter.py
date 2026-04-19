"""Formatting helpers for snapshot listings and details."""
from __future__ import annotations

from batchmark.snapshotter import SnapshotEntry


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _verdict_color(verdict: str) -> str:
    """Return a colored verdict string based on its value."""
    if verdict.lower() in ("pass", "improved"):
        return _color(verdict, "32")  # green
    if verdict.lower() in ("fail", "regression"):
        return _color(verdict, "31")  # red
    return _color(verdict, "33")  # yellow for unknown/neutral


def format_snapshot_list(names: list[str]) -> str:
    if not names:
        return _color("No snapshots found.", "33")
    lines = [_color("Snapshots:", "1")]
    for name in names:
        lines.append(f"  • {name}")
    return "\n".join(lines)


def format_snapshot_detail(entry: SnapshotEntry) -> str:
    lines = [
        _color(f"Snapshot: {entry.name}", "1"),
        f"  Created : {entry.created_at}",
        f"  Branches: {', '.join(entry.branches)}",
    ]
    suites = entry.data.get("comparisons", [])
    if suites:
        lines.append(f"  Suites  : {len(suites)}")
        for cmp in suites:
            suite = cmp.get("suite", "?")
            verdict = cmp.get("summary", {}).get("verdict", "")
            lines.append(f"    - {suite}  [{_verdict_color(verdict)}]")
    return "\n".join(lines)
