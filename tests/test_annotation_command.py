import argparse
import pytest
from batchmark.annotation_command import add_annotation_subparser, run_annotation_command


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "ann")


def _args(**kwargs):
    base = {"annotation_cmd": None}
    base.update(kwargs)
    ns = argparse.Namespace(**base)
    return ns


def test_add_annotation_returns_0(store):
    args = _args(annotation_cmd="add", suite="s", branch="main", note="hi", tags=[])
    assert run_annotation_command(args, store) == 0


def test_show_annotation(store, capsys):
    add_args = _args(annotation_cmd="add", suite="s", branch="main", note="great", tags=["v1"])
    run_annotation_command(add_args, store)
    show_args = _args(annotation_cmd="show", suite="s", branch="main")
    rc = run_annotation_command(show_args, store)
    out = capsys.readouterr().out
    assert rc == 0
    assert "great" in out


def test_show_missing_returns_1(store):
    args = _args(annotation_cmd="show", suite="nope", branch="main")
    assert run_annotation_command(args, store) == 1


def test_list_empty(store, capsys):
    args = _args(annotation_cmd="list")
    run_annotation_command(args, store)
    out = capsys.readouterr().out
    assert "No annotations" in out


def test_delete_existing(store):
    add_args = _args(annotation_cmd="add", suite="s", branch="dev", note="x", tags=[])
    run_annotation_command(add_args, store)
    del_args = _args(annotation_cmd="delete", suite="s", branch="dev")
    assert run_annotation_command(del_args, store) == 0


def test_no_subcommand_returns_1(store):
    args = _args(annotation_cmd=None)
    assert run_annotation_command(args, store) == 1


def test_add_annotation_subparser_registers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_annotation_subparser(sub)
    ns = parser.parse_args(["annotate", "list"])
    assert ns.annotation_cmd == "list"
