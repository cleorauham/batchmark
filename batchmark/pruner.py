"""Prune old baselines, tags, or archives by age or count."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


class PrunerError(Exception):
    pass


@dataclass
class PruneResult:
    removed: List[str]
    kept: int

    @property
    def total_removed(self) -> int:
        return len(self.removed)


def _sorted_by_mtime(directory: Path) -> List[Path]:
    files = [f for f in directory.iterdir() if f.is_file() and f.suffix == ".json"]
    return sorted(files, key=lambda f: f.stat().st_mtime)


def prune_by_count(directory: Path, keep: int, dry_run: bool = False) -> PruneResult:
    """Remove oldest files so that only `keep` remain."""
    if keep < 1:
        raise PrunerError(f"keep must be >= 1, got {keep}")
    if not directory.exists():
        return PruneResult(removed=[], kept=0)

    files = _sorted_by_mtime(directory)
    to_remove = files[: max(0, len(files) - keep)]

    removed = []
    for f in to_remove:
        removed.append(f.name)
        if not dry_run:
            f.unlink()

    return PruneResult(removed=removed, kept=len(files) - len(to_remove))


def prune_by_age(directory: Path, max_age_days: float, dry_run: bool = False) -> PruneResult:
    """Remove files older than `max_age_days` days."""
    import time

    if not directory.exists():
        return PruneResult(removed=[], kept=0)

    cutoff = time.time() - max_age_days * 86400
    files = _sorted_by_mtime(directory)
    removed = []
    kept = 0
    for f in files:
        if f.stat().st_mtime < cutoff:
            removed.append(f.name)
            if not dry_run:
                f.unlink()
        else:
            kept += 1

    return PruneResult(removed=removed, kept=kept)
