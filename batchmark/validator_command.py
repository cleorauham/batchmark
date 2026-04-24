"""CLI sub-command: validate."""
from __future__ import annotations

import argparse
import sys
from typing import List

from batchmark.validator import ValidationRule, validate_results, validate_report
from batchmark.validator_formatter import format_validation_report
from batchmark.baseline import load_baseline, BaselineError
from batchmark.comparator import ComparisonReport


def add_validator_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("validate", help="Validate benchmark results against rules")
    p.add_argument("baseline", help="Baseline name to validate")
    p.add_argument(
        "--max-duration",
        nargs=2,
        metavar=("SUITE", "SECONDS"),
        action="append",
        default=[],
        dest="max_duration",
        help="Max allowed duration for a suite (repeatable)",
    )
    p.add_argument(
        "--max-regression",
        nargs=2,
        metavar=("SUITE", "PCT"),
        action="append",
        default=[],
        dest="max_regression",
        help="Max allowed regression %% for a suite (repeatable)",
    )
    p.add_argument("--store", default=".batchmark", help="Storage directory")


def run_validator_command(args: argparse.Namespace) -> int:
    rules: List[ValidationRule] = []

    for suite, secs in args.max_duration:
        rules.append(ValidationRule(suite=suite, max_duration=float(secs)))

    for suite, pct in args.max_regression:
        existing = next((r for r in rules if r.suite == suite), None)
        if existing:
            existing.max_regression_pct = float(pct)
        else:
            rules.append(ValidationRule(suite=suite, max_regression_pct=float(pct)))

    try:
        results = load_baseline(args.baseline, store_dir=args.store)
    except BaselineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    report = validate_results(results, rules)
    print(format_validation_report(report))
    return 0 if report.passed else 1
