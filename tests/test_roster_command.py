"""Tests for batchmark.roster_command."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from batchmark.roster import Roster, save_roster
from batchmark.roster_command import add_roster_subparser, run_roster_command


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "rosters"


def _args(store: Path, **kwargs) -> argparse.Namespace:
    base = {"store": str(store), "roster_cmd": None}
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_add_roster_subparser_registers_command() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    add_roster_subparser(sub)
    parsed = parser.parse_args(["roster", "list"])
    assert parsed.cmd == "roster"


def test_list_empty(store: Path, capsys) -> None:
    args = _args(store, roster_cmd="list")
    rc = run_roster_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "no rosters" in out.lower()


def test_list_shows_names(store: Path, capsys) -> None:
    r = Roster()
    r.register("main", "bench_a")
    save_roster(store, "my-roster", r)
    args = _args(store, roster_cmd="list")
    run_roster_command(args)
    out = capsys.readouterr().out
    assert "my-roster" in out


def test_show_prints_detail(store: Path, capsys) -> None:
    r = Roster()
    r.register("main", "bench_x")
    save_roster(store, "detail-test", r)
    args = _args(store, roster_cmd="show", name="detail-test")
    rc = run_roster_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "main" in out
    assert "bench_x" in out


def test_show_missing_returns_1(store: Path, capsys) -> None:
    args = _args(store, roster_cmd="show", name="ghost")
    rc = run_roster_command(args)
    assert rc == 1
    out = capsys.readouterr().out
    assert "Error" in out


def test_no_subcommand_returns_1(store: Path, capsys) -> None:
    args = _args(store, roster_cmd=None)
    rc = run_roster_command(args)
    assert rc == 1
