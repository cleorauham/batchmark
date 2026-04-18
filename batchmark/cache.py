"""Simple result caching keyed by branch + suite + commit hash."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Optional

from batchmark.runner import BenchmarkResult

DEFAULT_CACHE_DIR = Path(".batchmark_cache")


class CacheError(Exception):
    pass


def _cache_key(branch: str, suite: str, commit: str) -> str:
    raw = f"{branch}:{suite}:{commit}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def cache_path(cache_dir: Path, branch: str, suite: str, commit: str) -> Path:
    key = _cache_key(branch, suite, commit)
    return cache_dir / f"{key}.json"


def save_result(result: BenchmarkResult, branch: str, commit: str, cache_dir: Path = DEFAULT_CACHE_DIR) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_path(cache_dir, branch, result.suite, commit)
    data = {
        "suite": result.suite,
        "branch": branch,
        "commit": commit,
        "duration": result.duration,
        "success": result.success,
        "output": result.output,
    }
    path.write_text(json.dumps(data, indent=2))
    return path


def load_result(branch: str, suite: str, commit: str, cache_dir: Path = DEFAULT_CACHE_DIR) -> Optional[BenchmarkResult]:
    path = cache_path(cache_dir, branch, suite, commit)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return BenchmarkResult(
            suite=data["suite"],
            duration=data["duration"],
            success=data["success"],
            output=data.get("output", ""),
        )
    except (KeyError, json.JSONDecodeError) as exc:
        raise CacheError(f"Corrupt cache entry {path}: {exc}") from exc


def clear_cache(cache_dir: Path = DEFAULT_CACHE_DIR) -> int:
    if not cache_dir.exists():
        return 0
    removed = 0
    for entry in cache_dir.glob("*.json"):
        entry.unlink()
        removed += 1
    return removed
