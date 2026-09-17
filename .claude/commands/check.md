---
description: Pre-submission gates on one beat (char count, word budget, slots, sync anchor)
argument-hint: <BEAT-ID>
---
Run `pe check $1` and `pe qa $1`.

Report every failure with the section it comes from and the fix. Then, if the beat is clear,
print the E7 call payloads with `pe call`. Do not submit anything until every gate passes.
