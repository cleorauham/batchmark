"""Fingerprinting: generate stable hashes for benchmark result sets."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class FingerprintEntry:
    branch: str
    suite: str
    fingerprint: str


@dataclass
class FingerprintReport:
    entries: List[FingerprintEntry]

    def by_branch(self) -> Dict[str, List[FingerprintEntry]]:
        out: Dict[str, List[FingerprintEntry]] = {}
        for e in self.entries:
            out.setdefault(e.branch, []).append(e)
        return out

    def get(self, branch: str, suite: str) -> str | None:
        for e in self.entries:
            if e.branch == branch and e.suite == suite:
                return e.fingerprint
        return None

    def matches(self, other: "FingerprintReport") -> bool:
        """Return True if every entry in self has the same fingerprint in other."""
        for e in self.entries:
            if other.get(e.branch, e.suite) != e.fingerprint:
                return False
        return True


def _fingerprint_result(result) -> str:
    payload = json.dumps(
        {
            "suite": result.suite,
            "branch": result.branch,
            "duration": round(result.duration, 6),
            "success": result.success,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def build_fingerprints(results) -> FingerprintReport:
    """Build a FingerprintReport from an iterable of benchmark results."""
    entries = [
        FingerprintEntry(
            branch=r.branch,
            suite=r.suite,
            fingerprint=_fingerprint_result(r),
        )
        for r in results
        if r.success
    ]
    return FingerprintReport(entries=entries)
