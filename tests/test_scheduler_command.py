import argparse
import pytest
from unittest.mock import patch
from batchmark.scheduler_command import add_scheduler_subparser, run_scheduler_command
from batchmark.scheduler import ScheduledBatch
from batchmark.config import BenchmarkSuite


def _suite(name, priority=0):
    return BenchmarkSuite(
        name=name,
        command=f"bench {name}",
        priority=priority,
    )


def _args(**kwargs):
    defaults = {
        "batch_size": 3,
        "suites": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_scheduler_subparser_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_scheduler_subparser(sub)
    args = parser.parse_args(["schedule", "--batch-size", "2"])
    assert args.batch_size == 2


def test_run_scheduler_prints_batches(capsys):
    suites = [_suite("alpha", priority=1), _suite("beta"), _suite("gamma", priority=2)]
    batches = [
        ScheduledBatch(index=0, suites=[suites[2], suites[0]]),
        ScheduledBatch(index=1, suites=[suites[1]]),
    ]
    with patch("batchmark.scheduler_command.schedule", return_value=batches):
        run_scheduler_command(_args(batch_size=2), suites)
    out = capsys.readouterr().out
    assert "Batch 1" in out
    assert "Batch 2" in out


def test_run_scheduler_shows_suite_names(capsys):
    suites = [_suite("fast", priority=1), _suite("slow")]
    batches = [
        ScheduledBatch(index=0, suites=[suites[0]]),
        ScheduledBatch(index=1, suites=[suites[1]]),
    ]
    with patch("batchmark.scheduler_command.schedule", return_value=batches):
        run_scheduler_command(_args(batch_size=1), suites)
    out = capsys.readouterr().out
    assert "fast" in out
    assert "slow" in out


def test_run_scheduler_filters_by_suite_name(capsys):
    suites = [_suite("alpha"), _suite("beta"), _suite("gamma")]
    batches = [ScheduledBatch(index=0, suites=[suites[0], suites[2]])]
    with patch("batchmark.scheduler_command.schedule", return_value=batches) as mock_sched:
        run_scheduler_command(_args(batch_size=5, suites=["alpha", "gamma"]), suites)
        called_suites = mock_sched.call_args[0][0]
        assert all(s.name in ("alpha", "gamma") for s in called_suites)


def test_run_scheduler_empty_suites(capsys):
    with patch("batchmark.scheduler_command.schedule", return_value=[]):
        run_scheduler_command(_args(batch_size=3), [])
    out = capsys.readouterr().out
    assert "no" in out.lower() or out.strip() == "" or "0" in out
