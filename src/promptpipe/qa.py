"""E1 QA matrix — every check bound to an instrument, a threshold, an on-fail action.

Checks marked AUTO run here. AUTO-ASSIST and HUMAN checks are queued onto the
ledger with their on-fail action attached, so nothing is silently skipped.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import budget as budget_mod
from .tables import QA_BY_ID, QA_CHECKS


@dataclass
class Result:
    check: str
    status: str      # PASS | FAIL | QUEUED
    detail: str
    on_fail: str
    klass: str

    @property
    def ok(self) -> bool:
        return self.status == "PASS"

    def __str__(self) -> str:
        return f"{self.status:6} {self.check:22} {self.detail}"


def _spec(check_id: str):
    return QA_BY_ID[check_id]


def _result(check_id: str, ok: bool, detail: str) -> Result:
    _, _, _, klass, on_fail = _spec(check_id)
    return Result(check_id, "PASS" if ok else "FAIL", detail, on_fail, klass)


def run_auto(beat: dict, prompts: dict[str, str], job: dict | None = None) -> list[Result]:
    """The AUTO rows of E1, run over one beat before submission and after return.

    `beat`   — its act-map row.
    `prompts`— {"t2i": str, "i2v": str}.
    `job`    — the completed job record, where one exists.
    """
    results: list[Result] = []
    kling_direct = bool(beat.get("kling_direct"))

    for stage in ("t2i", "i2v"):
        text = prompts.get(stage)
        if not text:
            continue
        verdict = budget_mod.check_char_budget(text, kling_direct=kling_direct or stage == "i2v")
        results.append(_result("char_count", verdict.ok, f"{stage}: {verdict.detail}"))

    dialogue = beat.get("dialogue") or ""
    if dialogue:
        duration = int(beat.get("duration") or 0)
        pace = beat.get("pace") or "brisk"
        talking_while_doing = bool(beat.get("bound_move_word"))
        verdict = budget_mod.check_word_budget(dialogue, duration, pace, talking_while_doing)
        results.append(_result("word_budget", verdict.ok, verdict.detail))

    if job:
        passed = job.get("model_requested")
        logged = job.get("model_logged")
        if passed or logged:
            results.append(_result("model_run", passed == logged,
                                   f"passed {passed!r}, logged {logged!r}"))
        if job.get("preset_offered"):
            results.append(_result("preset_override", bool(job.get("declined_preset_id")),
                                   f"preset offered; declined_preset_id={job.get('declined_preset_id')!r}"))
        if beat.get("stage") == "i2v":
            results.append(_result("start_frame_completed",
                                   job.get("start_frame_status") == "completed",
                                   f"start frame status={job.get('start_frame_status')!r}"))

    tier = (beat.get("location_tier") or "").upper()
    if tier:
        has_plate = bool(beat.get("plate_job_id"))
        ok = not (tier in ("TRAVERSED", "INCIDENTAL") and has_plate)
        results.append(_result("location_tier", ok, f"{tier}, plate attached={has_plate}"))

    return results


# The AUTO rows this process can actually measure. Every other applicable row is
# queued rather than dropped — an unwired instrument is a queued check, not a pass.
IMPLEMENTED = {
    "char_count", "word_budget", "model_run", "preset_override",
    "start_frame_completed", "location_tier",
}


def queue_manual(beat: dict) -> list[Result]:
    """Every E1 row that applies to this beat and is not measured in-process."""
    queued: list[Result] = []
    beat_type = (beat.get("type") or "").upper()
    for check_id, instrument, threshold, klass, on_fail in QA_CHECKS:
        if check_id in IMPLEMENTED:
            continue
        if not _applies(check_id, beat, beat_type):
            continue
        label = klass if klass != "AUTO" else "AUTO (no instrument wired)"
        queued.append(Result(check_id, "QUEUED", f"{instrument} — {threshold}", on_fail, label))
    return queued


def _applies(check_id: str, beat: dict, beat_type: str) -> bool:
    state = (beat.get("product_state") or "absent").lower()
    register = (beat.get("register") or "").upper()
    table = {
        "inner_face_fixtures": state in ("worn", "demo") and (beat.get("frame_side") or "").lower() in ("rear", "turning"),
        "closure_sync": beat_type == "TH",
        "voice_drift": beat_type == "TH",
        "voice_separability": beat_type == "TH",
        "scene_hold": bool(beat.get("location_id")),
        "subject_hold": bool(beat.get("subject")) and str(beat.get("subject")).startswith("S-"),
        "face_state": beat_type == "BR",
        "geography_axis": bool(beat.get("geo_line_ref")),
        "mechanism_greyscale": beat_type == "MECH" or "ANAT" in register,
        "cycle_rate": "STRESS" in register,
        "broll_cut_delta": beat_type == "BR",
        "avatar_sheet_panels": beat_type == "SHEET",
        "candid_seed_light": beat_type in ("TH", "BR") and bool(beat.get("candid_seed")),
        "wordmark": state in ("held", "demo", "worn"),
        "feature_span_ratio": state in ("worn", "held", "demo"),
        "placement_ratio": state == "worn",
        "entry_latency": beat_type == "TH",
        "tts_gaps": beat_type == "TH",
        "face_skin_register": beat_type in ("TH", "BR"),
        "coverage": False,  # run at act level, not beat level
    }
    return table.get(check_id, False)


def matrix() -> list[tuple]:
    return list(QA_CHECKS)
