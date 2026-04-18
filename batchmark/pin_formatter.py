"""Formatting helpers for pin entries."""

from __future__ import annotations

from typing import List

from batchmark.pinner import PinEntry


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_pin_list(names: List[str]) -> str:
    if not names:
        return _color("No pins saved.", "33")
    lines = [_color("Saved pins:", "1")]
    for name in names:
        lines.append(f"  - {name}")
    return "\n".join(lines)


def format_pin_detail(entry: PinEntry) -> str:
    status = _color("PASS", "32") if entry.passed else _color("FAIL", "31")
    lines = [
        _color(f"Pin: {entry.name}", "1"),
        f"  Branch  : {entry.branch}",
        f"  Suite   : {entry.suite}",
        f"  Duration: {entry.duration:.4f}s",
        f"  Status  : {status}",
    ]
    if entry.note:
        lines.append(f"  Note    : {entry.note}")
    return "\n".join(lines)
