"""CLI sub-command wiring for notification/hook configuration."""
from __future__ import annotations
import argparse
from batchmark.notifier import Notifier, build_event, stdout_hook, threshold_hook
from batchmark.notify_formatter import format_event_summary
from batchmark.comparator import ComparisonReport


def add_notify_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("notify", help="Print notification summary for a report")
    p.add_argument("--max-regressions", type=int, default=None,
                   help="Exit non-zero if regressions exceed this value")


def run_notify_command(args: argparse.Namespace, report: ComparisonReport) -> int:
    notifier = Notifier()
    notifier.register(stdout_hook)

    if args.max_regressions is not None:
        notifier.register(threshold_hook(args.max_regressions))

    event = build_event(report)
    print(format_event_summary(event))

    try:
        notifier.notify(event)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0
