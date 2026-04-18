"""Format annotations for CLI display."""
from __future__ import annotations

from batchmark.annotator import Annotation


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_annotation_list(annotations: list[Annotation]) -> str:
    if not annotations:
        return _color("No annotations stored.", "33")
    lines = [_color("Stored annotations:", "1")]
    for a in annotations:
        tags = f"  [{', '.join(a.tags)}]" if a.tags else ""
        lines.append(f"  {_color(a.suite, '36')} @ {_color(a.branch, '32')}{tags}")
        lines.append(f"    {a.note}")
    return "\n".join(lines)


def format_annotation_detail(a: Annotation) -> str:
    lines = [
        f"{_color('Suite:', '1')}  {a.suite}",
        f"{_color('Branch:', '1')} {a.branch}",
        f"{_color('Note:', '1')}   {a.note}",
    ]
    if a.tags:
        lines.append(f"{_color('Tags:', '1')}   {', '.join(a.tags)}")
    return "\n".join(lines)
