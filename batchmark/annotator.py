"""Attach free-form annotations to benchmark runs."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class AnnotationError(Exception):
    pass


@dataclass
class Annotation:
    suite: str
    branch: str
    note: str
    tags: list[str] = field(default_factory=list)


def annotation_path(store_dir: str, suite: str, branch: str) -> Path:
    safe = branch.replace("/", "__")
    return Path(store_dir) / f"{suite}__{safe}.annotation.json"


def save_annotation(store_dir: str, annotation: Annotation) -> Path:
    path = annotation_path(store_dir, annotation.suite, annotation.branch)
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w") as f:
        json.dump({"suite": annotation.suite, "branch": annotation.branch,
                   "note": annotation.note, "tags": annotation.tags}, f, indent=2)
    return path


def load_annotation(store_dir: str, suite: str, branch: str) -> Annotation:
    path = annotation_path(store_dir, suite, branch)
    if not path.exists():
        raise AnnotationError(f"No annotation found for {suite}@{branch}")
    with open(path) as f:
        data = json.load(f)
    return Annotation(**data)


def list_annotations(store_dir: str) -> list[Annotation]:
    base = Path(store_dir)
    if not base.exists():
        return []
    results = []
    for p in sorted(base.glob("*.annotation.json")):
        with open(p) as f:
            data = json.load(f)
        results.append(Annotation(**data))
    return results


def delete_annotation(store_dir: str, suite: str, branch: str) -> bool:
    path = annotation_path(store_dir, suite, branch)
    if path.exists():
        path.unlink()
        return True
    return False
