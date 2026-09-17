---
name: correction
description: Apply the §34 correction protocol when the user flags a problem with a shot — corrected block only, global scan, retroactive reissue list, and a Pending Amendment logged the same turn. Use whenever the user says a beat is wrong, a render is off, or a rule needs changing.
---

# Correction protocol (§34)

When the user flags a problem with a specific shot:

1. Return **only** the corrected block, labelled with its beat ID, as a drop-in swap.
2. Do not restate surrounding beats.
3. Do not re-explain the system.
4. Confirm the fix in one line, then stop.

## The four properties, all four

**Global.** Scan every other beat for the same flaw and fix it everywhere, then say in one
line which other IDs were also corrected.

```bash
grep -rl "<the flawed phrasing>" beats/
```

**Retroactive.** Name which already-delivered IDs are now invalid and need reissuing, and
flag them on the ledger so the scan is computed and not remembered:

```bash
pe ledger reissues
```

**Permanent.** Never reintroduce a fixed flaw in new work. If the flaw came from a string,
the string is what changes.

**It must reach the document, with a deadline.** Say which section the correction changes and
**add it to the Pending Amendments table the same turn**. Without the table, corrections live
in chat and reach the document only by accident.

## Reissues run once

Where several sections invalidate the same beats, hold the reissue until all of them are
resolved and run **one pass, not two**.

## Both copies move together (§0)

The master file and the loaded project instructions are patched in the same action and to the
same version. A change that lands in one copy only has not shipped. If the file and the
instructions disagree, **the file is the source**.
