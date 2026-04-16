"""CLI entry point for batchmark."""
import argparse
import sys
from pathlib import Path

from batchmark.config import from_file
from batchmark.reporter import run_and_compare
from batchmark.formatter import format_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="batchmark",
        description="Run and compare benchmark suites across git branches.",
    )
    parser.add_argument(
        "-c",
        "--config",
        default="batchmark.toml",
        help="Path to config file (default: batchmark.toml)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit with code 1 if any regressions are found",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file '{config_path}' not found.", file=sys.stderr)
        return 2

    try:
        config = from_file(config_path)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 2

    try:
        report = run_and_compare(config)
    except Exception as exc:  # noqa: BLE001
        print(f"Error running benchmarks: {exc}", file=sys.stderr)
        return 2

    if args.output == "json":
        import json
        from batchmark.serializer import report_to_dict
        print(json.dumps(report_to_dict(report), indent=2))
    else:
        print(format_report(report, color=not args.no_color))

    if args.fail_on_regression and report.regressions():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
