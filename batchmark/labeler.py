"""Attach and retrieve labels (free-form tags) on benchmark runs."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class LabelError(Exception):
    pass


@dataclass
class LabelEntry:
    run_id: str
    labels: List[str] = field(default_factory=list)
    note: Optional[str] = None


def label_path(store_dir: Path, run_id: str) -> Path:
    return store_dir / f"{run_id}.label.json"


def save_label(store_dir: Path, entry: LabelEntry) -> Path:
    store_dir.mkdir(parents=True, exist_ok=True)
    path = label_path(store_dir, entry.run_id)
    path.write_text(json.dumps({
        "run_id": entry.run_id,
        "labels": entry.labels,
        "note": entry.note,
    }, indent=2))
    return path


def load_label(store_dir: Path, run_id: str) -> LabelEntry:
    path = label_path(store_dir, run_id)
    if not path.exists():
        raise LabelError(f"No label found for run '{run_id}'")
    data = json.loads(path.read_text())
    return LabelEntry(run_id=data["run_id"], labels=data["labels"], note=data.get("note"))


def list_labels(store_dir: Path) -> List[LabelEntry]:
    if not store_dir.exists():
        return []
    entries = []
    for p in sorted(store_dir.glob("*.label.json")):
        data = json.loads(p.read_text())
        entries.append(LabelEntry(run_id=data["run_id"], labels=data["labels"], note=data.get("note")))
    return entries


def delete_label(store_dir: Path, run_id: str) -> bool:
    path = label_path(store_dir, run_id)
    if path.exists():
        path.unlink()
        return True
    return False
