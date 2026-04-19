from __future__ import annotations

import argparse
from unittest.mock import MagicMock, patch

import pytest

from batchmark.comparer_command import add_comparer_subparser, run_comparer_command
from batchmark.archiver import ArchiveError


def _args(**kwargs):
    defaults = {
        "baseline": "run-a",
        "candidate": "run-b",
        "store": ".batchmark/archives",
        "no_color": True,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_comparer_subparser_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_comparer_subparser(sub)
    args = parser.parse_args(["compare-archives", "a", "b"])
    assert args.command == "compare-archives"
    assert args.baseline == "a"
    assert args.candidate == "b"


def test_missing_baseline_returns_1():
    with patch("batchmark.comparer_command.load_archive", side_effect=ArchiveError("nope")):
        result = run_comparer_command(_args())
    assert result == 1


def test_missing_candidate_returns_1():
    fake_entry = MagicMock()
    fake_entry.report = MagicMock()

    def _load(store, name):
        if name == "run-a":
            return fake_entry
        raise ArchiveError("missing")

    with patch("batchmark.comparer_command.load_archive", side_effect=_load):
        result = run_comparer_command(_args())
    assert result == 1


def test_successful_compare_returns_0(capsys):
    fake_entry = MagicMock()
    fake_entry.report = MagicMock()
    fake_merged = MagicMock()

    with patch("batchmark.comparer_command.load_archive", return_value=fake_entry), \
         patch("batchmark.comparer_command.merge", return_value=fake_merged), \
         patch("batchmark.comparer_command.format_merge_report", return_value="output"):
        result = run_comparer_command(_args())

    assert result == 0
    captured = capsys.readouterr()
    assert "output" in captured.out


def test_merge_error_returns_1():
    from batchmark.merger import MergeError
    fake_entry = MagicMock()
    fake_entry.report = MagicMock()

    with patch("batchmark.comparer_command.load_archive", return_value=fake_entry), \
         patch("batchmark.comparer_command.merge", side_effect=MergeError("bad")):
        result = run_comparer_command(_args())
    assert result == 1
