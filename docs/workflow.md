# The workflow, end to end

The §18 eight-step flow, with the command that closes each step. Steps 1–5 ship as one
opening delivery — nothing inside it waits. **Step 6 is the only gate.**

```bash
pip install -e .
pe init "Product Name"       # E9 build tree, stamped with the Standards version
```

## Step 1 — Absorb the inspo video (DET)

Skill: `absorb-reference`. The §42 seven-part protocol into `absorption_sheet.md`.
Style Lock is **set, not proposed**.

## Step 2 — Absorb script, product, Product Sheet (DET)

```bash
pe split script.txt --write
pe coverage                  # every row still needs a disposition at this point
```

`pe split` is a mechanical pass over the script **as written** — sentence ends, clause
boundaries, and the list-of-nouns rule that splits `"Braces, creams, magnets, patches."` into
four beats with no exceptions. The triggers that are not mechanical — a tone shift mid
sentence, a punchline landing — are tagged `REVIEW` rather than guessed at, and short
shift-less clauses are tagged `merge-candidate` so §27's anti-stutter rule is applied
deliberately.

Fill in the `.py` half of the Product Sheet here. `verify()` refuses to pass while a slot is
empty, which is what stops a build running against a half-specified product.

Resolve every lock: mode and register, camera, format, tools and model strings, mechanism
claim, declared side.

## Step 3 — Cast everyone who recurs (DET)

Skill: `casting`.

```bash
pe call sheet --prompt sheets/narrator.txt
```

Route, variant, quality and resolution are fixed by §19 and the tool will not let the three
GPT Image parameters fall back to their catalogue defaults, which is the failure that returns
a low-resolution sheet that looks fine until the close-up panel.

## Step 4 — Location maps (DET)

The §30C derivation pass. Plates for PLATED locations only. `pe qa` flags a plate attached to
a TRAVERSED or INCIDENTAL beat.

## Step 5 — Act map and wardrobe map, together (DET)

```bash
pe actmap
```

Enforces the E4 schema, including the failure E4 was written to remove: a row carrying a
`wardrobe_ref` but no `story_day` — the ledger keyed to something the map did not have. It
also fails an act map on which the product never appears, because the first appearance is
cheap to locate here and expensive to locate at beat 74.

## Step 6 — Hooks, one by one (**the gate**)

Serial: deliver → generate → first-frame check → confirm → next. The only place the pipeline
waits for a person.

## Step 7 — B-roll and body acts (DET)

Skill: `beat-write`. Per beat:

```bash
pe check BR-06                                       # before generating
pe call t2i --route nano_banana_pro --prompt beats/BR-06.t2i.txt
pe call i2v --route kling3_0 --prompt beats/BR-06.i2v.json \
    --start-image <completed T2I job id> --declined-preset-id <id>
pe qa BR-06                                          # after it comes back
pe fail BR-06 "<what happened>"                      # when it comes back wrong
```

Each act delivery ends on its §27B reconciliation line:

```bash
pe coverage
```

## Step 8 — CapCut block (DET)

Last and separate. Nothing here generates.

---

## The checks, and where each comes from

| check | section | where it runs |
|---|---|---|
| minified character count vs the 2,500 ceiling | §37, E1 | `pe check`, `pe qa`, `pe call --kling-direct` |
| word budget vs the §28H table | §28H, E1 | `pe check`, `pe qa` |
| banned punctuation (ellipses, em-dashes) | §28H | `pe check` |
| a sync anchor — bound move word or closure word | §28H | `pe check` |
| unfilled slot tokens and residual bracket instructions | E5 | `pe check` |
| slots mandatory on a beat class (worn, rear, stress) | E5 | `pe check` |
| logged model vs passed model string | E1 | `pe qa` (with a job record) |
| start frame completed, not merely submitted | §5, E1 | `pe qa`, `pe ledger stalled` |
| preset declined with an id | §5, E1 | `pe qa`, `pe call` |
| plate attached to a TRAVERSED beat | §30C 1a | `pe qa` |
| every phrase carries a disposition; uncovered = 0 | §27B | `pe coverage`, `pe status` |
| beat-ID contiguity | §27B | `pe coverage` |
| `story_day` + `capture_event_id` on every row | E4 | `pe actmap` |
| one outfit row per story day | §14A W4 | `pe actmap` |
| product first appearance located | §18 step 5 | `pe actmap` |
| two rerolls per failure class, then a human | E2 | `pe fail` |
| Appendix A counts, NORMATIVE IDs, E5 manifest, retired strings | E10 | `pe lint` |

Everything the tool cannot measure in-process — OCR on a wordmark, a pixel ratio, a
greyscale legibility read, a blind voice listen — is **queued with its on-fail action
attached** rather than quietly passed. `pe qa` labels those `AUTO (no instrument wired)`
so an unwired instrument never reads as a green check.

## The worked example

`examples/demo-build/` is a complete tree: a five-line script split into nine phrases, all
nine dispositioned, a nine-row act map across three story days and five capture events, a
wardrobe map, and one fully written beat (`BR-06`) assembled from locked strings.

```console
$ cd examples/demo-build && pe status
Standards v7.49.8 · doc-lint: 39 fail, 24 warn
Coverage: P-001–P-009 → 9 beats · merged: none · TH-carried: TH-01, TH-02 · uncovered: 0 · blocked: 0 · unpaid plants: none
Act map: 9 rows · 0 problem(s)
Ledger: 1 beats · 1 undelivered · 1 queued for human · 0 reissue flag(s)
```
