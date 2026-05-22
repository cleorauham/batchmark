"""Audit trail: record and query which suites ran on which branches."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class AuditError(Exception):
    pass


@dataclass
class AuditEntry:
    suite: str
    branch: str
    timestamp: float
    duration: float
    success: bool
    meta: Dict[str, str] = field(default_factory=dict)


@dataclass
class AuditReport:
    entries: List[AuditEntry] = field(default_factory=list)

    def by_branch(self, branch: str) -> List[AuditEntry]:
        return [e for e in self.entries if e.branch == branch]

    def by_suite(self, suite: str) -> List[AuditEntry]:
        return [e for e in self.entries if e.suite == suite]

    def failed(self) -> List[AuditEntry]:
        return [e for e in self.entries if not e.success]

    def branches(self) -> List[str]:
        return sorted({e.branch for e in self.entries})

    def suites(self) -> List[str]:
        return sorted({e.suite for e in self.entries})


def audit_path(store: Path, name: str) -> Path:
    return store / f"{name}.audit.json"


def save_audit(store: Path, name: str, report: AuditReport) -> Path:
    store.mkdir(parents=True, exist_ok=True)
    path = audit_path(store, name)
    data = [
        {
            "suite": e.suite,
            "branch": e.branch,
            "timestamp": e.timestamp,
            "duration": e.duration,
            "success": e.success,
            "meta": e.meta,
        }
        for e in report.entries
    ]
    path.write_text(json.dumps(data, indent=2))
    return path


def load_audit(store: Path, name: str) -> AuditReport:
    path = audit_path(store, name)
    if not path.exists():
        raise AuditError(f"Audit not found: {name}")
    data = json.loads(path.read_text())
    entries = [
        AuditEntry(
            suite=d["suite"],
            branch=d["branch"],
            timestamp=d["timestamp"],
            duration=d["duration"],
            success=d["success"],
            meta=d.get("meta", {}),
        )
        for d in data
    ]
    return AuditReport(entries=entries)


def list_audits(store: Path) -> List[str]:
    if not store.exists():
        return []
    return sorted(p.stem.replace(".audit", "") for p in store.glob("*.audit.json"))


def build_audit(results: list, branch: str) -> AuditReport:
    """Build an AuditReport from a list of BenchmarkResult-like objects."""
    entries = []
    for r in results:
        entries.append(
            AuditEntry(
                suite=r.suite,
                branch=branch,
                timestamp=getattr(r, "timestamp", time.time()),
                duration=r.duration,
                success=r.success,
            )
        )
    return AuditReport(entries=entries)
