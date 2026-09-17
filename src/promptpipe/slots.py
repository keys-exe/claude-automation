"""E5 slot-fill manifest — fill and verify, never leave a token to the model."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .tables import SLOT_REQUIREMENTS, SLOT_SOURCES

SLOT_RE = re.compile(r"\[(?P<slot>[A-Z][A-Z0-9 \-/]*)\]")


@dataclass
class FillResult:
    text: str
    filled: dict[str, str] = field(default_factory=dict)
    unfilled: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.unfilled and not self.unknown


def tokens(text: str) -> list[str]:
    seen: list[str] = []
    for match in SLOT_RE.finditer(text):
        slot = match.group("slot")
        if slot not in seen:
            seen.append(slot)
    return seen


def fill(text: str, values: dict[str, str], strict: bool = True) -> FillResult:
    """Substitute verbatim. An unfilled slot is a failure, not a default."""
    result = FillResult(text=text)
    for slot in tokens(text):
        if slot in values and str(values[slot]).strip():
            value = str(values[slot])
            result.text = result.text.replace(f"[{slot}]", value)
            result.filled[slot] = value
        else:
            result.unfilled.append(slot)
            if slot not in SLOT_SOURCES:
                result.unknown.append(slot)
    if strict and not result.ok:
        pass  # caller decides; the CLI reports rather than raises
    return result


def source_for(slot: str) -> str:
    return SLOT_SOURCES.get(slot, "UNDECLARED — not in the E5 manifest")


def required_for(beat: dict) -> list[str]:
    """Slots E5 marks mandatory on this beat's class."""
    needed: list[str] = []
    state = (beat.get("product_state") or "").lower()
    register = (beat.get("register") or "").upper()
    notes = f"{beat.get('notes', '')} {beat.get('function', '')}".lower()
    if state == "worn":
        needed += SLOT_REQUIREMENTS["worn"]
    if "rear" in notes or "turn" in notes or (beat.get("frame_side") or "").lower() == "rear":
        needed += SLOT_REQUIREMENTS["rear_or_turning"]
    if "STRESS" in register:
        needed += SLOT_REQUIREMENTS["stress_register"]
    out: list[str] = []
    for slot in needed:
        if slot not in out:
            out.append(slot)
    return out


BRACKET_RE = re.compile(r"\[[^\]]{1,200}\]")


def residual_brackets(text: str) -> list[str]:
    """Any bracket left in a prompt is an instruction the model will read aloud.

    Catches both E5 slot tokens and the longer bracketed fill instructions the
    PATTERN strings carry, which are prose and so never match a slot token.
    """
    return [match.group(0) for match in BRACKET_RE.finditer(text)]


def audit_manifest(text: str) -> list[str]:
    """E10 doc-lint: every slot token appears in the E5 manifest."""
    return [slot for slot in tokens(text) if slot not in SLOT_SOURCES]
