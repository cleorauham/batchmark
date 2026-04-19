from batchmark.replayer import ReplayReport, ReplaySource
from batchmark.replay_formatter import format_replay_report
from batchmark.runner import BenchmarkResult


def _result(suite: str, success: bool = True) -> BenchmarkResult:
    return BenchmarkResult(suite=suite, branch="main", duration=0.42, success=success, output="")


def _report(kind: str = "baseline", name: str = "v1") -> ReplayReport:
    src = ReplaySource(kind=kind, name=name, suite_names=["bench_a"])
    return ReplayReport(source=src, results=[_result("bench_a")])


def test_format_shows_source_kind():
    out = format_replay_report(_report(kind="cache", name="main"), color=False)
    assert "cache" in out
    assert "main" in out


def test_format_shows_suite_name():
    out = format_replay_report(_report(), color=False)
    assert "bench_a" in out


def test_format_shows_duration():
    out = format_replay_report(_report(), color=False)
    assert "0.4200s" in out


def test_format_shows_ok_status():
    out = format_replay_report(_report(), color=False)
    assert "OK" in out


def test_format_shows_fail_status():
    src = ReplaySource(kind="baseline", name="v1", suite_names=["bench_a"])
    report = ReplayReport(source=src, results=[_result("bench_a", success=False)])
    out = format_replay_report(report, color=False)
    assert "FAIL" in out


def test_format_empty_results():
    src = ReplaySource(kind="cache", name="dev", suite_names=[])
    report = ReplayReport(source=src, results=[])
    out = format_replay_report(report, color=False)
    assert "no results" in out


def test_format_summary_counts():
    src = ReplaySource(kind="baseline", name="v2", suite_names=["a", "b"])
    report = ReplayReport(
        source=src,
        results=[_result("a", success=True), _result("b", success=False)],
    )
    out = format_replay_report(report, color=False)
    assert "1 ok" in out
    assert "1 failed" in out
