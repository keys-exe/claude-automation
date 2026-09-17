"""E10 doc-lint — the standing §34 step at every version cut.

A cut failing lint does not ship. Every check below is one clause of E10.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .slots import audit_manifest
from .standards import Standards, load

RETIRED_PHRASES = [
    "accurate lip sync",
    "accent restated",
]

RETIRED_IDS = [
    "ANAT-MOD1", "ANAT-MOD2", "ANAT-MOD5", "ANAT-MOD6",
    "ANAT-ARC", "ANAT-COL", "ANAT-HOLD", "NEG-FUTILE",
]

NORMATIVE_REF_RE = re.compile(r"NORMATIVE\s*[—-]\s*`?(?P<id>[A-Z][A-Z0-9\-]+)`?")
BACKTICK_ID_RE = re.compile(r"`(?P<id>[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+)`")
RETIREMENT_RE = re.compile(
    r"retire|withdraw|supersed|replac|no longer|dead instruction|never write both",
    re.I,
)


@dataclass
class Finding:
    rule: str
    detail: str
    line: int = 0
    severity: str = "FAIL"

    def __str__(self) -> str:
        where = f" (line {self.line})" if self.line else ""
        return f"{self.severity}  [{self.rule}]{where} {self.detail}"


def run(standards: Standards | None = None) -> list[Finding]:
    standards = standards or load()
    findings: list[Finding] = []
    findings += check_counts(standards)
    findings += check_id_resolution(standards)
    findings += check_slot_manifest(standards)
    findings += check_retired(standards)
    findings += check_changelogs(standards)
    findings += check_pending_amendments(standards)
    findings += check_open_decisions(standards)
    return findings


def check_counts(standards: Standards) -> list[Finding]:
    """Every Appendix A string has a count and the count matches its block."""
    findings = []
    for block in standards.blocks.values():
        if block.count_ok():
            continue
        declared = (f"{block.declared_lo}" if block.declared_lo == block.declared_hi
                    else f"{block.declared_lo}-{block.declared_hi}")
        findings.append(Finding(
            "count", f"{block.id}: declared {declared}, block measures {block.actual} "
                     f"(delta {block.actual - block.declared_lo:+d})",
            block.line,
        ))
    return findings


def check_id_resolution(standards: Standards) -> list[Finding]:
    """Every NORMATIVE ID resolves to a defined string."""
    findings = []
    for match in NORMATIVE_REF_RE.finditer(standards.text):
        block_id = match.group("id")
        if block_id not in standards.blocks:
            line = standards.text.count("\n", 0, match.start()) + 1
            findings.append(Finding("normative-id", f"{block_id} does not resolve to a string", line))
    return findings


def check_slot_manifest(standards: Standards) -> list[Finding]:
    """Every slot token appears in the E5 manifest."""
    findings = []
    for block in standards.blocks.values():
        for slot in audit_manifest(block.body):
            findings.append(Finding(
                "slot-manifest", f"{block.id}: [{slot}] is not in the E5 manifest", block.line,
                severity="WARN",
            ))
    return findings


def check_retired(standards: Standards) -> list[Finding]:
    """No retired phrase and no retired string ID survives outside a retirement notice."""
    findings = []
    lines = standards.text.splitlines()
    for number, line in enumerate(lines, start=1):
        if RETIREMENT_RE.search(line):
            continue
        for phrase in RETIRED_PHRASES:
            if phrase in line.lower():
                findings.append(Finding("retired-phrase", f"{phrase!r} survives", number))
        for retired in RETIRED_IDS:
            if re.search(rf"`{retired}`", line):
                findings.append(Finding("retired-id", f"`{retired}` survives", number))
    return findings


def check_changelogs(standards: Standards) -> list[Finding]:
    """Changelogs = current + one prior."""
    count = len(re.findall(r"^# CHANGELOG", standards.text, re.M))
    if count == 2:
        return []
    return [Finding("changelog", f"{count} changelog sections; E10 requires current + one prior")]


def check_pending_amendments(standards: Standards) -> list[Finding]:
    """Pending Amendments empties at each version cut (§34)."""
    match = re.search(r"^# PENDING AMENDMENTS(?P<body>.*?)^---", standards.text, re.M | re.S)
    if not match:
        return [Finding("pending", "no Pending Amendments table (§34)")]
    rows = [line for line in match.group("body").splitlines()
            if line.startswith("|") and not re.match(r"^\|[\s\-|]+\|$", line)]
    data_rows = [r for r in rows[1:] if "—" not in r.split("|")[1]]
    if data_rows:
        return [Finding("pending", f"{len(data_rows)} amendment(s) still pending at this cut (§34)",
                        severity="WARN")]
    return []


def check_open_decisions(standards: Standards) -> list[Finding]:
    """Open Decisions counts equal their lists."""
    match = re.search(r"^# OPEN DECISIONS(?P<body>.*?)(?=^# |\Z)", standards.text, re.M | re.S)
    if not match:
        return []
    body = match.group("body")
    findings = []
    for declared_count, label in re.findall(r"\*\*(\d+)\s+(open|unresolved|pending)\b", body, re.I):
        items = len(re.findall(r"^\s*[-*]\s+|^\|\s*\d+\s*\|", body, re.M))
        if items and int(declared_count) != items:
            findings.append(Finding(
                "open-decisions",
                f"declared {declared_count} {label}, list holds {items}", severity="WARN"))
    return findings


def summary(findings: list[Finding]) -> str:
    fails = sum(1 for f in findings if f.severity == "FAIL")
    warns = len(findings) - fails
    verdict = "ships" if fails == 0 else "DOES NOT SHIP"
    return f"{fails} fail · {warns} warn — a cut failing lint does not ship: this cut {verdict}"
