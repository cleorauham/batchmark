"""Configuration loading and validation for batchmark."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BenchmarkSuite:
    name: str
    command: str
    working_dir: str = "."
    iterations: int = 5
    env: dict[str, str] = field(default_factory=dict)


@dataclass
class BatchmarkConfig:
    branches: list[str]
    suites: list[BenchmarkSuite]
    output_dir: str = "batchmark-results"
    warmup_iterations: int = 1

    @classmethod
    def from_file(cls, path: Path) -> "BatchmarkConfig":
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls._parse(data)

    @classmethod
    def _parse(cls, data: dict) -> "BatchmarkConfig":
        if "branches" not in data:
            raise ValueError("Config must specify at least one branch")
        if "suites" not in data or not data["suites"]:
            raise ValueError("Config must define at least one benchmark suite")

        suites = [
            BenchmarkSuite(
                name=s["name"],
                command=s["command"],
                working_dir=s.get("working_dir", "."),
                iterations=s.get("iterations", 5),
                env=s.get("env", {}),
            )
            for s in data["suites"]
        ]

        return cls(
            branches=data["branches"],
            suites=suites,
            output_dir=data.get("output_dir", "batchmark-results"),
            warmup_iterations=data.get("warmup_iterations", 1),
        )
