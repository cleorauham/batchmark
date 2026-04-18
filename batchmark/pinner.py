"""Pin a benchmark result as a named reference point for future comparisons."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

from batchmark.runner import BenchmarkResult


class PinError(Exception):
    pass


@dataclass
class PinEntry:
    name: str
    branch: str
    suite: str
    duration: float
    passed: bool
    note: Optional[str] = None


def pin_path(store: Path, name: str) -> Path:
    return store / f"{name}.pin.json"


def save_pin(store: Path, name: str, result: BenchmarkResult, note: Optional[str] = None) -> Path:
    store.mkdir(parents=True, exist_ok=True)
    entry = PinEntry(
        name=name,
        branch=result.branch,
        suite=result.suite,
        duration=result.duration,
        passed=result.passed,
        note=note,
    )
    path = pin_path(store, name)
    path.write_text(json.dumps(asdict(entry), indent=2))
    return path


def load_pin(store: Path, name: str) -> PinEntry:
    path = pin_path(store, name)
    if not path.exists():
        raise PinError(f"Pin '{name}' not found.")
    data = json.loads(path.read_text())
    return PinEntry(**data)


def list_pins(store: Path) -> List[str]:
    if not store.exists():
        return []
    return sorted(p.stem.replace(".pin", "") for p in store.glob("*.pin.json"))


def delete_pin(store: Path, name: str) -> None:
    path = pin_path(store, name)
    if not path.exists():
        raise PinError(f"Pin '{name}' not found.")
    path.unlink()
