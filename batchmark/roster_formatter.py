"""Formatter for Roster data."""
from __future__ import annotations

from .roster import Roster


def _color(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_roster_list(names: list[str]) -> str:
    if not names:
        return _color(33, "(no rosters saved)")
    lines = [_color(1, "Saved rosters:")]
    for name in names:
        lines.append(f"  {_color(36, name)}")
    return "\n".join(lines)


def format_roster_detail(name: str, roster: Roster) -> str:
    if not roster.branches:
        return _color(33, f"Roster '{name}' is empty.")

    lines = [_color(1, f"Roster: {name}")]
    lines.append(f"  Branches : {len(roster.branches)}")
    lines.append(f"  Suites   : {len(roster.all_suites)}")
    lines.append("")

    for branch in roster.branches:
        lines.append(f"  {_color(36, branch)}")
        for suite in roster.suites_for(branch):
            lines.append(f"    - {suite}")

    return "\n".join(lines)


def format_roster_summary(roster: Roster) -> str:
    b = len(roster.branches)
    s = len(roster.all_suites)
    branch_word = "branch" if b == 1 else "branches"
    suite_word = "suite" if s == 1 else "suites"
    return (
        _color(32, "\u2714")
        + f" Roster covers {_color(1, str(b))} {branch_word}"
        + f" and {_color(1, str(s))} unique {suite_word}."
    )
