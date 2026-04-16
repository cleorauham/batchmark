"""Tests for batchmark configuration loading."""

import textwrap
from pathlib import Path

import pytest

from batchmark.config import BatchmarkConfig, BenchmarkSuite


SAMPLE_TOML = textwrap.dedent("""\
    branches = ["main", "feature/fast-path"]
    output_dir = "results"
    warmup_iterations = 2

    [[suites]]
    name = "sort-bench"
    command = "python bench_sort.py"
    iterations = 10

    [[suites]]
    name = "io-bench"
    command = "python bench_io.py"
    working_dir = "benchmarks"
    env = { DATA_SIZE = "large" }
""")


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    p = tmp_path / "batchmark.toml"
    p.write_text(SAMPLE_TOML)
    return p


def test_load_branches(config_file):
    cfg = BatchmarkConfig.from_file(config_file)
    assert cfg.branches == ["main", "feature/fast-path"]


def test_load_suites(config_file):
    cfg = BatchmarkConfig.from_file(config_file)
    assert len(cfg.suites) == 2
    assert isinstance(cfg.suites[0], BenchmarkSuite)
    assert cfg.suites[0].name == "sort-bench"
    assert cfg.suites[0].iterations == 10


def test_suite_defaults(config_file):
    cfg = BatchmarkConfig.from_file(config_file)
    assert cfg.suites[0].working_dir == "."
    assert cfg.suites[0].env == {}


def test_suite_env(config_file):
    cfg = BatchmarkConfig.from_file(config_file)
    assert cfg.suites[1].env == {"DATA_SIZE": "large"}


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        BatchmarkConfig.from_file(tmp_path / "missing.toml")


def test_missing_branches(tmp_path):
    p = tmp_path / "bad.toml"
    p.write_text('[[suites]]\nname="x"\ncommand="y"\n')
    with pytest.raises(ValueError, match="branch"):
        BatchmarkConfig.from_file(p)


def test_missing_suites(tmp_path):
    p = tmp_path / "bad.toml"
    p.write_text('branches = ["main"]\n')
    with pytest.raises(ValueError, match="suite"):
        BatchmarkConfig.from_file(p)
