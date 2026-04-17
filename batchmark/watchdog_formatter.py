"""Formatter for WatchdogReport output."""
from batchmark.watchdog import WatchdogReport


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_watchdog_report(report: WatchdogReport, *, color: bool = True) -> str:
    lines: list[str] = []

    if not report.has_alerts:
        ok = _color("OK", "32") if color else "OK"
        lines.append(f"Watchdog: {ok} — no threshold breaches detected.")
        return "\n".join(lines)

    header = _color("Watchdog Alerts", "31") if color else "Watchdog Alerts"
    lines.append(f"{header} ({len(report.alerts)} breach(es))")
    lines.append("-" * 48)

    for alert in report.alerts:
        suite = _color(alert.suite, "33") if color else alert.suite
        reason = alert.reason.replace("_", " ")
        lines.append(f"  {suite}: {reason} — got {alert.value:.2f}, limit {alert.threshold:.2f}")

    return "\n".join(lines)
