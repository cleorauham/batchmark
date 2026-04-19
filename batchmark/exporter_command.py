from __future__ import annotations

import argparse
import sys
from pathlib import Path

from batchmark.archiver import load_archive, ArchiveError
from batchmark.serializer import report_to_dict
from batchmark.exporter import export_report


def add_exporter_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("export", help="Export a stored archive to JSON or CSV")
    p.add_argument("name", help="Archive name to export")
    p.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        dest="fmt",
        help="Output format (default: json)",
    )
    p.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output file path (default: stdout)",
    )
    p.add_argument(
        "--store",
        default=".batchmark/archives",
        help="Archive store directory",
    )


def run_exporter_command(args: argparse.Namespace) -> int:
    store = Path(args.store)
    try:
        entry = load_archive(store, args.name)
    except ArchiveError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    report = entry.report
    output = export_report(report, fmt=args.fmt)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Exported '{args.name}' to {args.output} ({args.fmt})")
    else:
        print(output)

    return 0
