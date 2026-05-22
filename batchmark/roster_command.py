"""CLI sub-commands for roster management."""
from __future__ import annotations

import argparse
from pathlib import Path

from .roster import RosterError, build_roster, list_rosters, load_roster, save_roster
from .roster_formatter import format_roster_detail, format_roster_list, format_roster_summary


_DEFAULT_STORE = Path(".batchmark/rosters")


def add_roster_subparser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("roster", help="Manage branch/suite rosters")
    cmds = p.add_subparsers(dest="roster_cmd")

    cmds.add_parser("list", help="List saved rosters")

    show = cmds.add_parser("show", help="Show roster detail")
    show.add_argument("name", help="Roster name")

    p.add_argument("--store", default=str(_DEFAULT_STORE), help="Roster store directory")


def run_roster_command(args: argparse.Namespace) -> int:
    store = Path(getattr(args, "store", str(_DEFAULT_STORE)))
    cmd = getattr(args, "roster_cmd", None)

    if cmd == "list":
        names = list_rosters(store)
        print(format_roster_list(names))
        return 0

    if cmd == "show":
        try:
            roster = load_roster(store, args.name)
        except RosterError as exc:
            print(f"Error: {exc}")
            return 1
        print(format_roster_detail(args.name, roster))
        print(format_roster_summary(roster))
        return 0

    print("No roster sub-command given. Use --help.")
    return 1
