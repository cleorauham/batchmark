"""CLI sub-command: batchmark recommend."""
from __future__ import annotations

import argparse
import sys

from batchmark.archiver import load_archive
from batchmark.recommender import build_recommendations
from batchmark.recommender_formatter import format_recommendation_report


def add_recommender_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "recommend",
        help="Suggest branches/suites to investigate or promote",
    )
    p.add_argument("archive", help="Archive name to load comparison report from")
    p.add_argument(
        "--investigate-threshold",
        type=float,
        default=10.0,
        metavar="PCT",
        help="Regression %% that triggers an 'investigate' recommendation (default: 10)",
    )
    p.add_argument(
        "--promote-threshold",
        type=float,
        default=5.0,
        metavar="PCT",
        help="Improvement %% that triggers a 'promote' recommendation (default: 5)",
    )
    p.set_defaults(func=run_recommender_command)


def run_recommender_command(args: argparse.Namespace) -> int:
    try:
        entry = load_archive(args.archive)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    report = build_recommendations(
        entry.report,
        investigate_threshold=args.investigate_threshold,
        promote_threshold=-abs(args.promote_threshold),
    )
    print(format_recommendation_report(report))
    return 0
