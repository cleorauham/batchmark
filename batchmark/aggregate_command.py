"""CLI sub-command: batchmark aggregate."""

from __future__ import annotations

import argparse
import sys
from typing import List

from batchmark.aggregator import aggregate
from batchmark.aggregate_formatter import format_aggregate_report
from batchmark.baseline import load_baseline, BaselineError
from batchmark.cache import load_result


def add_aggregate_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "aggregate",
        help="Aggregate benchmark results from a baseline into statistics.",
    )
    p.add_argument("name", help="Baseline name to aggregate.")
    p.add_argument(
        "--store",
        default=".batchmark",
        metavar="DIR",
        help="Storage directory (default: .batchmark).",
    )
    p.set_defaults(func=run_aggregate_command)


def run_aggregate_command(args: argparse.Namespace) -> int:
    store = args.store
    name = args.name
    try:
        entry = load_baseline(store, name)
    except BaselineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    results = entry.results
    if not results:
        print(f"Baseline '{name}' contains no results.", file=sys.stderr)
        return 1

    report = aggregate(results)
    print(format_aggregate_report(report))
    return 0
