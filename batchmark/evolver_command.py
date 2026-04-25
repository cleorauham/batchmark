"""CLI subcommand for the evolver feature."""
from __future__ import annotations

import argparse
import sys
from typing import List

from batchmark.archiver import load_archive, ArchiveError
from batchmark.serializer import report_to_dict
from batchmark.evolver import build_evolution
from batchmark.evolver_formatter import format_evolution_report


def add_evolver_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "evolve",
        help="Show how benchmark results evolve across archived snapshots.",
    )
    p.add_argument(
        "archives",
        nargs="+",
        metavar="LABEL:ARCHIVE",
        help="One or more label:archive_name pairs.",
    )
    p.add_argument(
        "--store",
        default=".batchmark/archives",
        help="Directory where archives are stored.",
    )
    p.set_defaults(func=run_evolver_command)


def run_evolver_command(args: argparse.Namespace) -> int:
    labeled: List[tuple] = []
    for entry in args.archives:
        if ":" not in entry:
            print(f"error: expected LABEL:ARCHIVE, got '{entry}'", file=sys.stderr)
            return 2
        label, archive_name = entry.split(":", 1)
        try:
            archive_entry = load_archive(args.store, archive_name)
        except ArchiveError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        labeled.append((label, archive_entry.report))

    if not labeled:
        print("No archives provided.", file=sys.stderr)
        return 2

    report = build_evolution(labeled)
    print(format_evolution_report(report))
    return 0
