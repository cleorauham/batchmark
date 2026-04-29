"""Formatter for WatchdogReport output."""
from batchmark.watchdog import WatchdogReport


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _pluralize(count: int, singular: str, plural: str | None = None) -> str:
    """Return singular or plural form based on count."""
    if plural is None:
        plural = singular + "s"
    return singular if count == 1 else plural


def format_watchdog_report(report: WatchdogReport, *, color: bool = True) -> str:
    """Format a WatchdogReport into a human-readable string.

    Args:
        report: The WatchdogReport to format.
        color: Whether to include ANSI color codes in the output.

    Returns:
        A formatted string summarising the watchdog results.
    """
    lines: list[str] = []

    if not report.has_alerts:
        ok = _color("OK", "32") if color else "OK"
        lines.append(f"Watchdog: {ok} — no threshold breaches detected.")
        return "\n".join(lines)

    count = len(report.alerts)
    breach_word = _pluralize(count, "breach", "breaches")
    header = _color("Watchdog Alerts", "31") if color else "Watchdog Alerts"
    lines.append(f"{header} ({count} {breach_word})")
    lines.append("-" * 48)

    for alert in report.alerts:
        suite = _color(alert.suite, "33") if color else alert.suite
        reason = alert.reason.replace("_", " ")
        lines.append(f"  {suite}: {reason} — got {alert.value:.2f}, limit {alert.threshold:.2f}")

    return "\n".join(lines)
