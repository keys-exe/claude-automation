"""E2 failure taxonomy and retry budgets.

Global rule: two automatic rerolls per beat per failure class, then the beat
queues for a human with its failure history attached. Retries never change the
prompt silently — every changed prompt is a delivered iteration (§16).
"""

from __future__ import annotations

from dataclasses import dataclass

from .ledger import Ledger
from .tables import FAILURE_CLASSES, GLOBAL_RETRY_CAP


@dataclass
class Decision:
    action: str          # "retry" | "human"
    failure_class: str
    remedy: str
    attempt: int
    budget: int
    history: list[dict]

    @property
    def to_human(self) -> bool:
        return self.action == "human"

    def __str__(self) -> str:
        if self.to_human:
            return (f"HUMAN — {self.failure_class} exhausted after {self.attempt} "
                    f"of {self.budget}; failure history attached")
        return (f"RETRY {self.attempt}/{self.budget} — {self.failure_class}: {self.remedy}")


def classify(signal: str) -> str:
    """Map a raw API/QA signal to an E2 class. Unknown signals are not guessed."""
    lowered = signal.lower()
    table = [
        ("SAFETY_REJECT", ("safety", "refus", "content policy", "blocked by")),
        ("PRESET_OVERRIDE", ("preset",)),
        ("COMPLETION_404", ("404", "not found", "media input")),
        ("ALIAS_MISMATCH", ("alias", "model mismatch", "logged model")),
        ("SYNC_DRIFT", ("sync", "drift", "lip")),
        ("CONSISTENCY_FAIL", ("scene", "subject", "plate", "identity", "anchor")),
        ("QUALITY_FAIL", ("quality", "smooth", "plastic", "qa", "reroll")),
    ]
    for name, needles in table:
        if any(needle in lowered for needle in needles):
            return name
    return "QUALITY_FAIL"


def decide(ledger: Ledger, beat_id: str, failure_class: str) -> Decision:
    if failure_class not in FAILURE_CLASSES:
        raise KeyError(f"{failure_class!r} is not an E2 failure class")
    spec = FAILURE_CLASSES[failure_class]
    budget = min(spec["budget"], GLOBAL_RETRY_CAP) if failure_class not in (
        "PRESET_OVERRIDE", "COMPLETION_404") else spec["budget"]
    already = ledger.retries_for(beat_id, failure_class)
    history = [r for r in ledger.beat(beat_id)["retries"] if r["class"] == failure_class]
    if already >= budget:
        return Decision("human", failure_class, spec["remedy"], already, budget, history)
    return Decision("retry", failure_class, spec["remedy"], already + 1, budget, history)


def apply(ledger: Ledger, beat_id: str, failure_class: str, action: str | None = None) -> Decision:
    """Record the attempt and return the decision it produced."""
    decision = decide(ledger, beat_id, failure_class)
    if decision.action == "retry":
        ledger.record_retry(beat_id, failure_class, action or decision.remedy)
    else:
        row = ledger.beat(beat_id)
        row["i2v_qa"] = {**(row.get("i2v_qa") or {}), failure_class: "HUMAN"}
    return decision
