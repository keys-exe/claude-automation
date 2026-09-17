"""E9 build directory layout — one beat, one pair of files.

The tree is what makes §34 global corrections, coverage diffs and reissue passes
run as scripts over the tree, never as memory.
"""

from __future__ import annotations

import json
from pathlib import Path

from .ledger import Ledger
from .standards import load as load_standards

PRODUCT_SHEET_MD = """# Product Sheet — {name}

One per product. Stable across every build for that product (Appendix B).
Nothing in here invents a rule or overrides one; it fills a slot the Standards define.

## 1. Product name and category

## 2. The eight spec fields (§8), in order

## 3. Phrasing table
| intent | phrasing that failed, and what it produced | phrasing that works |
|---|---|---|
| | | |

## 4. Reference image registry
- Canonical reference set:
- Never attached as reference:
- Per-batch verification checklist:

## 5. Mechanism type and slots (§12A)
`[REGION]` · `[STACK]` · `[BONES]` · `[TARGET]` · `[SITE]`
`[SITE]` is derived from the placement lock below, never chosen per beat.
The attachment point it is *not*:

## 6. Mechanism claim (§12A)
Protection unless a new modulation block has been written. One per build.

## 7. Placement lock (§9A-P)
`[SITE]` · `[LANDMARK]` · `[OFFSET]` in units · side · contact geometry ·
`[BAND-MATERIAL]` · `[HARDWARE]` · `[BAND-INNER]` · landmarks `NEG-PLACE` excludes

## 8. Competitor archetypes (§10)

## 9. Buyer age band and cast profile (§13)

## 10. Claim register (§43A)
| claim | tier | source |
|---|---|---|

## 11. Standing negatives
Accumulated from observed failures, dated.

## 12. Pattern fills (V7.49.0)
Every PATTERN string filled here and imported, never retyped.
Measured ratios as numbers with tolerances, never adjectives (V7.47).
"""

PRODUCT_SHEET_PY = '''"""Machine half of the Product Sheet for {name} (Appendix B, V7.36).

Step 2 of §18 absorbs this file. Appendix E5 consumes SLOTS.
Every count check here fails loudly rather than shipping a long prompt.
"""

NAME = "{name}"

# --- E5 slot fills, verbatim -------------------------------------------------
SLOTS = {{
    "SITE": "",
    "LANDMARK": "",
    "OFFSET": "",
    "REGION": "",
    "STACK": "",
    "BONES": "",
    "TARGET": "",
    "BAND-MATERIAL": "",
    "HARDWARE": "",
    "BAND-INNER": "",
    "CONTACT": "",
    "NAMED-ASYMMETRIES": "",
    "REAR-PATH": "",
    "BAND-HEIGHT-RATIO": "",
    "LOAD-CADENCE": "",
    "FEATURE": "",
    "FRACTION": "",
}}

# --- Measured ratios, with tolerance (V7.47) ---------------------------------
RATIOS = {{
    # "feature_span_over_whole_width": (value, tolerance),
}}

# --- Locked strings, filled from the Standards patterns ----------------------
PLACE_LOCK = ""
ORIENT_LOCK = ""
NEG_PLACE = ""

# --- Verification checklist as assertions (§18 step 2) -----------------------
def verify():
    """Raises on anything that would invalidate every beat built against it."""
    missing = [name for name, value in SLOTS.items() if not value]
    assert not missing, f"unfilled Product Sheet slots: {{missing}}"
    for name, spec in RATIOS.items():
        assert len(spec) == 2, f"{{name}} needs (value, tolerance), not an adjective"


if __name__ == "__main__":
    verify()
    print(f"{{NAME}}: product sheet verified")
'''

BUILD_SHEET_MD = """# Build Sheet — {name}

One per build. Disposable (Appendix C).

1. Build type and act count (§3, §31):
2. Angle — what this build argues that others do not:
3a. Absorption Sheet (§42, seven parts):
3. Avatar reference sheet (§19):
4. Character constraint sheets (§20):
4a. Roster Ledger (§19A, eight axes, five-of-eight clearance):
5. Act map -> `act_map.json`
5a. Phrase inventory + coverage ledger -> `phrase_inventory.json`
6. Wardrobe map -> `wardrobe_map.json`
6a. Wardrobe Ledger (one outfit row per story day):
6b. Story-day map (§14A five-channel derivation pass):
7. Location Sheet library -> `location_sheets/`
7a. Scene Registry -> `registries/scene.json`
7b. Subject Registry -> `registries/subject.json`
8. Audio Part B library (§22C):
9. Surface library (§15A):
10. CapCut block -> `capcut_block.md`
11. Build-level open decisions:

## Locks resolved at step 2 (§18)
- mode and register:
- camera:
- format (§3A default fires silently — talking heads unless full B-roll stated):
- tools and model strings:
- mechanism claim:
- declared side:
"""

CAPCUT_MD = """# CapCut block (§40, §18 step 8)

Last and separate. Nothing here generates (§17).

## Cover points
## J-cuts
## Designed silences
## Sync triage
Standing lines (§28H): sync check at closure + stress word; constant offset -> slip; drift -> reissue.
## Motion graphics layer (§17A)
Annotate, never explain.
## Supplied-asset cut-ins
## Ambient audio bed
"""


def create(root: Path | str, name: str, force: bool = False) -> list[str]:
    root = Path(root)
    if root.exists() and any(root.iterdir()) and not force:
        raise FileExistsError(f"{root} is not empty; pass force=True to fill it anyway")

    created: list[str] = []

    def write(relative: str, content: str) -> None:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not force:
            return
        target.write_text(content, encoding="utf-8")
        created.append(relative)

    standards = load_standards()

    write("product_sheet.md", PRODUCT_SHEET_MD.format(name=name))
    write("product_sheet.py", PRODUCT_SHEET_PY.format(name=name))
    write("absorption_sheet.md", _absorption_sheet(name))
    write("build_sheet.md", BUILD_SHEET_MD.format(name=name))
    write("act_map.json", json.dumps(
        {"declared": {"side": "", "mechanism_claim": "", "format": "", "mode": ""}, "rows": []},
        indent=2) + "\n")
    write("phrase_inventory.json", json.dumps({"phrases": []}, indent=2) + "\n")
    write("wardrobe_map.json", json.dumps(
        {"outfits": {}, "capture_events": {}, "generic_pool": [], "signature_items": {}},
        indent=2) + "\n")
    for registry in ("roster", "voice", "scene", "subject"):
        write(f"registries/{registry}.json", json.dumps({}, indent=2) + "\n")
    write("location_sheets/.gitkeep", "")
    write("beats/.gitkeep", "")
    write("capcut_block.md", CAPCUT_MD)

    ledger = Ledger(root / "run_ledger.json")
    ledger.data["version_built_against"] = standards.version
    ledger.save()
    created.append("run_ledger.json")

    return created


def _absorption_sheet(name: str) -> str:
    return f"""# Absorption Sheet — {name}

The §42 seven-part protocol, in order, none skipped (§18 step 1).

## Part 1 — Measure before read
| metric | value |
|---|---|

## Part 2 — Structure map, in the build system's vocabulary

## Part 3 — Style Lock (set, not proposed)

## Part 4 — Script absorption
- reference phrase inventory:
- copy formula:
- voice fingerprint:
- beat map:

## Part 5 — Surfaced, not absorbed

## Part 6 — The beat-it plan

## Part 7 — Confirmation gate
"""
