"""CLI sub-command: heatmap — render a suite × branch duration heatmap."""
from __future__ import annotations

import argparse
import sys
from typing import List

from batchmark.archiver import ArchiveError, load_archive
from batchmark.heatmap import build_heatmap
from batchmark.heatmap_formatter import format_heatmap


def add_heatmap_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("heatmap", help="Show suite × branch duration heatmap")
    p.add_argument("archive", help="Archive name to load results from")
    p.add_argument(
        "--suites",
        nargs="+",
        metavar="SUITE",
        help="Only include these suites",
    )
    p.add_argument(
        "--branches",
        nargs="+",
        metavar="BRANCH",
        help="Only include these branches",
    )


def run_heatmap_command(args: argparse.Namespace) -> int:
    try:
        entry = load_archive(args.archive)
    except ArchiveError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    results = list(entry.results)

    if getattr(args, "suites", None):
        results = [r for r in results if r.suite in args.suites]
    if getattr(args, "branches", None):
        results = [r for r in results if r.branch in args.branches]

    report = build_heatmap(results)
    print(format_heatmap(report), end="")
    return 0
