"""Tag benchmark runs with labels for later retrieval and comparison."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TAGS_DIR = Path(".batchmark") / "tags"


class TaggerError(Exception):
    pass


@dataclass
class TagEntry:
    name: str
    branch: str
    created_at: str
    meta: dict[str, Any] = field(default_factory=dict)


def tag_path(name: Path = TAGS_DIR) -> Path:
    return base / f"{name}.json"


def save_tag(name: str, branch: str, meta: dict[str, Any] | None = None, base: Path = TAGS_DIR) -> Path:
    """Persist a tag entry to disk."""
    base.mkdir(parents=True, exist_ok=True)
    entry = TagEntry(
        name=name,
        branch=branch,
        created_at=datetime.now(timezone.utc).isoformat(),
        meta=meta or {},
    )
    path = tag_path(name, base)
    path.write_text(json.dumps(entry.__dict__, indent=2))
    return path


def load_tag(name: str, base: Path = TAGS_DIR) -> TagEntry:
    """Load a tag entry by name."""
    path = tag_path(name, base)
    if not path.exists():
        raise TaggerError(f"Tag '{name}' not found at {path}")
    data = json.loads(path.read_text())
    return TagEntry(**data)


def list_tags(base: Path = TAGS_DIR) -> list[str]:
    """Return sorted list of tag names."""
    if not base.exists():
        return []
    return sorted(p.stem for p in base.glob("*.json"))


def delete_tag(name: str, base: Path = TAGS_DIR) -> None:
    """Remove a tag entry."""
    path = tag_path(name, base)
    if not path.exists():
        raise TaggerError(f"Tag '{name}' not found")
    path.unlink()
