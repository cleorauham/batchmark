"""Tests for batchmark.formatter."""
from batchmark.comparator import ComparisonReport, SuiteComparison
from batchmark.formatter import format_report


def _make_report(comparisons=None):
    return ComparisonReport(
        baseline_branch="main",
        compare_branch="feature",
        comparisons=comparisons or [],
    )


def test_format_report_contains_branches():
    report = _make_report()
    output = format_report(report, use_color=False)
    assert "main" in output
    assert "feature" in output


def test_format_report_no_results():
    report = _make_report()
    output = format_report(report, use_color=False)
    assert "No comparable results found" in output


def test_format_report_shows_suite_name():
    c = SuiteComparison(
        suite_name="my_suite",
        baseline_branch="main",
        compare_branch="feature",
        baseline_duration=2.0,
        compare_duration=1.5,
        delta_pct=-25.0,
        improved=True,
    )
    report = _make_report([c])
    output = format_report(report, use_color=False)
    assert "my_suite" in output
    assert "-25.00%" in output


def test_format_report_summary_counts():
    imp = SuiteComparison("a", "main", "f", 1.0, 0.8, -20.0, True)
    reg = SuiteComparison("b", "main", "f", 1.0, 1.3, 30.0, False)
    report = _make_report([imp, reg])
    output = format_report(report, use_color=False)
    assert "1 improvement(s)" in output
    assert "1 regression(s)" in output
