"""Snapshot: capture and persist a full report at a named point in time."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from batchmark.serializer import report_to_dict


class SnapshotError(Exception):
    pass


@dataclass
class SnapshotEntry:
    name: str
    created_at: str
    branches: list[str]
    data: dict[str, Any] = field(repr=False)


def snapshot_path(store_dir: str, name: str) -> str:
    return os.path.join(store_dir, f"{name}.snapshot.json")


def save_snapshot(store_dir: str, name: str, report: Any) -> str:
    os.makedirs(store_dir, exist_ok=True)
    path = snapshot_path(store_dir, name)
    entry = {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "branches": report.branches,
        "data": report_to_dict(report),
    }
    with open(path, "w") as fh:
        json.dump(entry, fh, indent=2)
    return path


def load_snapshot(store_dir: str, name: str) -> SnapshotEntry:
    path = snapshot_path(store_dir, name)
    if not os.path.exists(path):
        raise SnapshotError(f"Snapshot not found: {name!r}")
    with open(path) as fh:
        raw = json.load(fh)
    return SnapshotEntry(
        name=raw["name"],
        created_at=raw["created_at"],
        branches=raw["branches"],
        data=raw["data"],
    )


def list_snapshots(store_dir: str) -> list[str]:
    if not os.path.isdir(store_dir):
        return []
    names = []
    for fname in sorted(os.listdir(store_dir)):
        if fname.endswith(".snapshot.json"):
            names.append(fname[: -len(".snapshot.json")])
    return names


def delete_snapshot(store_dir: str, name: str) -> None:
    path = snapshot_path(store_dir, name)
    if not os.path.exists(path):
        raise SnapshotError(f"Snapshot not found: {name!r}")
    os.remove(path)
