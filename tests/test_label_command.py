import argparse
import pytest
from pathlib import Path
from batchmark.label_command import add_label_subparser, run_label_command
from batchmark.labeler import save_label, LabelEntry


@pytest.fixture
def store(tmp_path):
    return tmp_path / "labels"


def _args(store, *argv):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    add_label_subparser(sub)
    ns = parser.parse_args(["label"] + list(argv))
    return ns


def test_add_label_returns_0(store):
    ns = _args(store, "add", "run42", "fast", "stable", "--note", "good run")
    assert run_label_command(ns, store_dir=store) == 0


def test_show_label(store, capsys):
    save_label(store, LabelEntry(run_id="r1", labels=["alpha"], note="first"))
    ns = _args(store, "show", "r1")
    rc = run_label_command(ns, store_dir=store)
    assert rc == 0
    out = capsys.readouterr().out
    assert "r1" in out
    assert "alpha" in out


def test_show_missing_returns_1(store):
    ns = _args(store, "show", "missing")
    assert run_label_command(ns, store_dir=store) == 1


def test_list_empty(store, capsys):
    ns = _args(store, "list")
    rc = run_label_command(ns, store_dir=store)
    assert rc == 0
    assert "No labels" in capsys.readouterr().out


def test_remove_existing(store):
    save_label(store, LabelEntry(run_id="r2", labels=[]))
    ns = _args(store, "remove", "r2")
    assert run_label_command(ns, store_dir=store) == 0


def test_remove_missing_returns_1(store):
    ns = _args(store, "remove", "ghost")
    assert run_label_command(ns, store_dir=store) == 1
