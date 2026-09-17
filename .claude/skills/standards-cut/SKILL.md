---
name: standards-cut
description: Cut a new version of the Global Standards — state the change first, patch both copies, empty Pending Amendments, run E10 doc-lint, and refuse to ship a cut that fails. Use when amending, versioning, or releasing the standards document.
---

# Cut a Standards version (§0, §34, E10)

## 1. State the change before making it

Name the proposed change and **every section it affects**, then make it. No silent edits.

## 2. Patch both copies in the same action

The master file (`standards/CURRENT.md`) and the loaded project instructions move together,
to the same version. A cut that patches only one copy has not shipped.

## 3. Empty Pending Amendments

The table empties at each version cut. Every locked correction written in, or the cut is not
the cut it claims to be.

## 4. Run doc-lint — a cut failing lint does not ship

```bash
pe lint
```

The checks, all computed:

- every Appendix A string has a count and the count matches its block
- every `NORMATIVE —` ID resolves to a defined string
- every slot token appears in the E5 manifest
- §18 and §31 agree · §44 numbering is ordered
- Open Decisions counts equal their lists
- every act-map row carries a `story_day` and a `capture_event_id`; every capture event
  resolves to a story day; every story day resolves to exactly one outfit row (§14A W4)
- no retired phrase and no retired string ID survives outside a retirement notice
- changelogs = current + one prior

## 5. Boundaries that do not move

Nothing that names a product, brand, body region, character or location enters the
Standards. If it names a thing, it is a Product Sheet or Build Sheet entry.

A Product Sheet or Build Sheet fills a slot the Standards define. It never invents a rule,
never overrides one, and never adds a category the Standards do not already have.

## 6. A new section is not locked until it names its field

Claims are marked **measured** or **unverified**. Never let a derived claim sit unmarked
beside a measured one.
