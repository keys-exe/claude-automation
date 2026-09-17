# claude-automation — the machine half of the Global Standards

This repo automates one workflow: building realistic ads, VSLs, B-roll and talking heads
against **AI Prompt Engineer — Global Standards V7.49.8** (`standards/CURRENT.md`).

## The one rule that governs everything else

`standards/CURRENT.md` is the only standard. There is no external skill layer, no house-style
file, no secondary guide. **If a rule is not there, it does not exist** — including anything
auto-loaded alongside it. The skills in `.claude/skills/` are navigation, not authority: they
tell you which section to read and which command to run. They never restate a threshold.

Order of authority, highest wins, and a lower layer never silently overrides a higher one:

1. Reference images (§7) · 2. Product Sheet (§8, App. B) · 3. Locked visual and performance
standards · 4. Script · 5. Build Sheet (App. C) · 6. Locked defaults (§44)

Where a script line contradicts a product spec or a visual standard, the render follows the
higher layer and **the line is flagged to the advertiser — it is not rewritten.**

## Never answer a threshold from memory

Every number in the Standards is available from `pe`. Ask the tool:

```bash
pe steps              # the §18 eight-step flow, and where the single gate is
pe status             # every gate at once, for the build in the current directory
pe string CAP-A       # a locked string, verbatim, with its declared count
pe strings            # all 239, with counts and a `!` where a count has drifted
pe check BR-01        # pre-submission gates on one beat
pe qa BR-01           # E1 matrix: AUTO rows run, everything else queues
pe coverage           # §27B audit and the reconciliation line
pe actmap             # E4 schema, story-day chain, product first appearance
pe call i2v --route kling3_0 --prompt beats/BR-01.i2v.json --start-image <job>
pe fail BR-01 "came back plastic"   # E2 class, retry budget, decision
pe lint               # E10 doc-lint over the Standards
```

## Build layout (E9)

One beat, one pair of files, so §34 global corrections, coverage diffs and reissue passes run
as scripts over the tree and never as memory.

```
<build>/
  product_sheet.md  product_sheet.py     absorption_sheet.md  build_sheet.md
  act_map.json      phrase_inventory.json  wardrobe_map.json
  location_sheets/  registries/{roster,voice,scene,subject}.json
  run_ledger.json   beats/{BEAT-ID}.t2i.txt  beats/{BEAT-ID}.i2v.json
  capcut_block.md
```

`pe init "<product>"` creates it, stamped with the Standards version it was built against.

## Standing rules while working in this repo

- **The prompt is the deliverable** (§16). Running a generation never replaces delivering the
  prompt. A description of a prompt is not a prompt.
- **A beat without its line label is undelivered** (§26). An act without its reconciliation
  line is undelivered (§27B). Uncovered must read zero.
- **`CUT` is not a disposition.** A line is never removed to solve a coverage problem —
  `BLOCKED` carries its reason and its section, and the advertiser moves it.
- **Two automatic rerolls per beat per failure class, then a human** (E2). Record every
  failure through `pe fail` so the budget is computed, not remembered.
- **Corrections are global, retroactive, permanent, and reach the document the same turn**
  (§34). Use the `correction` skill; do not improvise the shape of a fix.
- **Nothing that names a product, brand, body region, character or location enters
  `standards/`.** That content is Product Sheet or Build Sheet.

## Working on the tooling

```bash
pip install -e .          # web sessions do this automatically via the SessionStart hook
python -m pytest -q
```

`src/promptpipe/tables.py` is the only place figures from the Standards are transcribed, and
every entry carries its section. When a Standards cut moves a threshold, that file is what
changes — and `pe lint` is what proves the cut is clean before it ships.
