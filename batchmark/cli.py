"""CLI entry point for batchmark."""

from __future__ import annotations

import argparse
import sys

from batchmark.config import from_file, BatchmarkConfigError
from batchmark.reporter import run_and_compare
from batchmark.formatter import format_report
from batchmark.exporter import export_report
from batchmark.filter import filter_suites, filter_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="batchmark",
        description="Run and compare benchmark suites across git branches.",
    )
    parser.add_argument("-c", "--config", default="batchmark.toml", help="Path to config file.")
    parser.add_argument("--fail-on-regression", action="store_true", help="Exit 1 if regressions found.")
    parser.add_argument("--export", choices=["json", "csv"], help="Export results in given format.")
    parser.add_argument("--export-file", default="batchmark_results", help="Export filename (no extension).")
    parser.add_argument("--include", nargs="+", metavar="SUITE", help="Only run these suites.")
    parser.add_argument("--exclude", nargs="+", metavar="SUITE", help="Skip these suites.")
    parser.add_argument("--only-regressions", action="store_true", help="Show only regressions in output.")
    parser.add_argument("--only-improvements", action="store_true", help="Show only improvements in output.")
    parser.add_argument("--min-delta-pct", type=float, default=0.0, help="Minimum absolute delta %% to show.")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = from_file(args.config)
    except FileNotFoundError:
        print(f"Error: config file '{args.config}' not found.", file=sys.stderr)
        return 2
    except BatchmarkConfigError as exc:
        print(f"Error: invalid config — {exc}", file=sys.stderr)
        return 2

    if args.include or args.exclude:
        config.suites = filter_suites(config.suites, include=args.include, exclude=args.exclude)

    report = run_and_compare(config)

    display_report = filter_report(
        report,
        only_regressions=args.only_regressions,
        only_improvements=args.only_improvements,
        min_delta_pct=args.min_delta_pct,
    )

    print(format_report(display_report))

    if args.export:
        path = export_report(report, fmt=args.export, filename=args.export_file)
        print(f"Results exported to {path}")

    if args.fail_on_regression and report.regressions():
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
