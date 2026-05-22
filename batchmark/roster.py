"""Roster: track which branches and suites have been seen across runs."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set


class RosterError(Exception):
    pass


@dataclass
class RosterEntry:
    branch: str
    suites: List[str] = field(default_factory=list)

    def add_suite(self, name: str) -> None:
        if name not in self.suites:
            self.suites.append(name)


@dataclass
class Roster:
    entries: Dict[str, RosterEntry] = field(default_factory=dict)

    @property
    def branches(self) -> List[str]:
        return sorted(self.entries.keys())

    @property
    def all_suites(self) -> List[str]:
        seen: Set[str] = set()
        for entry in self.entries.values():
            seen.update(entry.suites)
        return sorted(seen)

    def register(self, branch: str, suite: str) -> None:
        if branch not in self.entries:
            self.entries[branch] = RosterEntry(branch=branch)
        self.entries[branch].add_suite(suite)

    def suites_for(self, branch: str) -> List[str]:
        if branch not in self.entries:
            return []
        return list(self.entries[branch].suites)


def roster_path(store: Path, name: str) -> Path:
    return store / f"{name}.roster.json"


def save_roster(store: Path, name: str, roster: Roster) -> Path:
    store.mkdir(parents=True, exist_ok=True)
    path = roster_path(store, name)
    data = {
        branch: entry.suites
        for branch, entry in roster.entries.items()
    }
    path.write_text(json.dumps(data, indent=2))
    return path


def load_roster(store: Path, name: str) -> Roster:
    path = roster_path(store, name)
    if not path.exists():
        raise RosterError(f"Roster not found: {name}")
    data = json.loads(path.read_text())
    entries = {
        branch: RosterEntry(branch=branch, suites=suites)
        for branch, suites in data.items()
    }
    return Roster(entries=entries)


def list_rosters(store: Path) -> List[str]:
    if not store.exists():
        return []
    return sorted(
        p.name.removesuffix(".roster.json")
        for p in store.glob("*.roster.json")
    )


def build_roster(results: list) -> Roster:
    roster = Roster()
    for r in results:
        if getattr(r, "success", False):
            roster.register(r.branch, r.suite)
    return roster
