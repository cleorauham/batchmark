"""Tests for batchmark.recommender_formatter."""
from __future__ import annotations

from batchmark.recommender import Recommendation, RecommendationReport
from batchmark.recommender_formatter import format_recommendation_report


def _report(*recs: Recommendation) -> RecommendationReport:
    return RecommendationReport(recommendations=list(recs))


def test_format_empty_returns_no_recommendations():
    out = format_recommendation_report(_report())
    assert "No recommendations" in out


def test_format_shows_investigate_section():
    rec = Recommendation("investigate", "feature", "suite_a", "duration increased by 20.0%")
    out = format_recommendation_report(_report(rec))
    assert "INVESTIGATE" in out
    assert "suite_a" in out
    assert "20.0%" in out


def test_format_shows_promote_section():
    rec = Recommendation("promote", "feature", "suite_b", "duration decreased by 15.0%")
    out = format_recommendation_report(_report(rec))
    assert "PROMOTE" in out
    assert "suite_b" in out


def test_format_shows_skip_section():
    rec = Recommendation("skip", "feature", "suite_c", "missing result in one branch")
    out = format_recommendation_report(_report(rec))
    assert "SKIP" in out
    assert "suite_c" in out


def test_format_summary_counts():
    recs = [
        Recommendation("investigate", "feature", "s1", "reason"),
        Recommendation("investigate", "feature", "s2", "reason"),
        Recommendation("promote", "feature", "s3", "reason"),
    ]
    out = format_recommendation_report(_report(*recs))
    assert "investigate=" in out
    assert "promote=" in out
    assert "Total: 3" in out
