"""Benchmark runner: executes benchmark suites against git branches."""

import os
import subprocess
import time
import shlex
from dataclasses import dataclass, field
from typing import Optional

from .config import BenchmarkSuite, BatchmarkConfig


@dataclass
class BenchmarkResult:
    """Result of a single benchmark suite run on a specific branch."""

    branch: str
    suite_name: str
    command: str
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    env: dict = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.returncode == 0


class RunnerError(Exception):
    """Raised when a runner operation fails unrecoverably."""


def _checkout_branch(branch: str, repo_path: str) -> None:
    """Checkout the given branch in the repo at repo_path."""
    result = subprocess.run(
        ["git", "checkout", branch],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RunnerError(
            f"Failed to checkout branch '{branch}': {result.stderr.strip()}"
        )


def _run_suite(
    suite: BenchmarkSuite,
    branch: str,
    repo_path: str,
    timeout: Optional[int] = None,
) -> BenchmarkResult:
    """Run a single benchmark suite and return its result."""
    env = os.environ.copy()
    env.update(suite.env)

    start = time.monotonic()
    try:
        proc = subprocess.run(
            shlex.split(suite.command),
            cwd=repo_path,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return BenchmarkResult(
            branch=branch,
            suite_name=suite.name,
            command=suite.command,
            returncode=-1,
            stdout="",
            stderr=f"Timed out after {timeout}s",
            duration_seconds=elapsed,
            env=suite.env,
        )
    elapsed = time.monotonic() - start

    return BenchmarkResult(
        branch=branch,
        suite_name=suite.name,
        command=suite.command,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        duration_seconds=elapsed,
        env=suite.env,
    )


def run_all(
    config: BatchmarkConfig,
    repo_path: str = ".",
    timeout: Optional[int] = None,
    verbose: bool = False,
) -> list[BenchmarkResult]:
    """Run all suites across all configured branches.

    Checks out each branch in turn, runs every suite, and collects results.
    Restores the original branch (or HEAD) when finished.
    """
    # Remember the current branch so we can restore it afterward.
    head = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    ).stdout.strip()

    results: list[BenchmarkResult] = []

    try:
        for branch in config.branches:
            if verbose:
                print(f"[batchmark] checking out branch: {branch}")
            _checkout_branch(branch, repo_path)

            for suite in config.suites:
                if verbose:
                    print(f"[batchmark]   running suite: {suite.name}")
                result = _run_suite(suite, branch, repo_path, timeout=timeout)
                results.append(result)

                if verbose:
                    status = "ok" if result.success else f"exit {result.returncode}"
                    print(f"[batchmark]   {suite.name}: {status} ({result.duration_seconds:.2f}s)")
    finally:
        # Best-effort restore; ignore errors (e.g. dirty working tree).
        subprocess.run(["git", "checkout", head], cwd=repo_path, capture_output=True)

    return results
