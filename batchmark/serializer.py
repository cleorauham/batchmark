"""JSON serialization for benchmark reports."""
from __future__ import annotations

import json
from typing import Any

from batchmark.comparator import ComparisonReport, SuiteComparison
from batchmark.runner import BenchmarkResult


def result_to_dict(result: BenchmarkResult) -> dict[str, Any]:
    return {
        "suite": result.suite,
        "branch": result.branch,
        "duration": result.duration,
        "success": result.success,
        "output": result.output,
        "error": result.error,
    }


def suite_comparison_to_dict(cmp: SuiteComparison) -> dict[str, Any]:
    return {
        "suite": cmp.suite,
        "baseline": result_to_dict(cmp.baseline) if cmp.baseline else None,
        "candidate": result_to_dict(cmp.candidate) if cmp.candidate else None,
        "delta": cmp.delta,
        "delta_pct": cmp.delta_pct,
        "summary": cmp.summary(),
    }


def report_to_dict(report: ComparisonReport) -> dict[str, Any]:
    return {
        "baseline_branch": report.baseline_branch,
        "candidate_branch": report.candidate_branch,
        "comparisons": [suite_comparison_to_dict(c) for c in report.comparisons],
        "regressions": len(report.regressions()),
        "improvements": len(report.improvements()),
    }


def report_to_json(report: ComparisonReport, indent: int = 2) -> str:
    """Serialize a ComparisonReport to a JSON string.

    Args:
        report: The comparison report to serialize.
        indent: Number of spaces for JSON indentation. Defaults to 2.

    Returns:
        A formatted JSON string representation of the report.
    """
    return json.dumps(report_to_dict(report), indent=indent)
