"""CLI subcommand for classifying cached/archived benchmark results."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from batchmark.classifier import classify, ClassifierError
from batchmark.classifier_formatter import format_classify_report


def add_classifier_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "classify",
        help="Classify benchmark results into performance tiers",
    )
    p.add_argument("input", help="JSON file containing benchmark results")
    p.add_argument("--fast", type=float, default=0.5, metavar="S",
                   help="Upper bound (seconds) for 'fast' tier (default: 0.5)")
    p.add_argument("--moderate", type=float, default=2.0, metavar="S",
                   help="Upper bound (seconds) for 'moderate' tier (default: 2.0)")
    p.add_argument("--slow", type=float, default=10.0, metavar="S",
                   help="Upper bound (seconds) for 'slow' tier (default: 10.0)")
    p.add_argument("--no-color", action="store_true", help="Disable colored output")
    p.set_defaults(func=run_classifier_command)


class _FlatResult:
    """Minimal duck-type shim for results loaded from JSON."""
    __slots__ = ("suite", "branch", "duration", "success")

    def __init__(self, suite: str, branch: str, duration: float, success: bool):
        self.suite = suite
        self.branch = branch
        self.duration = duration
        self.success = success


def run_classifier_command(args: argparse.Namespace) -> int:
    try:
        with open(args.input) as fh:
            raw: List[dict] = json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {args.input}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON — {exc}", file=sys.stderr)
        return 1

    results = [
        _FlatResult(
            suite=r.get("suite", ""),
            branch=r.get("branch", ""),
            duration=float(r.get("duration", 0.0)),
            success=bool(r.get("success", True)),
        )
        for r in raw
    ]

    thresholds = {"fast": args.fast, "moderate": args.moderate, "slow": args.slow}
    try:
        report = classify(results, thresholds=thresholds)
    except ClassifierError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(format_classify_report(report, color=not args.no_color))
    return 0
