"""Tests for batchmark.exporter."""

import json
import pytest

from batchmark.comparator import ComparisonReport, SuiteComparison
from batchmark.runner import BenchmarkResult
from batchmark.exporter import export_report


def _result(branch: str, mean: float, ok: bool = True) -> BenchmarkResult:
    r = BenchmarkResult(suite="suite_a", branch=branch, mean=mean, stddev=0.01, iterations=10)
    r._ok = ok  # type: ignore[attr-defined]
    return r


@pytest.fixture()
def report() -> ComparisonReport:
    baseline = _result("main", 1.0)
    candidate = _result("feature", 1.2)
    sc = SuiteComparison(suite_name="suite_a", baseline=baseline, candidate=candidate)
    return ComparisonReport(
        baseline_branch="main",
        candidate_branch="feature",
        comparisons=[sc],
    )


def test_export_json_is_valid(report):
    out = export_report(report, "json")
    data = json.loads(out)
    assert data["baseline_branch"] == "main"
    assert data["candidate_branch"] == "feature"
    assert "comparisons" in data


def test_export_json_contains_suite(report):
    out = export_report(report, "json")
    data = json.loads(out)
    names = [c["suite_name"] for c in data["comparisons"]]
    assert "suite_a" in names


def test_export_csv_header(report):
    out = export_report(report, "csv")
    first_line = out.splitlines()[0]
    assert "suite" in first_line
    assert "delta_pct" in first_line


def test_export_csv_row_count(report):
    out = export_report(report, "csv")
    lines = [l for l in out.splitlines() if l.strip()]
    assert len(lines) == 2  # header + 1 data row


def test_export_unsupported_format_raises(report):
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_report(report, "xml")  # type: ignore[arg-type]
