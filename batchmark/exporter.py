"""Export comparison reports to JSON or CSV formats."""

from __future__ import annotations

import csv
import json
import io
from typing import Literal

from batchmark.comparator import ComparisonReport
from batchmark.serializer import report_to_dict


ExportFormat = Literal["json", "csv"]


def export_report(report: ComparisonReport, fmt: ExportFormat) -> str:
    """Serialize *report* to the requested format and return as a string."""
    if fmt == "json":
        return _to_json(report)
    if fmt == "csv":
        return _to_csv(report)
    raise ValueError(f"Unsupported export format: {fmt!r}")


def _to_json(report: ComparisonReport) -> str:
    data = report_to_dict(report)
    return json.dumps(data, indent=2)


def _to_csv(report: ComparisonReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "suite", "benchmark",
        "baseline_branch", "baseline_mean",
        "candidate_branch", "candidate_mean",
        "delta_pct",
    ])
    for sc in report.comparisons:
        baseline_branch = report.baseline_branch
        candidate_branch = report.candidate_branch
        baseline = sc.baseline
        candidate = sc.candidate
        if baseline is None or candidate is None:
            writer.writerow([
                sc.suite_name, "",
                baseline_branch, baseline.mean if baseline else "",
                candidate_branch, candidate.mean if candidate else "",
                "",
            ])
            continue
        delta = (candidate.mean - baseline.mean) / baseline.mean * 100 if baseline.mean else ""
        writer.writerow([
            sc.suite_name, sc.suite_name,
            baseline_branch, round(baseline.mean, 6),
            candidate_branch, round(candidate.mean, 6),
            round(delta, 2) if isinstance(delta, float) else delta,
        ])
    return buf.getvalue()
