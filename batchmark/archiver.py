"""Archive and retrieve full benchmark reports by name."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

DEFAULT_ARCHIVE_DIR = ".batchmark/archives"


class ArchiveError(Exception):
    pass


@dataclass
class ArchiveEntry:
    name: str
    created_at: str
    branches: List[str]
    path: Path


def archive_path(name: str, archive_dir: str = DEFAULT_ARCHIVE_DIR) -> Path:
    return Path(archive_dir) / f"{name}.json"


def save_archive(name: str, report_dict: dict, archive_dir: str = DEFAULT_ARCHIVE_DIR) -> Path:
    path = archive_path(name, archive_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "report": report_dict,
    }
    path.write_text(json.dumps(payload, indent=2))
    return path


def load_archive(name: str, archive_dir: str = DEFAULT_ARCHIVE_DIR) -> dict:
    path = archive_path(name, archive_dir)
    if not path.exists():
        raise ArchiveError(f"Archive '{name}' not found at {path}")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ArchiveError(f"Archive '{name}' contains invalid JSON: {exc}") from exc


def list_archives(archive_dir: str = DEFAULT_ARCHIVE_DIR) -> List[ArchiveEntry]:
    base = Path(archive_dir)
    if not base.exists():
        return []
    entries = []
    for p in sorted(base.glob("*.json")):
        try:
            data = json.loads(p.read_text())
            entries.append(ArchiveEntry(
                name=data.get("name", p.stem),
                created_at=data.get("created_at", ""),
                branches=data.get("report", {}).get("branches", []),
                path=p,
            ))
        except Exception:
            continue
    return entries


def delete_archive(name: str, archive_dir: str = DEFAULT_ARCHIVE_DIR) -> None:
    path = archive_path(name, archive_dir)
    if not path.exists():
        raise ArchiveError(f"Archive '{name}' not found")
    path.unlink()
