"""E6 duration function, §28H word budget, §37 character budget.

Every check here is programmatic and free, and is run before submission —
never after a render comes back (§28H part 1).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .standards import minify
from .tables import (
    BROLL_DEFAULT_DURATION,
    KLING_DIRECT_CEILING,
    MECHANISM_KLING_DIRECT_DURATION,
    WORDS_PER_DURATION,
)

WORD_RE = re.compile(r"[A-Za-z0-9'’\-]+")


@dataclass
class Verdict:
    ok: bool
    check: str
    detail: str
    remedy: str = ""

    def __str__(self) -> str:
        mark = "PASS" if self.ok else "FAIL"
        line = f"{mark}  {self.check}: {self.detail}"
        if not self.ok and self.remedy:
            line += f"\n      -> {self.remedy}"
        return line


def word_count(dialogue: str) -> int:
    return len(WORD_RE.findall(dialogue))


def char_count(prompt: str) -> int:
    """Counts are measured on the minified string (§37, measured V7.48)."""
    return len(minify(prompt))


def duration_for(words: int, pace: str = "brisk", talking_while_doing: bool = False) -> int | None:
    """E6: words at pace -> duration. None means split the line (§29)."""
    if talking_while_doing:
        pace = "unhurried"  # movement eats tempo (§28H)
    table = WORDS_PER_DURATION[pace]
    for seconds in sorted(table):
        if words <= table[seconds]:
            return seconds
    return None


def broll_duration(demonstration_needs_longer: bool = False, kling_direct_mechanism: bool = False) -> int:
    if kling_direct_mechanism:
        return MECHANISM_KLING_DIRECT_DURATION
    return BROLL_DEFAULT_DURATION if not demonstration_needs_longer else 10


def check_word_budget(dialogue: str, duration: int, pace: str = "brisk",
                      talking_while_doing: bool = False) -> Verdict:
    """§28H part 1 — a hard gate. Over budget gets a longer duration or gets cut."""
    if talking_while_doing:
        pace = "unhurried"
    words = word_count(dialogue)
    table = WORDS_PER_DURATION[pace]
    if duration not in table:
        return Verdict(False, "word_budget",
                       f"{duration}s is not a §28H duration (5 or 10)",
                       "Use E6 to pick the duration, or split the line (§29)")
    ceiling = table[duration]
    if words <= ceiling:
        return Verdict(True, "word_budget", f"{words} words <= {ceiling} at {pace}/{duration}s")
    suggested = duration_for(words, pace, talking_while_doing)
    remedy = (f"raise duration to {suggested}s (E7)" if suggested
              else "split the line per §29")
    return Verdict(False, "word_budget",
                   f"{words} words > {ceiling} at {pace}/{duration}s",
                   f"{remedy} — never squeeze")


def check_char_budget(prompt: str, kling_direct: bool = True,
                      ceiling: int = KLING_DIRECT_CEILING) -> Verdict:
    """E1 — <= 2,500 on any beat that may route Kling-direct."""
    count = char_count(prompt)
    if not kling_direct:
        return Verdict(True, "char_count", f"{count} chars (Higgsfield-routed, no ceiling)")
    if count <= ceiling:
        return Verdict(True, "char_count", f"{count} <= {ceiling} minified")
    return Verdict(False, "char_count", f"{count} > {ceiling} minified",
                   f"Trim ladder (§37), recount — over by {count - ceiling}")


def check_punctuation(dialogue: str) -> Verdict:
    """§28H supporting locks: full stops and commas only."""
    banned = {"…": "ellipsis", "...": "ellipsis", "—": "em-dash", "–": "en-dash"}
    found = [name for token, name in banned.items() if token in dialogue]
    if not found:
        return Verdict(True, "punctuation", "full stops and commas only")
    return Verdict(False, "punctuation", f"banned punctuation: {', '.join(sorted(set(found)))}",
                   "Ellipses are banned; em-dashes generate unpredictable holds (§28H)")


def closure_word(dialogue: str) -> str | None:
    """E5: first stressed word containing m/b/p (or f/v); else any m/b/p word."""
    words = WORD_RE.findall(dialogue)
    for group in ("mbp", "fv"):
        for word in words:
            if any(ch in word.lower() for ch in group):
                return word
    return None


def check_sync_anchor(dialogue: str, bound_move_word: str | None,
                      closure: str | None) -> Verdict:
    """§28H part 2 — a beat with neither anchor has no sync anchor at all."""
    if bound_move_word or closure:
        anchor = bound_move_word or closure
        kind = "bound move" if bound_move_word else "closure word"
        return Verdict(True, "sync_anchor", f"{kind}: {anchor!r}")
    suggestion = closure_word(dialogue)
    return Verdict(False, "sync_anchor", "no bound move word and no closure word",
                   f"bind a word to a visible move, or set closure_word"
                   + (f" (candidate: {suggestion!r})" if suggestion else ""))
