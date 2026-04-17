"""Tests for the tag subcommand handler."""

import json
import pytest
from unittest.mock import patch, MagicMock
from argparse import Namespace

from batchmark.tag_command import run_tag_command
from batchmark.tagger import TagEntry


SAMPLE_TAG = TagEntry(
    name="v1.0",
    branch="main",
    created_at="2024-01-01T00:00:00",
    results=[],
    meta={"note": "baseline release"},
)


@pytest.fixture
def tag_dir(tmp_path):
    return tmp_path / "tags"


def _args(**kwargs):
    defaults = {
        "tag_action": None,
        "tag_name": None,
        "branch": None,
        "config": "batchmark.toml",
        "meta": None,
        "tag_dir": None,
    }
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_run_tag_list_empty(tag_dir, capsys):
    with patch("batchmark.tag_command.list_tags", return_value=[]):
        with patch("batchmark.tag_command.format_tag_list", return_value="no tags"):
            run_tag_command(_args(tag_action="list", tag_dir=str(tag_dir)))
    captured = capsys.readouterr()
    assert "no tags" in captured.out


def test_run_tag_list_shows_names(tag_dir, capsys):
    with patch("batchmark.tag_command.list_tags", return_value=["v1.0", "v2.0"]):
        with patch("batchmark.tag_command.format_tag_list", return_value="v1.0\nv2.0") as fmt:
            run_tag_command(_args(tag_action="list", tag_dir=str(tag_dir)))
            fmt.assert_called_once_with(["v1.0", "v2.0"])
    captured = capsys.readouterr()
    assert "v1.0" in captured.out


def test_run_tag_show_prints_detail(tag_dir, capsys):
    with patch("batchmark.tag_command.load_tag", return_value=SAMPLE_TAG):
        with patch("batchmark.tag_command.format_tag_detail", return_value="detail output"):
            run_tag_command(_args(tag_action="show", tag_name="v1.0", tag_dir=str(tag_dir)))
    captured = capsys.readouterr()
    assert "detail output" in captured.out


def test_run_tag_show_missing_name_exits(tag_dir, capsys):
    with pytest.raises(SystemExit) as exc:
        run_tag_command(_args(tag_action="show", tag_name=None, tag_dir=str(tag_dir)))
    assert exc.value.code != 0


def test_run_tag_delete_removes_tag(tag_dir):
    with patch("batchmark.tag_command.tag_path") as mock_path:
        mock_file = MagicMock()
        mock_path.return_value = mock_file
        mock_file.exists.return_value = True
        run_tag_command(_args(tag_action="delete", tag_name="v1.0", tag_dir=str(tag_dir)))
        mock_file.unlink.assert_called_once()


def test_run_tag_delete_missing_name_exits(tag_dir):
    with pytest.raises(SystemExit) as exc:
        run_tag_command(_args(tag_action="delete", tag_name=None, tag_dir=str(tag_dir)))
    assert exc.value.code != 0


def test_run_tag_unknown_action_exits(tag_dir):
    with pytest.raises(SystemExit) as exc:
        run_tag_command(_args(tag_action="explode", tag_dir=str(tag_dir)))
    assert exc.value.code != 0
