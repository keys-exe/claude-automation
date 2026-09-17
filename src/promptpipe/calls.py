"""E7 verified call templates — build the exact payload, never a remembered one.

This module emits the JSON an orchestrator hands to the generation tool. It does
not call anything: running a generation never replaces delivering the prompt
(§16), so the payload is an artefact too.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from .budget import char_count
from .tables import CALL_TEMPLATES

T2I_ROUTES = {"nano_banana_pro", "nano_banana_2", "gpt_image_2_5", "gpt_image_2"}
I2V_ROUTES = {"kling3_0", "wan_references", "seedance_omni"}
SHEET_ROUTE = "gpt_image_2_5"   # §19, measured V7.49.8


@dataclass
class Call:
    stage: str
    route: str
    tool: str
    params: dict
    warnings: list[str] = field(default_factory=list)
    note: str = ""

    def json(self) -> str:
        return json.dumps(self.params, indent=2, ensure_ascii=False)

    def __str__(self) -> str:
        head = f"{self.stage.upper()} · {self.route} · {self.tool}"
        body = self.json()
        tail = ""
        if self.note:
            tail += f"\nnote: {self.note}"
        for warning in self.warnings:
            tail += f"\nWARN: {warning}"
        return f"{head}\n{body}{tail}"


def t2i(prompt: str, route: str = "nano_banana_pro", medias: list[str] | None = None,
        aspect_ratio: str = "9:16", resolution: str = "2k") -> Call:
    key = f"t2i.{route}"
    if key not in CALL_TEMPLATES:
        raise KeyError(f"{route!r} is not an E7 T2I route ({', '.join(sorted(T2I_ROUTES))})")
    template = CALL_TEMPLATES[key]
    params = dict(template["params"])
    params["aspect_ratio"] = aspect_ratio
    params["resolution"] = resolution
    params["prompt"] = prompt
    if medias:
        params["medias"] = [{"role": template["media_role"], "value": m} for m in medias]

    warnings = []
    if route in ("gpt_image_2_5", "gpt_image_2") and (
        params.get("quality") != "high" or params.get("resolution") != "2k"
    ):
        warnings.append("quality and resolution both default low on GPT Image — never omit (§19)")
    return Call("t2i", route, template["tool"], params, warnings, template.get("note", ""))


def avatar_sheet(prompt: str) -> Call:
    """§19: one generation, nothing attached, sunburst/high/2k, and read the logged job."""
    call = t2i(prompt, route=SHEET_ROUTE, medias=None)
    call.params["variant"] = "sunburst"
    call.params["quality"] = "high"
    call.params["resolution"] = "2k"
    call.note = ("The sheet is generated once and locked. Reroll only for a panel "
                 "failure, never for taste (§19). Read the logged job for all three params.")
    return call


def i2v(prompt: str, route: str = "kling3_0", start_image_job_id: str | None = None,
        duration: int = 5, references: list[str] | None = None,
        audios: list[str] | None = None, declined_preset_id: str | None = None,
        seed: int | None = None, kling_direct: bool = False) -> Call:
    key = f"i2v.{route}"
    if key not in CALL_TEMPLATES:
        raise KeyError(f"{route!r} is not an E7 I2V route ({', '.join(sorted(I2V_ROUTES))})")
    template = CALL_TEMPLATES[key]
    params = dict(template["params"])
    params["prompt"] = prompt
    params["duration"] = duration
    warnings: list[str] = []

    if route == "kling3_0":
        if not start_image_job_id:
            warnings.append("no start_image — an I2V beat without a completed seed is not submittable (§5)")
        else:
            params["medias"] = [{"role": "start_image", "value": start_image_job_id}]
        if declined_preset_id:
            params["declined_preset_id"] = declined_preset_id
        else:
            warnings.append("declined_preset_id is mandatory on dark-field and any preset-matched beat (§5)")
    elif route == "wan_references":
        params["images"] = references or []
        if audios:
            params["audios"] = audios
        if seed is not None:
            params["seed"] = seed
        if not references:
            warnings.append("references mode is the default on Wan 3.0 — no images passed (§4)")
    elif route == "seedance_omni":
        params["images_list"] = references or []
        if audios:
            params["audios_list"] = audios
        if duration in (None, "auto"):
            warnings.append("duration is never 'auto' on Seedance (E7)")

    if kling_direct:
        count = char_count(prompt)
        if count > 2500:
            warnings.append(f"{count} chars minified > 2,500 Kling-direct ceiling (§37)")
    return Call("i2v", route, template["tool"], params, warnings, template.get("note", ""))


def wait(job_ids: list[str]) -> Call:
    """E7: jobs_wait on every T2I before its I2V. Batch order never implies completion order."""
    return Call("wait", "jobs_wait", "jobs_wait", {"job_ids": job_ids}, [],
                "Batch order never implies completion order — on every route.")
