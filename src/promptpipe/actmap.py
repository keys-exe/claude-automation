"""E4 act-map row schema, and the four things §18 step 5 is where you catch."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .tables import (
    ACT_MAP_FIELDS,
    ACT_MAP_REQUIRED,
    BEAT_TYPES,
    ENERGY,
    OWNERSHIP,
    PRODUCT_STATES,
    VALENCE,
    VISIBILITY,
)


@dataclass
class ActMap:
    rows: list[dict]
    declared: dict
    path: Path | None = None

    def by_id(self, beat_id: str) -> dict | None:
        for row in self.rows:
            if row.get("beat_id") == beat_id:
                return row
        return None

    def story_days(self) -> set[str]:
        return {str(row.get("story_day")) for row in self.rows if row.get("story_day")}

    def capture_events(self) -> dict[str, list[str]]:
        events: dict[str, list[str]] = {}
        for row in self.rows:
            event = row.get("capture_event_id")
            if event:
                events.setdefault(str(event), []).append(row.get("beat_id", "?"))
        return events


def load(path: Path | str) -> ActMap:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("rows", data if isinstance(data, list) else [])
    return ActMap(rows=rows, declared=data.get("declared", {}) if isinstance(data, dict) else {},
                  path=Path(path))


def save(act_map: ActMap, path: Path | str) -> None:
    payload = {"declared": act_map.declared, "rows": act_map.rows}
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate(act_map: ActMap, wardrobe: dict | None = None) -> list[str]:
    """Every rule E4 states, plus the §14A W4 resolution chain."""
    problems: list[str] = []
    seen_ids: set[str] = set()

    for index, row in enumerate(act_map.rows, start=1):
        label = row.get("beat_id") or f"row {index}"

        for name in ACT_MAP_REQUIRED:
            if not row.get(name) and row.get(name) != 0:
                problems.append(f"{label}: missing required field {name!r} (E4)")

        if row.get("beat_id") in seen_ids:
            problems.append(f"{label}: duplicate beat_id")
        seen_ids.add(row.get("beat_id"))

        problems += _enum(label, row, "type", BEAT_TYPES)
        problems += _enum(label, row, "energy", ENERGY, optional=True)
        problems += _enum(label, row, "valence", VALENCE, optional=True)
        problems += _enum(label, row, "ownership", OWNERSHIP, optional=True)
        problems += _enum(label, row, "product_state", PRODUCT_STATES)
        problems += _enum(label, row, "visibility", VISIBILITY)

        unknown = [key for key in row if key not in ACT_MAP_FIELDS]
        if unknown:
            problems.append(f"{label}: fields not in the E4 schema: {', '.join(sorted(unknown))}")

        # E4: a row carrying a wardrobe_ref but no story_day is the failure
        # this correction removes.
        if row.get("wardrobe_ref") and not row.get("story_day"):
            problems.append(f"{label}: wardrobe_ref with no story_day (E4)")

        if row.get("type") == "TH" and not row.get("duration"):
            problems.append(f"{label}: talking head with no duration (§28H gate)")

        if wardrobe is not None and row.get("story_day"):
            day = str(row["story_day"])
            outfits = wardrobe.get("outfits", {})
            if day not in outfits:
                problems.append(f"{label}: story_day {day!r} resolves to no outfit row (§14A W4)")

    problems += _first_appearance(act_map)
    problems += _wardrobe_one_outfit(wardrobe)
    return problems


def _enum(label: str, row: dict, field: str, allowed: tuple, optional: bool = False) -> list[str]:
    value = row.get(field)
    if value in (None, ""):
        return [] if optional else []
    if value not in allowed:
        return [f"{label}: {field}={value!r} not one of {', '.join(allowed)}"]
    return []


def _first_appearance(act_map: ActMap) -> list[str]:
    """§18 step 5: the product's first appearance is located here, not at beat 74."""
    for row in act_map.rows:
        if (row.get("product_state") or "absent") != "absent":
            return []
    if act_map.rows:
        return ["act map: no beat carries the product — first appearance unlocated (§9, §18 step 5)"]
    return []


def _wardrobe_one_outfit(wardrobe: dict | None) -> list[str]:
    """E10: every story day resolves to exactly one outfit row (§14A W4)."""
    if not wardrobe:
        return []
    problems = []
    for day, outfit in (wardrobe.get("outfits") or {}).items():
        if isinstance(outfit, list) and len(outfit) != 1:
            problems.append(f"story day {day!r} carries {len(outfit)} outfit rows; a story day has exactly one (§14A)")
        if isinstance(outfit, dict):
            missing = [slot for slot in ("BASE", "MID", "OUTER", "LOWER", "FOOT", "ACCENT")
                       if slot not in outfit]
            if missing:
                problems.append(f"story day {day!r} outfit missing layers: {', '.join(missing)} (§14A)")
    return problems


def blank_row(beat_id: str, **overrides) -> dict:
    row = {name: "" for name in ACT_MAP_FIELDS}
    row["beat_id"] = beat_id
    row["phrase_ids"] = []
    row["claims"] = []
    row.update(overrides)
    return row
