"""Format SegmentReport for terminal output."""
from __future__ import annotations

from batchmark.segmenter import SegmentReport


def _color(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _header() -> str:
    cols = [
        f"{'Segment':<20}",
        f"{'Branches':<20}",
        f"{'Suites':<20}",
        f"{'Results':>8}",
    ]
    return "  ".join(cols)


def _row(label: str, branches: int, suites: int, count: int) -> str:
    cols = [
        f"{_color(36, label):<29}",
        f"{branches:<20}",
        f"{suites:<20}",
        f"{count:>8}",
    ]
    return "  ".join(cols)


def format_segment_report(report: SegmentReport) -> str:
    if not report.segments:
        return _color(33, "No segments found.")

    lines = [
        _color(1, "Segment Report"),
        _color(90, f"  {report.total_segments} segment(s), "
               f"{report.total_results} result(s) total"),
        "",
        _header(),
        "-" * 72,
    ]
    for seg in report.segments:
        lines.append(
            _row(seg.label, len(seg.branch_names), len(seg.suite_names), len(seg))
        )
    return "\n".join(lines)
