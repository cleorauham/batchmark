import pytest
from batchmark.config import BenchmarkSuite
from batchmark.scheduler import schedule, SchedulerError, suite_names, ScheduledBatch


def _suite(name: str, priority: int | None = None) -> BenchmarkSuite:
    env = {"BATCHMARK_PRIORITY": str(priority)} if priority is not None else {}
    return BenchmarkSuite(name=name, command=f"run {name}", env=env or None)


def test_schedule_single_batch():
    suites = [_suite("a"), _suite("b"), _suite("c")]
    batches = schedule(suites, max_parallel=10)
    assert len(batches) == 1
    assert batches[0].size == 3


def test_schedule_splits_into_batches():
    suites = [_suite("a"), _suite("b"), _suite("c")]
    batches = schedule(suites, max_parallel=2)
    assert len(batches) == 2
    assert batches[0].size == 2
    assert batches[1].size == 1


def test_schedule_respects_priority_order():
    suites = [_suite("slow", priority=10), _suite("fast", priority=1)]
    batches = schedule(suites, max_parallel=1)
    assert suite_names(batches[0]) == ["fast"]
    assert suite_names(batches[1]) == ["slow"]


def test_schedule_default_priority_last():
    suites = [_suite("no_prio"), _suite("first", priority=1)]
    batches = schedule(suites, max_parallel=1)
    assert suite_names(batches[0]) == ["first"]


def test_schedule_invalid_parallel():
    with pytest.raises(SchedulerError):
        schedule([_suite("a")], max_parallel=0)


def test_schedule_empty_suites():
    batches = schedule([], max_parallel=2)
    assert batches == []


def test_suite_names_returns_list():
    batch = ScheduledBatch(index=0, suites=[_suite("x"), _suite("y")])
    assert suite_names(batch) == ["x", "y"]


def test_batch_index_increments():
    suites = [_suite(str(i)) for i in range(4)]
    batches = schedule(suites, max_parallel=2)
    assert [b.index for b in batches] == [0, 1]
