from __future__ import annotations

import argparse
from typing import Optional

from batchmark.archiver import load_archive, ArchiveError
from batchmark.merger import merge, MergeError
from batchmark.merge_formatter import format_merge_report


def add_comparer_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "compare-archives",
        help="Compare two saved archive entries side-by-side",
    )
    p.add_argument("baseline", help="Name of the baseline archive entry")
    p.add_argument("candidate", help="Name of the candidate archive entry")
    p.add_argument(
        "--store",
        default=".batchmark/archives",
        help="Directory where archives are stored (default: .batchmark/archives)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    p.set_defaults(command="compare-archives")


def run_comparer_command(args: argparse.Namespace) -> int:
    store = args.store
    try:
        baseline_entry = load_archive(store, args.baseline)
    except ArchiveError as exc:
        print(f"error: baseline archive '{args.baseline}' not found: {exc}")
        return 1

    try:
        candidate_entry = load_archive(store, args.candidate)
    except ArchiveError as exc:
        print(f"error: candidate archive '{args.candidate}' not found: {exc}")
        return 1

    try:
        merged = merge([baseline_entry.report, candidate_entry.report])
    except MergeError as exc:
        print(f"error: could not merge reports: {exc}")
        return 1

    color = not args.no_color
    print(format_merge_report(merged, color=color))
    return 0
