"""Baseline management: save and load benchmark results as a named baseline."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from batchmark.runner import BenchmarkResult

DEFAULT_BASELINE_DIR = ".batchmark/baselines"


class BaselineError(Exception):
    pass


def baseline_path(name: str, directory: str = DEFAULT_BASELINE_DIR) -> Path:
    return Path(directory) / f"{name}.json"


def save_baseline(
    results: list[BenchmarkResult],
    name: str,
    directory: str = DEFAULT_BASELINE_DIR,
) -> Path:
    """Persist a list of BenchmarkResult objects under *name*."""
    path = baseline_path(name, directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "suite": r.suite,
            "branch": r.branch,
            "duration": r.duration,
            "success": r.success,
            "error": r.error,
        }
        for r in results
    ]
    path.write_text(json.dumps(payload, indent=2))
    return path


def load_baseline(
    name: str,
    directory: str = DEFAULT_BASELINE_DIR,
) -> list[BenchmarkResult]:
    """Load a previously saved baseline by name."""
    path = baseline_path(name, directory)
    if not path.exists():
        raise BaselineError(f"Baseline '{name}' not found at {path}")
    raw = json.loads(path.read_text())
    return [
        BenchmarkResult(
            suite=entry["suite"],
            branch=entry["branch"],
            duration=entry["duration"],
            success=entry["success"],
            error=entry.get("error"),
        )
        for entry in raw
    ]


def list_baselines(directory: str = DEFAULT_BASELINE_DIR) -> list[str]:
    """Return names of all saved baselines."""
    d = Path(directory)
    if not d.exists():
        return []
    return [p.stem for p in sorted(d.glob("*.json"))]
