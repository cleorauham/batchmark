"""CLI sub-command: batchmark bucket."""
from __future__ import annotations

import argparse
import sys
from typing import List

from batchmark.archiver import load_archive, ArchiveError
from batchmark.bucketer import bucket_results, BucketerError
from batchmark.bucket_formatter import format_bucket_report
from batchmark.serializer import result_to_dict  # noqa: F401 – kept for symmetry


def add_bucket_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "bucket",
        help="Group benchmark results from an archive into duration buckets.",
    )
    p.add_argument("archive", help="Archive name to load results from.")
    p.add_argument("branch", help="Branch name to bucket.")
    p.add_argument(
        "--store",
        default=".batchmark/archives",
        help="Directory where archives are stored (default: .batchmark/archives).",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable terminal colours.",
    )


def run_bucket_command(args: argparse.Namespace) -> int:
    try:
        entry = load_archive(args.store, args.archive)
    except ArchiveError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    results = entry.results
    if not results:
        print("No results found in archive.", file=sys.stderr)
        return 1

    try:
        report = bucket_results(results, branch=args.branch)
    except BucketerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(format_bucket_report(report, color=not args.no_color))
    return 0
