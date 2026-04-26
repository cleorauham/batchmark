import pytest
from batchmark.runner import BenchmarkResult
from batchmark.comparator import SuiteComparison, ComparisonReport
from batchmark.summarizer import summarize_report, summary_counts, SuiteSummaryRow
from batchmark.summary_formatter import format_summary


def _result(elapsed: float, success: bool = True) -> BenchmarkResult:
    return BenchmarkResult(suite="s", branch="b", elapsed=elapsed, success=success, output="")


def _report(*comparisons) -> ComparisonReport:
    return ComparisonReport(baseline="main", candidate="feature", comparisons=list(comparisons))


def _cmp(suite, baseline_times, candidate_times) -> SuiteComparison:
    return SuiteComparison(
        suite=suite,
        baseline_results=[_result(t) for t in baseline_times],
        candidate_results=[_result(t) for t in candidate_times],
    )


def test_summarize_improvement():
    report = _report(_cmp("fast", [1.0, 1.0], [0.5, 0.5]))
    rows = summarize_report(report)
    assert len(rows) == 1
    assert rows[0].verdict == "improved"
    assert rows[0].delta_pct == pytest.approx(-50.0)


def test_summarize_regression():
    report = _report(_cmp("slow", [1.0], [1.2]))
    rows = summarize_report(report)
    assert rows[0].verdict == "regressed"
    assert rows[0].delta_pct == pytest.approx(20.0)


def test_summarize_unchanged():
    report = _report(_cmp("same", [1.0], [1.01]))
    rows = summarize_report(report, threshold=5.0)
    assert rows[0].verdict == "unchanged"


def test_summarize_missing_candidate():
    report = _report(_cmp("gone", [1.0], []))
    rows = summarize_report(report)
    assert rows[0].verdict == "missing"
    assert rows[0].delta_pct is None


def test_failed_results_excluded():
    cmp = SuiteComparison(
        suite="x",
        baseline_results=[_result(1.0), _result(99.0, success=False)],
        candidate_results=[_result(1.0)],
    )
    rows = summarize_report(_report(cmp))
    assert rows[0].baseline_mean == pytest.approx(1.0)


def test_summary_counts():
    rows = [
        SuiteSummaryRow("a", 1.0, 0.5, -50.0, "improved"),
        SuiteSummaryRow("b", 1.0, 1.2, 20.0, "regressed"),
        SuiteSummaryRow("c", 1.0, 1.0, 0.0, "unchanged"),
    ]
    counts = summary_counts(rows)
    assert counts["improved"] == 1
    assert counts["regressed"] == 1
    assert counts["unchanged"] == 1


def test_summary_counts_missing():
    """Ensure 'missing' verdict is counted correctly alongside other verdicts."""
    rows = [
        SuiteSummaryRow("a", 1.0, None, None, "missing"),
        SuiteSummaryRow("b", 1.0, 0.5, -50.0, "improved"),
        SuiteSummaryRow("c", 1.0, None, None, "missing"),
    ]
    counts = summary_counts(rows)
    assert counts["missing"] == 2
    assert counts["improved"] == 1
    assert counts.get("regressed", 0) == 0


def test_format_summary_contains_suite_name():
    rows = [SuiteSummaryRow("mybench", 1.0, 0.8, -20.0, "improved")]
    output = format_summary(rows, color=False)
    assert "mybench" in output
    assert "improved" in output.lower()


def test_format_summary_no_color():
    rows = [SuiteSummaryRow("s", 1.0, 1.1, 10.0, "regressed")]
    output = format_summary(rows, color=False)
    assert "\033[" not in output
