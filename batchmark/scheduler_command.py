"""CLI sub-command: show how suites would be scheduled."""
from __future__ import annotations
import argparse
from batchmark.config import from_file, BatchmarkConfig
from batchmark.scheduler import schedule, suite_names


def add_scheduler_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("schedule", help="Preview suite scheduling batches")
    p.add_argument("--config", default="batchmark.toml", help="Config file path")
    p.add_argument(
        "--parallel", type=int, default=1, metavar="N",
        help="Max suites per batch (default: 1)"
    )


def run_scheduler_command(args: argparse.Namespace) -> int:
    try:
        cfg: BatchmarkConfig = from_file(args.config)
    except Exception as exc:
        print(f"[error] Could not load config: {exc}")
        return 2

    try:
        batches = schedule(cfg.suites, max_parallel=args.parallel)
    except Exception as exc:
        print(f"[error] Scheduling failed: {exc}")
        return 2

    if not batches:
        print("No suites to schedule.")
        return 0

    print(f"Scheduling {sum(b.size for b in batches)} suite(s) "
          f"across {len(batches)} batch(es) (parallel={args.parallel}):\n")
    for batch in batches:
        names = ", ".join(suite_names(batch))
        print(f"  Batch {batch.index + 1}: [{names}]")
    return 0
