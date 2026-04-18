"""CLI sub-command handler for snapshot management."""
from __future__ import annotations

import argparse
import sys

from batchmark.snapshotter import SnapshotError, delete_snapshot, list_snapshots, load_snapshot, save_snapshot
from batchmark.snapshot_formatter import format_snapshot_detail, format_snapshot_list

_DEFAULT_DIR = ".batchmark/snapshots"


def add_snapshot_subparser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("snapshot", help="Manage report snapshots")
    p.add_argument("action", choices=["save", "show", "list", "delete"])
    p.add_argument("name", nargs="?", default=None)
    p.add_argument("--store", default=_DEFAULT_DIR)


def run_snapshot_command(args: argparse.Namespace, report: object | None = None) -> int:
    store = args.store
    action = args.action
    name = args.name

    if action == "list":
        names = list_snapshots(store)
        print(format_snapshot_list(names))
        return 0

    if action == "save":
        if not name:
            print("Error: name required for save", file=sys.stderr)
            return 2
        if report is None:
            print("Error: no report provided", file=sys.stderr)
            return 2
        path = save_snapshot(store, name, report)
        print(f"Snapshot saved: {path}")
        return 0

    if action == "show":
        if not name:
            print("Error: name required for show", file=sys.stderr)
            return 2
        try:
            entry = load_snapshot(store, name)
        except SnapshotError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(format_snapshot_detail(entry))
        return 0

    if action == "delete":
        if not name:
            print("Error: name required for delete", file=sys.stderr)
            return 2
        try:
            delete_snapshot(store, name)
        except SnapshotError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(f"Snapshot deleted: {name}")
        return 0

    return 2
