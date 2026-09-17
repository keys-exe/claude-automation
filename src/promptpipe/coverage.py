"""§27B Coverage Ledger — every phrase receives a disposition, or the act is undelivered.

The phrase inventory is built at §18 step 2 as a mechanical pass over the script
as written. The script is never edited to solve a build problem: `CUT` is
withdrawn, `BLOCKED` replaces it and carries its reason and its section.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .tables import DEMO_KINDS, DISPOSITIONS, WITHDRAWN_DISPOSITIONS

SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")
CLAUSE_SPLIT_RE = re.compile(r",(?=\s)|\bbut\b|\bthen\b|\bso\b|\bbecause\b|\band then\b", re.I)
DISPOSITION_RE = re.compile(
    r"^(?P<kind>BR|TH|MECH)-(?P<num>[0-9]+[A-Za-z]?)$|"
    r"^(?P<merged>MERGED)→(?P<target>P-[0-9]+)$|"
    r"^(?P<blocked>BLOCKED)$"
)


@dataclass
class Phrase:
    id: str
    text: str
    triggers: list[str] = field(default_factory=list)
    disposition: str = ""
    demo: str = ""
    plant: str = ""
    payoff: str = ""
    blocked_reason: str = ""
    blocked_section: str = ""

    @property
    def covered(self) -> bool:
        return bool(self.disposition) and self.disposition not in ("", "UNSET")


@dataclass
class Reconciliation:
    """The one line outside the prompt blocks that closes an act (§27B)."""

    first: str
    last: str
    beats: int
    merges: list[str]
    th_carried: list[str]
    uncovered: int
    blocked: int
    unpaid_plants: list[str]

    @property
    def delivered(self) -> bool:
        # Uncovered must read zero. Blocked is reported, never resolved.
        return self.uncovered == 0

    def line(self) -> str:
        parts = [
            f"{self.first}–{self.last} → {self.beats} beats",
            f"merged: {', '.join(self.merges) if self.merges else 'none'}",
            f"TH-carried: {', '.join(self.th_carried) if self.th_carried else 'none'}",
            f"uncovered: {self.uncovered}",
            f"blocked: {self.blocked}",
            f"unpaid plants: {', '.join(self.unpaid_plants) if self.unpaid_plants else 'none'}",
        ]
        return " · ".join(parts)


def split_script(script: str) -> list[Phrase]:
    """A mechanical pass per §27's split triggers.

    Mechanical triggers fire here: sentence end, clause boundary, list item.
    The tone-shift and punchline triggers are not mechanical — phrases carrying
    a candidate are tagged `REVIEW` so the split is confirmed, never assumed.
    """
    phrases: list[Phrase] = []
    counter = 0
    for raw_sentence in SENTENCE_RE.findall(script):
        sentence = raw_sentence.strip()
        if not sentence:
            continue
        units = _split_sentence(sentence)
        for text, triggers in units:
            counter += 1
            phrases.append(Phrase(id=f"P-{counter:03d}", text=text, triggers=triggers))
    return phrases


def _split_sentence(sentence: str) -> list[tuple[str, list[str]]]:
    # List of nouns: one beat each, no exceptions (§27).
    body = sentence.rstrip(".!?")
    if body.count(",") >= 2 and not re.search(r"\b(and then|because|so that)\b", body, re.I):
        items = [item.strip() for item in re.split(r",|\band\b", body) if item.strip()]
        if len(items) >= 3 and all(len(item.split()) <= 4 for item in items):
            return [(item, ["list-item"]) for item in items]

    pieces = [piece.strip(" ,") for piece in CLAUSE_SPLIT_RE.split(sentence) if piece and piece.strip(" ,")]
    if len(pieces) <= 1:
        return [(sentence, _tone_flags(sentence))]
    out = []
    for piece in pieces:
        triggers = ["clause"] + _tone_flags(piece)
        # A clause with no internal shift is a MERGED candidate, not a split.
        if len(piece.split()) <= 5:
            triggers.append("merge-candidate")
        out.append((piece, triggers))
    return out


_TONE_WORDS = {
    "problem": ("pain", "ache", "stiff", "worse", "struggle", "can't", "cannot", "tired", "swollen"),
    "solution": ("relief", "finally", "again", "easier", "back to", "no longer", "without"),
}


def _tone_flags(text: str) -> list[str]:
    lowered = text.lower()
    flags = []
    if any(word in lowered for word in _TONE_WORDS["problem"]):
        flags.append("problem-language")
    if any(word in lowered for word in _TONE_WORDS["solution"]):
        flags.append("solution-language")
    if re.search(r"\b\d+([.,]\d+)?%?\b", text):
        flags.append("number")
    if "problem-language" in flags and "solution-language" in flags:
        flags.append("REVIEW:tone-shift")
    return flags


def validate_disposition(value: str) -> str | None:
    """Returns an error string, or None when the disposition is legal."""
    if not value:
        return "no disposition — silence is not a legal state (§27B)"
    head = value.split("-")[0].split("→")[0]
    if head in WITHDRAWN_DISPOSITIONS:
        return f"{head} is withdrawn as an agent disposition; use BLOCKED with its reason (§27B)"
    if DISPOSITION_RE.match(value):
        return None
    return (f"{value!r} is not a §27B disposition "
            f"(expected one of {', '.join(DISPOSITIONS)})")


def reconcile(phrases: list[Phrase]) -> Reconciliation:
    beats: set[str] = set()
    merges, th_carried, unpaid = [], [], []
    uncovered = blocked = 0
    paid_plants = {p.payoff for p in phrases if p.payoff}
    for phrase in phrases:
        disposition = phrase.disposition
        if not disposition:
            uncovered += 1
            continue
        if disposition == "BLOCKED":
            blocked += 1
            continue
        if disposition.startswith("MERGED"):
            merges.append(phrase.id)
            continue
        if disposition.startswith("TH-"):
            th_carried.append(disposition)
            beats.add(disposition)
            continue
        beats.add(disposition)
    for phrase in phrases:
        if phrase.plant and phrase.plant not in paid_plants:
            unpaid.append(f"{phrase.id}→{phrase.plant}")
    ids = [p.id for p in phrases]
    return Reconciliation(
        first=ids[0] if ids else "P-000",
        last=ids[-1] if ids else "P-000",
        beats=len(beats),
        merges=sorted(merges),
        th_carried=sorted(set(th_carried)),
        uncovered=uncovered,
        blocked=blocked,
        unpaid_plants=sorted(unpaid),
    )


def audit(phrases: list[Phrase]) -> list[str]:
    """Every problem §27B names, as a flat list of strings."""
    problems: list[str] = []
    for phrase in phrases:
        error = validate_disposition(phrase.disposition)
        if error:
            problems.append(f"{phrase.id}: {error}")
        if phrase.disposition == "BLOCKED" and not (phrase.blocked_reason and phrase.blocked_section):
            problems.append(f"{phrase.id}: BLOCKED carries no reason and section (§27B)")
        if phrase.demo and phrase.demo.split(":")[0].upper() not in DEMO_KINDS:
            problems.append(f"{phrase.id}: DEMO {phrase.demo!r} is not a §30B demonstration")
        if phrase.disposition.startswith("MERGED"):
            target = phrase.disposition.split("→")[-1]
            if target not in {p.id for p in phrases}:
                problems.append(f"{phrase.id}: MERGED into {target}, which is not in the inventory")
    problems += _beat_id_gaps(phrases)
    return problems


def _beat_id_gaps(phrases: list[Phrase]) -> list[str]:
    """Beat IDs stay contiguous — a gap in BR- numbering is itself the alarm (§27B)."""
    problems = []
    for prefix in ("BR", "TH", "MECH"):
        numbers = sorted(
            int(re.sub(r"[^0-9]", "", p.disposition.split("-", 1)[1]))
            for p in phrases
            if p.disposition.startswith(f"{prefix}-")
            and re.sub(r"[^0-9]", "", p.disposition.split("-", 1)[1])
        )
        if not numbers:
            continue
        expected = set(range(numbers[0], numbers[-1] + 1))
        missing = sorted(expected - set(numbers))
        if missing:
            problems.append(
                f"{prefix} numbering has gaps at {', '.join(f'{prefix}-{n:02d}' for n in missing)} (§27B)"
            )
    return problems


def load(path: Path | str) -> list[Phrase]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data["phrases"] if isinstance(data, dict) else data
    return [Phrase(**row) for row in rows]


def save(phrases: list[Phrase], path: Path | str) -> None:
    payload = {"phrases": [asdict(p) for p in phrases]}
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
