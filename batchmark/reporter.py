"""High-level reporter: runs suites on branches and emits a comparison."""
from __future__ import annotations

import sys
from typing import List, Optional

from batchmark.comparator import ComparisonReport, compare_results
from batchmark.config import BatchmarkConfig
from batchmark.formatter import format_report
from batchmark.runner import BenchmarkResult, RunnerError, run_all


def run_and_compare(
    config: BatchmarkConfig,
    baseline_branch: Optional[str] = None,
    compare_branch: Optional[str] = None,
    use_color: bool = True,
    out=None,
) -> ComparisonReport:
    """Run all suites on two branches and return a ComparisonReport."""
    if out is None:
        out = sys.stdout

    branches = config.branches
    if len(branches) < 2:
        raise ValueError("At least two branches are required for comparison.")

    base = baseline_branch or branches[0]
    cmp = compare_branch or branches[1]

    print(f"Running suites on '{base}'...", file=out)
    try:
        baseline_results: List[BenchmarkResult] = run_all(config, base)
    except RunnerError as exc:
        raise RunnerError(f"Failed on baseline branch '{base}': {exc}") from exc

    print(f"Running suites on '{cmp}'...", file=out)
    try:
        compare_results_list: List[BenchmarkResult] = run_all(config, cmp)
    except RunnerError as exc:
        raise RunnerError(f"Failed on compare branch '{cmp}': {exc}") from exc

    report = compare_results(
        baseline=baseline_results,
        compare=compare_results_list,
        baseline_branch=base,
        compare_branch=cmp,
    )

    print(format_report(report, use_color=use_color), file=out)
    return report
