"""Format BucketReport for terminal output."""
from __future__ import annotations

from batchmark.bucketer import BucketReport

_COLORS = {
    "fast": "\033[32m",      # green
    "moderate": "\033[34m",  # blue
    "slow": "\033[33m",      # yellow
    "very_slow": "\033[31m", # red
}
_RESET = "\033[0m"
_BOLD = "\033[1m"


def _color(label: str, text: str) -> str:
    code = _COLORS.get(label, "")
    return f"{code}{text}{_RESET}" if code else text


def format_bucket_report(report: BucketReport, *, color: bool = True) -> str:
    lines: list[str] = []
    header = f"Bucket Report — branch: {_BOLD}{report.branch}{_RESET}"
    lines.append(header)
    lines.append(f"Total results: {report.total_results}")
    lines.append("")

    if report.total_results == 0:
        lines.append("  (no results)")
        return "\n".join(lines)

    col_w = 12
    lines.append(
        f"  {'Bucket':<{col_w}}  {'Count':>6}  {'% of total':>10}  Suites"
    )
    lines.append("  " + "-" * 60)

    for bucket in report.buckets:
        count = len(bucket)
        pct = (count / report.total_results * 100) if report.total_results else 0.0
        suite_preview = ", ".join(bucket.suite_names[:3])
        if len(bucket.suite_names) > 3:
            suite_preview += f" (+{len(bucket.suite_names) - 3} more)"

        label_str = bucket.label
        if color:
            label_str = _color(bucket.label, bucket.label)

        lines.append(
            f"  {label_str:<{col_w + len(label_str) - len(bucket.label)}}  "
            f"{count:>6}  {pct:>9.1f}%  {suite_preview}"
        )

    return "\n".join(lines)
