"""Format tag listings and details for CLI output."""

from __future__ import annotations

from batchmark.tagger import TagEntry


_RESET = "\033[0m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"
_DIM = "\033[2m"


def _color(text: str, code: str, enabled: bool = True) -> str:
    return f"{code}{text}{_RESET}" if enabled else text


def format_tag_list(names: list[str], color: bool = True) -> str:
    if not names:
        return "No tags saved."
    lines = [_color("Saved tags:", _BOLD, color)]
    for name in names:
        lines.append(f"  {_color(name, _CYAN, color)}")
    return "\n".join(lines)


def format_tag_detail(entry: TagEntry, color: bool = True) -> str:
    lines = [
        f"{_color('Tag:', _BOLD, color)} {_color(entry.name, _CYAN, color)}",
        f"  Branch  : {entry.branch}",
        f"  Created : {_color(entry.created_at, _DIM, color)}",
    ]
    if entry.meta:
        lines.append("  Meta:")
        for k, v in entry.meta.items():
            lines.append(f"    {k}: {v}")
    return "\n".join(lines)
