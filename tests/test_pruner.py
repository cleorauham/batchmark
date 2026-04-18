"""Tests for batchmark.pruner."""
import json
import time
from pathlib import Path

import pytest

from batchmark.pruner import PrunerError, prune_by_age, prune_by_count


@pytest.fixture
def store(tmp_path):
    """Create a directory with 5 JSON files at staggered mtimes."""
    for i in range(5):
        f = tmp_path / f"entry_{i:02d}.json"
        f.write_text(json.dumps({"i": i}))
        # stagger mtime by 10s each
        t = time.time() - (4 - i) * 10
        import os
        os.utime(f, (t, t))
    return tmp_path


def test_prune_by_count_removes_oldest(store):
    result = prune_by_count(store, keep=3)
    assert result.total_removed == 2
    assert result.kept == 3
    remaining = list(store.glob("*.json"))
    assert len(remaining) == 3


def test_prune_by_count_dry_run_does_not_delete(store):
    result = prune_by_count(store, keep=2, dry_run=True)
    assert result.total_removed == 3
    assert len(list(store.glob("*.json"))) == 5


def test_prune_by_count_invalid_keep(store):
    with pytest.raises(PrunerError):
        prune_by_count(store, keep=0)


def test_prune_by_count_missing_dir(tmp_path):
    result = prune_by_count(tmp_path / "nonexistent", keep=3)
    assert result.total_removed == 0
    assert result.kept == 0


def test_prune_by_age_removes_old(store):
    # files are 0-40s old; threshold = 25s removes the 2 oldest (30s, 40s)
    result = prune_by_age(store, max_age_days=25 / 86400)
    assert result.total_removed == 2
    assert result.kept == 3


def test_prune_by_age_dry_run(store):
    result = prune_by_age(store, max_age_days=25 / 86400, dry_run=True)
    assert result.total_removed == 2
    assert len(list(store.glob("*.json"))) == 5


def test_prune_by_age_missing_dir(tmp_path):
    result = prune_by_age(tmp_path / "nope", max_age_days=1)
    assert result.total_removed == 0
