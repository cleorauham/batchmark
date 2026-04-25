"""CLI subcommand for segmenting benchmark results."""
from __future__ import annotations

import argparse

from batchmark.segmenter import segment_by_count, segment_by_branch, SegmentError
from batchmark.segment_formatter import format_segment_report
from batchmark.baseline import load_baseline, BaselineError


def add_segment_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("segment", help="Segment benchmark results")
    p.add_argument("baseline", help="Baseline name to segment")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--by-count",
        type=int,
        metavar="N",
        help="Split into segments of N results",
    )
    group.add_argument(
        "--by-branch",
        action="store_true",
        help="Group results by branch",
    )
    p.add_argument(
        "--baseline-dir",
        default=".batchmark/baselines",
        metavar="DIR",
    )


def run_segment_command(args: argparse.Namespace) -> int:
    try:
        results = load_baseline(args.baseline, basedir=args.baseline_dir)
    except BaselineError as exc:
        print(f"error: {exc}")
        return 1

    try:
        if args.by_branch:
            report = segment_by_branch(results)
        else:
            report = segment_by_count(results, args.by_count)
    except SegmentError as exc:
        print(f"error: {exc}")
        return 1

    print(format_segment_report(report))
    return 0
