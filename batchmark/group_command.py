"""CLI subcommand for grouping benchmark results."""
from __future__ import annotations
import argparse
from batchmark.grouper import group_by_prefix, group_by_branch
from batchmark.group_formatter import format_group_report


def add_group_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("group", help="Group benchmark comparisons")
    p.add_argument("--by", choices=["prefix", "branch"], default="prefix",
                   help="Grouping strategy (default: prefix)")
    p.add_argument("--sep", default="_",
                   help="Separator for prefix grouping (default: '_')")
    p.set_defaults(func=run_group_command)


def run_group_command(args: argparse.Namespace, report) -> int:
    """Run the group command given a ComparisonReport."""
    if args.by == "branch":
        grp_report = group_by_branch(report)
    else:
        grp_report = group_by_prefix(report, sep=args.sep)

    print(format_group_report(grp_report))
    return 0
