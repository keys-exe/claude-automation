---
name: beat-write
description: Write and gate a single beat — T2I seed plus I2V prompt — against the registers, string library, budgets and QA matrix. Use when writing, fixing, rerolling or checking one beat, or when asked for a prompt for a specific shot.
---

# Write one beat

## 1. Read the row, not your memory

```bash
pe check <BEAT-ID>        # what the act map says, and every pre-submission gate
```

The row decides register, rig, framing step, energy, valence, story day, capture event,
product state and visibility. If the row is missing a field, fix the act map first — step 5
is where the expensive things are cheap.

## 2. Assemble from the string library, never freehand

```bash
pe strings --section App.A          # every locked string, with its declared count
pe string CAP-A                     # print one verbatim
pe string PLACE-LOCK --fill SIDE=left --fill REGION=forearm
```

Invariant content is compressed once, tested once and locked. Paste NORMATIVE blocks
verbatim with only the named substitutions; never paraphrase one to save characters.

**§6 relocation:** anything that is a property of the frame lives in T2I, which has no
ceiling. Only change-over-time survives in I2V. Restating capture, lighting, surface,
wardrobe, geometry or style in I2V spends ~615 characters describing what the model can
already see — `INHERIT-CAP` does the job in 146.

## 3. Gate before submitting

`pe check` enforces, per §37/§28H/E1/E5:

- minified character count against the 2,500 Kling-direct ceiling
- word budget against the §28H table — over budget takes the longer duration or gets cut,
  **never squeezed**
- banned punctuation (ellipses, em-dashes)
- a sync anchor: a bound move word, or a §28F closure word
- unfilled slot tokens **and** leftover bracketed fill instructions
- the slots E5 marks mandatory on this beat class

Fix every failure before generating. A failing gate is cheaper than a reroll.

## 4. Build the call, then wait

```bash
pe call t2i --route nano_banana_pro --prompt beats/BR-01.t2i.txt
pe call i2v --route kling3_0 --prompt beats/BR-01.i2v.json \
    --start-image <completed T2I job id> --declined-preset-id <id> --duration 5
```

A start frame must be **completed**, not merely submitted. Batch order never implies
completion order — `jobs_wait` on every T2I before its I2V, on every route.

## 5. Deliver

Six parts, in order (§26): line label header → visual purpose → T2I block → I2V block →
camera/motion note → editor note. Each prompt in its own fenced block; never merged.
A prompt delivered without its line label is undelivered.

## 6. When it comes back wrong

```bash
pe qa <BEAT-ID>                     # AUTO rows run; HUMAN rows queue with their remedy
pe fail <BEAT-ID> "<what happened>" # E2 class, retry budget, decision
```

Two automatic rerolls per failure class, then the beat queues for a human with its failure
history attached. A retry never changes the prompt silently — a changed prompt is a
delivered iteration.
