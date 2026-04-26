from __future__ import annotations

import argparse
import pytest
from unittest.mock import patch, MagicMock

from batchmark.scorer_command import add_scorer_subparser, run_scorer_command
from batchmark.archiver import ArchiveError


def _args(**kwargs):
    defaults = {
        "archives": ["run-001"],
        "store": ".batchmark",
        "no_color": True,
        "func": run_scorer_command,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_scorer_subparser_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_scorer_subparser(sub)
    args = parser.parse_args(["score", "run-001"])
    assert args.func is run_scorer_command


def test_run_scorer_missing_archive_returns_1(capsys):
    with patch(
        "batchmark.scorer_command.load_archive",
        side_effect=ArchiveError("not found"),
    ):
        rc = run_scorer_command(_args())
    assert rc == 1
    out = capsys.readouterr().out
    assert "error" in out


def test_run_scorer_empty_results_returns_1(capsys):
    fake_entry = MagicMock()
    fake_entry.results = []
    with patch("batchmark.scorer_command.load_archive", return_value=fake_entry):
        rc = run_scorer_command(_args())
    assert rc == 1
    out = capsys.readouterr().out
    assert "No results" in out


def test_run_scorer_prints_report(capsys):
    fake_result = MagicMock()
    fake_result.suite = "bench_a"
    fake_result.branch = "main"
    fake_result.success = True
    fake_result.duration = 1.0

    fake_entry = MagicMock()
    fake_entry.results = [fake_result]

    fake_report = MagicMock()
    fake_report.by_branch = {"main": MagicMock()}
    fake_report.best_branch = "main"

    with patch("batchmark.scorer_command.load_archive", return_value=fake_entry), \
         patch("batchmark.scorer_command.build_score_report", return_value=fake_report), \
         patch("batchmark.scorer_command.format_score_report", return_value="SCORE OUTPUT"):
        rc = run_scorer_command(_args())

    assert rc == 0
    out = capsys.readouterr().out
    assert "SCORE OUTPUT" in out


def test_run_scorer_multiple_archives_merged(capsys):
    r1 = MagicMock(suite="a", branch="main", success=True, duration=1.0)
    r2 = MagicMock(suite="b", branch="dev", success=True, duration=2.0)

    e1 = MagicMock(results=[r1])
    e2 = MagicMock(results=[r2])

    captured_results = []

    def fake_build(results):
        captured_results.extend(results)
        return MagicMock(by_branch={"main": MagicMock()}, best_branch="main")

    with patch("batchmark.scorer_command.load_archive", side_effect=[e1, e2]), \
         patch("batchmark.scorer_command.build_score_report", side_effect=fake_build), \
         patch("batchmark.scorer_command.format_score_report", return_value="OK"):
        rc = run_scorer_command(_args(archives=["run-001", "run-002"]))

    assert rc == 0
    assert len(captured_results) == 2
