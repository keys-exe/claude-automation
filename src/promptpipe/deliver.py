"""§16 output layout and §26 video package — the prompt is the deliverable.

Running a beat and describing what changed leaves the user with an image and no
asset. Every generated beat ships its full prompt text in a fenced block, with
the model string, aspect ratio, resolution or duration, and the character count.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from .budget import char_count
from .coverage import Reconciliation

VO = "🎙"      # VO over B-roll — narration in the edit, no synced speech
ON_CAMERA = "🗣"  # spoken on camera — the line lives in `dialogue` and lip-syncs


@dataclass
class Beat:
    beat_id: str
    line: str                  # the exact script line, numerals spelled out
    speech: str = VO
    model: str = ""
    params: str = ""
    purpose: str = ""
    t2i: str = ""
    i2v: str = ""              # prose, or a JSON string for §35/§36
    i2v_is_json: bool = False
    camera_note: str = ""
    editor_note: str = ""
    face_state: str = ""       # FACE | NOFACE on B-roll (§30E Part 4)
    demo: str = ""             # DEMO name on product and mechanism beats (§30B)
    extras: dict = field(default_factory=dict)

    def header(self) -> str:
        """§26 item 1 — a prompt delivered without its line label is undelivered."""
        parts = [self.beat_id, f'{self.speech} "{self.line}"']
        if self.model:
            parts.append(f"{self.model}{'/' + self.params if self.params else ''}")
        if self.face_state:
            parts.append(self.face_state)
        if self.demo:
            parts.append(f"DEMO: {self.demo}")
        counts = []
        if self.t2i:
            counts.append(f"T2I {char_count(self.t2i)}")
        if self.i2v:
            counts.append(f"I2V {char_count(self.i2v)}")
        if counts:
            parts.append(" · ".join(counts) + " chars")
        return " · ".join(parts)

    def render(self) -> str:
        """The six-part video package (§26), each prompt in its own block (§16)."""
        out = [f"**{self.header()}**", ""]
        if self.purpose:
            out += [f"*Visual purpose:* {self.purpose}", ""]
        if self.t2i:
            out += ["T2I", "```text", self.t2i.strip(), "```", ""]
        if self.i2v:
            fence = "json" if self.i2v_is_json else "text"
            body = self.i2v.strip()
            if self.i2v_is_json:
                body = json.dumps(json.loads(body), indent=2, ensure_ascii=False)
            out += ["I2V", f"```{fence}", body, "```", ""]
        if self.camera_note:
            out += [f"*Camera / motion:* {self.camera_note}", ""]
        if self.editor_note:
            out += [f"*Editor note:* {self.editor_note}", ""]
        return "\n".join(out).rstrip() + "\n"


def act(beats: list[Beat], reconciliation: Reconciliation, title: str = "") -> str:
    """One act delivery: never merged prompts, and one reconciliation line at the end."""
    chunks = []
    if title:
        chunks.append(f"## {title}\n")
    for beat in beats:
        chunks.append(beat.render())
    chunks.append(f"**Reconciliation —** {reconciliation.line()}\n")
    if not reconciliation.delivered:
        chunks.append(
            f"> UNDELIVERED: {reconciliation.uncovered} phrase(s) uncovered. "
            "Uncovered must read zero (§27B).\n"
        )
    return "\n".join(chunks)


def validate(beat: Beat) -> list[str]:
    """What §16/§26 make undelivered, checked before the act ships."""
    problems = []
    if not beat.line:
        problems.append(f"{beat.beat_id}: no line label — a prompt delivered without it is undelivered (§26)")
    if not (beat.t2i or beat.i2v):
        problems.append(f"{beat.beat_id}: no prompt text — a description of a prompt is not a prompt (§16)")
    if beat.i2v and not beat.model:
        problems.append(f"{beat.beat_id}: no model string on the delivery header (§16)")
    if beat.i2v_is_json:
        try:
            parsed = json.loads(beat.i2v)
        except json.JSONDecodeError as error:
            problems.append(f"{beat.beat_id}: I2V JSON does not parse — valid JSON only (§37): {error}")
        else:
            problems += _json_shape(beat.beat_id, parsed)
    return problems


def _json_shape(beat_id: str, payload: dict) -> list[str]:
    """§37: camera stays nested; negatives stays a single comma-separated string."""
    problems = []
    camera = payload.get("camera")
    if camera is not None:
        if not isinstance(camera, dict):
            problems.append(f"{beat_id}: `camera` must stay nested with movement and framing separated (§37)")
        else:
            for key in ("movement", "framing"):
                if key not in camera:
                    problems.append(f"{beat_id}: camera.{key} missing (§37)")
    negatives = payload.get("negatives")
    if negatives is not None and not isinstance(negatives, str):
        problems.append(f"{beat_id}: `negatives` must be a single comma-separated string (§37)")
    if "duration" in payload and payload.get("type", "").upper() == "BR":
        problems.append(f"{beat_id}: never include duration anywhere in B-roll JSON (§27)")
    return problems


def correction(beat: Beat, also_corrected: list[str], now_invalid: list[str],
               section: str, one_line: str) -> str:
    """§34 — return only the corrected block, then one line, then stop."""
    out = [beat.render()]
    out.append(f"Fixed: {one_line}")
    if also_corrected:
        out.append(f"Also corrected for the same flaw: {', '.join(also_corrected)}")
    if now_invalid:
        out.append(f"Now invalid, reissue in one pass: {', '.join(now_invalid)}")
    out.append(f"Pending Amendment logged against {section}.")
    return "\n".join(out) + "\n"
