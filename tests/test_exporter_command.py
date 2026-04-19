from __future__ import annotations

import json
import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from batchmark.exporter_command import add_exporter_subparser, run_exporter_command
from batchmark.archiver import ArchiveError


def _args(**kwargs):
    defaults = {
        "name": "run-1",
        "fmt": "json",
        "output": None,
        "store": ".batchmark/archives",
    }
    defaults.update(kwargs)
    ns = argparse.Namespace(**defaults)
    return ns


def _fake_report():
    report = MagicMock()
    report.branches = ["main", "dev"]
    report.comparisons = []
    return report


def _fake_entry(report):
    entry = MagicMock()
    entry.report = report
    return entry


def test_add_exporter_subparser_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_exporter_subparser(sub)
    parsed = parser.parse_args(["export", "run-1"])
    assert parsed.name == "run-1"
    assert parsed.fmt == "json"


def test_run_exporter_missing_archive_returns_1():
    with patch("batchmark.exporter_command.load_archive", side_effect=ArchiveError("not found")):
        result = run_exporter_command(_args())
    assert result == 1


def test_run_exporter_json_to_stdout(capsys):
    report = _fake_report()
    entry = _fake_entry(report)
    fake_json = '{"branches": ["main"]}'
    with patch("batchmark.exporter_command.load_archive", return_value=entry), \
         patch("batchmark.exporter_command.export_report", return_value=fake_json):
        result = run_exporter_command(_args(fmt="json"))
    assert result == 0
    captured = capsys.readouterr()
    assert fake_json in captured.out


def test_run_exporter_writes_file(tmp_path):
    report = _fake_report()
    entry = _fake_entry(report)
    out_file = tmp_path / "out.json"
    fake_json = '{"branches": ["main"]}'
    with patch("batchmark.exporter_command.load_archive", return_value=entry), \
         patch("batchmark.exporter_command.export_report", return_value=fake_json):
        result = run_exporter_command(_args(fmt="json", output=str(out_file)))
    assert result == 0
    assert out_file.exists()
    assert out_file.read_text() == fake_json


def test_run_exporter_csv_format(capsys):
    report = _fake_report()
    entry = _fake_entry(report)
    fake_csv = "suite,branch,duration\n"
    with patch("batchmark.exporter_command.load_archive", return_value=entry), \
         patch("batchmark.exporter_command.export_report", return_value=fake_csv) as mock_exp:
        result = run_exporter_command(_args(fmt="csv"))
    assert result == 0
    mock_exp.assert_called_once_with(report, fmt="csv")
