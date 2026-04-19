"""Tests for batchmark.pinner and batchmark.pin_formatter."""

import pytest
from pathlib import Path

from batchmark.pinner import (
    PinError,
    delete_pin,
    list_pins,
    load_pin,
    save_pin,
)
from batchmark.pin_formatter import format_pin_detail, format_pin_list
from batchmark.runner import BenchmarkResult


@pytest.fixture
def store(tmp_path):
    return tmp_path / "pins"


def _result(suite="bench", branch="main", duration=1.5, passed=True):
    return BenchmarkResult(suite=suite, branch=branch, duration=duration, passed=passed)


def test_save_creates_file(store):
    save_pin(store, "v1", _result())
    assert (store / "v1.pin.json").exists()


def test_save_and_load_roundtrip(store):
    save_pin(store, "v1", _result(duration=2.0, branch="dev"), note="initial")
    entry = load_pin(store, "v1")
    assert entry.name == "v1"
    assert entry.branch == "dev"
    assert entry.duration == pytest.approx(2.0)
    assert entry.note == "initial"


def test_load_missing_raises(store):
    with pytest.raises(PinError, match="not found"):
        load_pin(store, "ghost")


def test_list_pins_empty(store):
    assert list_pins(store) == []


def test_list_pins_returns_names(store):
    save_pin(store, "alpha", _result())
    save_pin(store, "beta", _result())
    assert list_pins(store) == ["alpha", "beta"]


def test_list_pins_sorted(store):
    """Pins should be returned in alphabetical order regardless of insertion order."""
    save_pin(store, "zebra", _result())
    save_pin(store, "alpha", _result())
    save_pin(store, "mango", _result())
    assert list_pins(store) == ["alpha", "mango", "zebra"]


def test_delete_pin(store):
    save_pin(store, "v1", _result())
    delete_pin(store, "v1")
    assert list_pins(store) == []


def test_delete_missing_raises(store):
    with pytest.raises(PinError):
        delete_pin(store, "nope")


def test_format_pin_list_empty():
    out = format_pin_list([])
    assert "No pins" in out


def test_format_pin_list_shows_names():
    out = format_pin_list(["v1", "v2"])
    assert "v1" in out and "v2" in out


def test_format_pin_detail_shows_fields(store):
    save_pin(store, "v1", _result(suite="mysuite", branch="feat", duration=3.14), note="hi")
    entry = load_pin(store, "v1")
    out = format_pin_detail(entry)
    assert "mysuite" in out
    assert "feat" in out
    assert "3.1400" in out
    assert "hi" in out
