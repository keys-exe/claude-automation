"""E3 run ledger — the build's state file. Computed, never hand-maintained.

The ledger is the source for §34 global scans, reissue passes, resume after
interruption, and the Open Decisions counts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LEDGER_NAME = "run_ledger.json"

BEAT_FIELDS = {
    "beat_id": "", "phrase_ids": [], "t2i_prompt_path": "", "t2i_job_id": "",
    "t2i_status": "", "t2i_qa": {}, "i2v_prompt_path": "", "i2v_job_id": "",
    "i2v_status": "", "i2v_qa": {}, "retries": [], "attachments": [],
    "delivered": False, "reissue_flag": None,
}

BUILD_FIELDS = {
    "plates": {}, "subjects": {}, "story_days": {}, "capture_events": {},
    "declared": {}, "version_built_against": "",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Ledger:
    def __init__(self, path: Path | str, data: dict | None = None):
        self.path = Path(path)
        self.data: dict[str, Any] = data or {"beats": {}, **{k: _copy(v) for k, v in BUILD_FIELDS.items()}}

    # --- persistence ------------------------------------------------------

    @classmethod
    def load(cls, path: Path | str) -> "Ledger":
        path = Path(path)
        if not path.exists():
            return cls(path)
        return cls(path, json.loads(path.read_text(encoding="utf-8")))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
            encoding="utf-8",
        )

    # --- beat rows --------------------------------------------------------

    def beat(self, beat_id: str) -> dict:
        beats = self.data.setdefault("beats", {})
        if beat_id not in beats:
            row = {k: _copy(v) for k, v in BEAT_FIELDS.items()}
            row["beat_id"] = beat_id
            beats[beat_id] = row
        return beats[beat_id]

    def update(self, beat_id: str, **fields) -> dict:
        row = self.beat(beat_id)
        unknown = [k for k in fields if k not in BEAT_FIELDS]
        if unknown:
            raise KeyError(f"not E3 ledger fields: {', '.join(unknown)}")
        row.update(fields)
        return row

    def record_retry(self, beat_id: str, failure_class: str, action: str) -> dict:
        row = self.beat(beat_id)
        row["retries"].append({"class": failure_class, "action": action, "ts": _now()})
        return row

    def retries_for(self, beat_id: str, failure_class: str) -> int:
        return sum(1 for r in self.beat(beat_id)["retries"] if r["class"] == failure_class)

    def attach(self, beat_id: str, role: str, media_or_job_id: str) -> dict:
        row = self.beat(beat_id)
        row["attachments"].append({"role": role, "media_or_job_id": media_or_job_id})
        return row

    def flag_reissue(self, beat_id: str, section: str, reason: str) -> dict:
        """§34: corrections are retroactive — name which delivered IDs are now invalid."""
        row = self.beat(beat_id)
        row["reissue_flag"] = {"section": section, "reason": reason, "ts": _now()}
        return row

    # --- computed views ---------------------------------------------------

    def pending_human(self) -> list[str]:
        out = []
        for beat_id, row in self.data.get("beats", {}).items():
            for stage in ("t2i_qa", "i2v_qa"):
                for check, result in (row.get(stage) or {}).items():
                    if result in ("HUMAN", "human", "queued"):
                        out.append(f"{beat_id}:{stage}:{check}")
        return sorted(out)

    def undelivered(self) -> list[str]:
        return sorted(b for b, r in self.data.get("beats", {}).items() if not r.get("delivered"))

    def reissues(self) -> dict[str, dict]:
        return {b: r["reissue_flag"] for b, r in self.data.get("beats", {}).items()
                if r.get("reissue_flag")}

    def blocked_on_start_frame(self) -> list[str]:
        """E1: a start frame must be completed, not merely submitted (§5)."""
        return sorted(
            beat_id for beat_id, row in self.data.get("beats", {}).items()
            if row.get("i2v_job_id") and row.get("t2i_status") != "completed"
        )

    def summary(self) -> dict:
        beats = self.data.get("beats", {})
        return {
            "beats": len(beats),
            "delivered": sum(1 for r in beats.values() if r.get("delivered")),
            "undelivered": len(self.undelivered()),
            "pending_human": len(self.pending_human()),
            "reissues": len(self.reissues()),
            "blocked_on_start_frame": len(self.blocked_on_start_frame()),
            "version_built_against": self.data.get("version_built_against", ""),
        }


def _copy(value):
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, list):
        return list(value)
    return value
