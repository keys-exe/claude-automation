---
name: vsl-build
description: Drive a full ad/VSL build through the §18 eight-step flow against the Global Standards — absorption, phrase inventory, casting, locations, act map, hooks gate, B-roll acts, CapCut block. Use when the user asks to build, start, or continue a VSL, ad, UGC or B-roll build, or names a script, product or inspo video to work from.
---

# Build a VSL / ad against the Global Standards

The Standards are at `standards/CURRENT.md`. **If a rule is not there, it does not exist.**
Order of authority, highest first: reference images → Product Sheet → locked visual and
performance standards → script → Build Sheet → locked defaults (§44).

All deterministic checks run through `pe` (`pip install -e .` once). Never re-derive a
threshold from memory — ask the tool.

## Before anything

```bash
pe steps          # the eight steps and where the single gate is
pe status         # every gate at once, for a build already under way
```

If `pe status` warns the ledger and the Standards have drifted, say so and stop until
the user decides which is authoritative (§34 — the file is the source).

## The flow

Steps 1–5 ship as **one opening delivery**. Nothing inside it waits. Step 6 is the only
gate. Do not invent gates; do not stop to ask for approval at 3, 4 or 5.

### 1 — Absorb the inspo video (DET)
Run the `absorb-reference` skill. Output: `absorption_sheet.md`, Style Lock **set, not proposed**.

### 2 — Absorb script, product, Product Sheet (DET)
- Create the `.md` + `.py` Product Sheet pair where absent (`pe init <name>` scaffolds both).
- Run the §43A claims pass: every figure tiered before anything builds against it.
- Build the phrase inventory — a mechanical pass over the script **as written**:
  ```bash
  pe split script.txt --write
  ```
  Then confirm the non-mechanical split triggers the tool flags `REVIEW` (tone shift,
  punchline) and fold the `merge-candidate` rows it names. The script is never edited to
  solve a build problem.
- Resolve **every lock** here: mode and register, camera, format, tools and model strings,
  mechanism claim, declared side. Write them into `build_sheet.md` and `act_map.json`'s
  `declared` block.

### 3 — Cast everyone who recurs (DET, a render dependency, not an approval)
Run the `casting` skill. Every subject with two or more beats on the step-2 inventory gets
a §19 sheet through the panel check. Send it, then go straight on.

### 4 — Location maps (DET)
The §30C derivation pass over the phrase inventory. Plates for **PLATED locations only** —
never INCIDENTAL or TRAVERSED. The location set closes here; a later addition is a gated
redress. Send it, then go straight on.

### 5 — Act map and wardrobe map, together (DET)
Fill `act_map.json` rows on the E4 schema and `wardrobe_map.json` on §14A. Then:
```bash
pe actmap        # E4 schema, story_day/capture_event chain, first appearance
pe coverage      # §27B audit + the reconciliation line
```
Both must come back clean. `story_day` and `capture_event_id` are mandatory on every row.

### 6 — Hooks, one by one (AC → **HUMAN GATE**)
Serial and only serial: deliver → generate → first-frame check → confirm → next.
This is the one place you wait for the user. Confirmed renders feed the Scene and
Subject registries as they land.

### 7 — B-roll and body acts (DET)
Per beat, run the `beat-write` skill. Each act delivery ends on its §27B reconciliation
line — an act delivered without it is undelivered.

### 8 — CapCut block (DET)
Last and separate. Nothing here generates.

## Standing rules while building

- **The prompt is the deliverable** (§16). Running a beat and describing the result leaves
  the user with an image and no asset. Every generated beat ships its full prompt in a
  fenced block with model string, aspect ratio, resolution or duration, and char count.
- **Uncovered reads zero or the act is undelivered** (§27B). `BLOCKED` is reported, never
  resolved. `CUT` is not an available disposition.
- **Two automatic rerolls per beat per failure class, then a human** (E2). Record every
  failure with `pe fail <beat> "<signal>"` so the budget is real and not remembered.
- Conflicts between layers are surfaced at the gate they belong to, stated once with a
  recommendation, and resolved before the affected beats are written.
