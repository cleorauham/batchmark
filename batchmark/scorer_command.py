from __future__ import annotations

import argparse
from typing import List

from batchmark.archiver import load_archive, ArchiveError
from batchmark.scorer import build_score_report
from batchmark.score_formatter import format_score_report


def add_scorer_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "score",
        help="Score branches based on benchmark results from one or more archives",
    )
    p.add_argument(
        "archives",
        nargs="+",
        metavar="ARCHIVE",
        help="Archive names to load results from",
    )
    p.add_argument(
        "--store",
        default=".batchmark",
        metavar="DIR",
        help="Storage directory (default: .batchmark)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    p.set_defaults(func=run_scorer_command)


def run_scorer_command(args: argparse.Namespace) -> int:
    all_results: List = []
    for name in args.archives:
        try:
            entry = load_archive(name, store=args.store)
        except ArchiveError as exc:
            print(f"error: {exc}")
            return 1
        all_results.extend(entry.results)

    if not all_results:
        print("No results found in the specified archives.")
        return 1

    report = build_score_report(all_results)
    color = not args.no_color
    print(format_score_report(report, color=color))
    return 0
