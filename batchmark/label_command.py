"""CLI sub-commands for managing run labels."""
from __future__ import annotations

import argparse
from pathlib import Path

from batchmark.labeler import LabelEntry, LabelError, save_label, load_label, list_labels, delete_label
from batchmark.label_formatter import format_label_list, format_label_detail

_DEFAULT_STORE = Path(".batchmark/labels")


def add_label_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("label", help="Manage run labels")
    sub = p.add_subparsers(dest="label_cmd", required=True)

    add = sub.add_parser("add", help="Add labels to a run")
    add.add_argument("run_id")
    add.add_argument("labels", nargs="+")
    add.add_argument("--note", default=None)

    show = sub.add_parser("show", help="Show labels for a run")
    show.add_argument("run_id")

    sub.add_parser("list", help="List all labelled runs")

    rm = sub.add_parser("remove", help="Remove labels for a run")
    rm.add_argument("run_id")


def run_label_command(args: argparse.Namespace, store_dir: Path = _DEFAULT_STORE) -> int:
    if args.label_cmd == "add":
        entry = LabelEntry(run_id=args.run_id, labels=args.labels, note=args.note)
        save_label(store_dir, entry)
        print(f"Labels saved for '{args.run_id}'.")
        return 0

    if args.label_cmd == "show":
        try:
            entry = load_label(store_dir, args.run_id)
            print(format_label_detail(entry))
            return 0
        except LabelError as exc:
            print(str(exc))
            return 1

    if args.label_cmd == "list":
        entries = list_labels(store_dir)
        print(format_label_list(entries))
        return 0

    if args.label_cmd == "remove":
        removed = delete_label(store_dir, args.run_id)
        if removed:
            print(f"Labels removed for '{args.run_id}'.")
            return 0
        print(f"No labels found for '{args.run_id}'.")
        return 1

    return 1
