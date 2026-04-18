"""Format label entries for CLI display."""
from __future__ import annotations

from typing import List

from batchmark.labeler import LabelEntry


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_label_list(entries: List[LabelEntry]) -> str:
    if not entries:
        return _color("No labels stored.", "33")
    lines = [_color("Stored labels:", "1")]
    for e in entries:
        tags = ", ".join(e.labels) if e.labels else "(none)"
        line = f"  {_color(e.run_id, '36')}  [{tags}]"
        if e.note:
            line += f"  — {e.note}"
        lines.append(line)
    return "\n".join(lines)


def format_label_detail(entry: LabelEntry) -> str:
    lines = [
        f"{_color('Run ID:', '1')} {entry.run_id}",
        f"{_color('Labels:', '1')} {', '.join(entry.labels) if entry.labels else '(none)'}",
    ]
    if entry.note:
        lines.append(f"{_color('Note:', '1')} {entry.note}")
    return "\n".join(lines)
