"""Format pruner results for CLI output."""
from __future__ import annotations

from batchmark.pruner import PruneResult


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_prune_result(result: PruneResult, dry_run: bool = False) -> str:
    lines = []
    mode = " (dry run)" if dry_run else ""
    title = _color(f"Prune result{mode}", "1")
    lines.append(title)

    if not result.removed:
        lines.append("  Nothing to remove.")
    else:
        lines.append(f"  Removed ({result.total_removed}):")
        for name in result.removed:
            lines.append("    " + _color(f"- {name}", "31"))

    lines.append(f"  Kept: {_color(str(result.kept), '32')}")
    return "\n".join(lines)
