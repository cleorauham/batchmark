"""Tests for batchmark.snapshot_command."""
from __future__ import annotations

import argparse
import pytest

from batchmark.snapshot_command import run_snapshot_command


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path / "snaps")


def _args(action, name=None, store=None):
    ns = argparse.Namespace(action=action, name=name, store=store or ".batchmark/snapshots")
    return ns


class _FakeReport:
    branches = ["main"]
    comparisons = []


import batchmark.snapshotter as _mod


@pytest.fixture(autouse=True)
def patch_serial(monkeypatch):
    monkeypatch.setattr(_mod, "report_to_dict", lambda r: {"comparisons": [], "branches": r.branches})


def test_list_empty(store, capsys):
    rc = run_snapshot_command(_args("list", store=store))
    assert rc == 0
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_save_and_list(store, capsys):
    report = _FakeReport()
    rc = run_snapshot_command(_args("save", name="s1", store=store), report=report)
    assert rc == 0
    run_snapshot_command(_args("list", store=store))
    out = capsys.readouterr().out
    assert "s1" in out


def test_save_no_name_returns_2(store):
    rc = run_snapshot_command(_args("save", store=store), report=_FakeReport())
    assert rc == 2


def test_show_missing_returns_1(store):
    rc = run_snapshot_command(_args("show", name="ghost", store=store))
    assert rc == 1


def test_delete_then_list_empty(store, capsys):
    report = _FakeReport()
    run_snapshot_command(_args("save", name="tmp", store=store), report=report)
    rc = run_snapshot_command(_args("delete", name="tmp", store=store))
    assert rc == 0
    run_snapshot_command(_args("list", store=store))
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_show_prints_detail(store, capsys):
    report = _FakeReport()
    run_snapshot_command(_args("save", name="detail", store=store), report=report)
    rc = run_snapshot_command(_args("show", name="detail", store=store))
    assert rc == 0
    out = capsys.readouterr().out
    assert "detail" in out
