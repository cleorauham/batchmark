"""Tests for the CLI entry point."""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from batchmark.cli import main


@pytest.fixture()
def mock_report():
    report = MagicMock()
    report.baseline_branch = "main"
    report.candidate_branch = "feature"
    report.comparisons = []
    report.regressions.return_value = []
    report.improvements.return_value = []
    return report


def test_missing_config_returns_2(tmp_path):
    result = main(["-c", str(tmp_path / "nonexistent.toml")])
    assert result == 2


def test_invalid_config_returns_2(tmp_path):
    bad = tmp_path / "bad.toml"
    bad.write_text("not valid toml [[[")
    result = main(["-c", str(bad)])
    assert result == 2


def test_successful_run_returns_0(tmp_path, mock_report):
    cfg_file = tmp_path / "batchmark.toml"
    cfg_file.write_text(
        '[batchmark]\nbranches = ["main", "feature"]\n\n[[suites]]\nname = "s"\ncommand = "echo hi"\n'
    )
    with patch("batchmark.cli.run_and_compare", return_value=mock_report), \
         patch("batchmark.cli.format_report", return_value="report output"):
        result = main(["-c", str(cfg_file)])
    assert result == 0


def test_fail_on_regression_returns_1(tmp_path, mock_report):
    cfg_file = tmp_path / "batchmark.toml"
    cfg_file.write_text(
        '[batchmark]\nbranches = ["main", "feature"]\n\n[[suites]]\nname = "s"\ncommand = "echo hi"\n'
    )
    mock_report.regressions.return_value = [MagicMock()]
    with patch("batchmark.cli.run_and_compare", return_value=mock_report), \
         patch("batchmark.cli.format_report", return_value=""):
        result = main(["-c", str(cfg_file), "--fail-on-regression"])
    assert result == 1


def test_json_output(tmp_path, mock_report):
    cfg_file = tmp_path / "batchmark.toml"
    cfg_file.write_text(
        '[batchmark]\nbranches = ["main", "feature"]\n\n[[suites]]\nname = "s"\ncommand = "echo hi"\n'
    )
    with patch("batchmark.cli.run_and_compare", return_value=mock_report), \
         patch("batchmark.serializer.report_to_dict", return_value={"ok": True}), \
         patch("builtins.print") as mock_print:
        result = main(["-c", str(cfg_file), "--output", "json"])
    assert result == 0
