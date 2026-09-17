---
name: casting
description: Cast and lock characters — §19 avatar reference sheets, the §19 panel check, §19A eight-axis novelty clearance, §20 constraint sheets, §22D voice identity and the Voice Roster. Use when creating a narrator, side character, or recurring anonymous B-roll subject.
---

# Casting (§18 step 3)

**Every subject with two or more beats on the phrase inventory** gets a full sheet — the
narrator, every named side character, and every anonymous recurring B-roll subject
(`S-01`, `S-02`…). One-off subjects are not sheeted (§13).

This is a render dependency, not an approval. Generate, check, attach, keep going.

## 1. Clear the character before you render it (§19A)

Eight axes, every new character stated on all eight, cleared against the Roster Ledger at
**five of eight**. Derivation before appearance: the claim picks the life, the life picks
the face. Ship the axis table with the sheet.

## 2. Generate the sheet — one generation, nothing attached (§19)

```bash
pe call sheet --prompt sheets/narrator.txt
```

Route is `gpt_image_2_5`, `variant: sunburst`, `quality: high`, `resolution: 2k` — measured
V7.49.8. The three parameters are **never** left at their catalogue defaults, and the logged
job is read for all three. `gpt_image_2` at `high`/`2k` is the fallback.

Five photographs on one 9:16 canvas: top row front / true left profile / true right profile,
bottom row full-length back view and a face close-up. `SHEET-GRID` is pasted **verbatim** —
a layout described by content lets the model pick its own scale per panel, and it did.

Spend the words on **sameness**: same minute, same distance, same head size, same hair tone
and ponytail height, the same window on the same side in all five, nothing on the skin in one
panel that is not in the others.

```bash
pe string SHEET-GRID
pe string AVATAR-SHEET
pe string NEG-SHEET ; pe string NEG-GRID ; pe string NEG-DEFAULT-FACE
```

## 3. Panel check — a gate before the sheet is used anywhere

Close-up is the front panel · hair tone in all five · window same side, profiles lit opposite ·
wardrobe identical · nothing on the skin in one panel only · heads on one line, feet on one
line, true 90° profiles, nothing cut off · logged params `sunburst`/`high`/`2k`.

**Never attach a failing sheet.** Reroll only for a panel failure, never for taste once the
face has landed — with nothing attached, every reroll is a new person.

## 4. Read the identity off the render, never off the prompt (§7)

Markers, asymmetries and age features are transcribed from what came back. Then:

- speaking characters additionally get `VOICE-[CHAR]` (§22D, seven axes, roster-cleared on
  3+ axes against `GEN-DEFAULT-[sex]-[band]`) and a full §20 constraint sheet
- record the sheet's job id in `registries/subject.json` and the voice in `registries/voice.json`

`VOICE-[CHAR]` is pasted verbatim, never paraphrased, and goes **first** in `delivery`.
