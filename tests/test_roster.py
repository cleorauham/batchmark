"""Tests for batchmark.roster."""
from __future__ import annotations

import pytest
from pathlib import Path

from batchmark.roster import (
    Roster,
    RosterEntry,
    RosterError,
    build_roster,
    list_rosters,
    load_roster,
    save_roster,
)


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "rosters"


class _FakeResult:
    def __init__(self, branch: str, suite: str, success: bool = True):
        self.branch = branch
        self.suite = suite
        self.success = success


def test_save_creates_file(store: Path) -> None:
    r = Roster()
    r.register("main", "bench_a")
    path = save_roster(store, "my-roster", r)
    assert path.exists()


def test_save_and_load_roundtrip(store: Path) -> None:
    r = Roster()
    r.register("main", "bench_a")
    r.register("main", "bench_b")
    r.register("dev", "bench_a")
    save_roster(store, "roundtrip", r)
    loaded = load_roster(store, "roundtrip")
    assert set(loaded.branches) == {"main", "dev"}
    assert set(loaded.suites_for("main")) == {"bench_a", "bench_b"}
    assert loaded.suites_for("dev") == ["bench_a"]


def test_load_missing_raises(store: Path) -> None:
    with pytest.raises(RosterError):
        load_roster(store, "ghost")


def test_list_empty(store: Path) -> None:
    assert list_rosters(store) == []


def test_list_shows_saved(store: Path) -> None:
    r = Roster()
    save_roster(store, "alpha", r)
    save_roster(store, "beta", r)
    names = list_rosters(store)
    assert "alpha" in names
    assert "beta" in names


def test_build_roster_from_results() -> None:
    results = [
        _FakeResult("main", "bench_a", success=True),
        _FakeResult("main", "bench_b", success=False),
        _FakeResult("dev", "bench_a", success=True),
    ]
    roster = build_roster(results)
    assert "main" in roster.branches
    assert "dev" in roster.branches
    assert "bench_a" in roster.suites_for("main")
    assert "bench_b" not in roster.suites_for("main")  # failed excluded


def test_all_suites_deduplicates() -> None:
    r = Roster()
    r.register("main", "bench_a")
    r.register("dev", "bench_a")
    r.register("dev", "bench_b")
    assert sorted(r.all_suites) == ["bench_a", "bench_b"]


def test_suites_for_missing_branch() -> None:
    r = Roster()
    assert r.suites_for("nonexistent") == []
