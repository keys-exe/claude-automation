# claude-automation

Appendix E of the **AI Prompt Engineer Global Standards V7.49.8** made executable: a web
console, a CLI, and the Claude Code layer that drives the §18 build flow.

**Beat Console — https://claude.ai/artifact/Tg8gix6v7GgWyhozD4gDGP**
The same gates in a browser, no install. Split a script into phrases, disposition every one,
build the act map, write beats with the character and word budgets live, and search all 239
locked strings. Export drops straight into a build tree. Source in [`web/`](web/).

The Standards describe how ads, VSLs, B-roll and talking heads are built. Appendix E is the
machine half — a QA matrix bound to instruments, a failure taxonomy with retry budgets, a run
ledger, an act-map schema, a slot manifest, a duration function, verified call templates and a
doc-lint. This repo implements all of it as a CLI (`pe`) and wires it into Claude Code.

## Install

On **claude.ai/code** there is nothing to install — a `SessionStart` hook sets the
container up on every session and `pe` is on the PATH when you start typing.

On your own machine:

```bash
pip install -e .
pe steps
```

## What it does

**Reads the Standards rather than remembering them.** All 239 Appendix A strings are parsed
out of the document with their declared character counts, their slot tokens and the section
they belong to.

```console
$ pe string INHERIT-CAP
# INHERIT-CAP (§App.A) — declared 146, filled 146
Capture characteristics exactly as in the start frame — same tone-mapping, same noise, same
colour temperature. No grading change across the clip.
```

**Gates a beat before it costs a generation.** Character count on the minified string against
the 2,500 Kling-direct ceiling, word budget against the §28H table, banned punctuation, a sync
anchor, unfilled slot tokens, leftover bracketed fill instructions, and the slots E5 marks
mandatory on that beat class.

```console
$ pe check BR-04
i2v: FAIL  char_count: 2731 > 2500 minified
      -> Trim ladder (§37), recount — over by 231
FAIL  word_budget: 11 words > 9 at brisk/5s
      -> raise duration to 10s (E7) — never squeeze
BR-04: 2 gate(s) failed
```

**Keeps coverage honest.** The §27B ledger: every phrase carries a disposition, uncovered
reads zero or the act is undelivered, and the reconciliation line is computed.

**Makes the retry budget real.** `pe fail` walks the E2 taxonomy — two automatic rerolls per
beat per failure class, then the beat queues for a human with its failure history attached.

**Lints a version cut.** `pe lint` runs E10 over the document: count drift, unresolved
NORMATIVE IDs, slot tokens missing from the E5 manifest, retired phrases and IDs surviving
outside a retirement notice, changelog depth, Pending Amendments, Open Decisions counts.

On the shipped V7.49.8 it finds **39 character-count drifts and 24 slot tokens absent from the
E5 manifest** — real findings against the current cut, listed in `docs/lint-findings.md`.

## Claude Code layer

Six skills that navigate the Standards (`vsl-build`, `beat-write`, `absorb-reference`,
`casting`, `correction`, `standards-cut`), six slash commands (`/status`, `/check`,
`/reconcile`, `/lint`, `/correct`, `/strings`), and a `PostToolUse` hook that gates any beat
prompt the moment it is written.

See `CLAUDE.md` for the working rules and `docs/workflow.md` for the end-to-end walkthrough.

## Layout

| path | what |
|---|---|
| `standards/CURRENT.md` | the Standards — the only standard |
| `src/promptpipe/standards.py` | parser: strings, counts, slots, sections |
| `src/promptpipe/tables.py` | the only transcribed figures, each with its section |
| `src/promptpipe/{budget,slots,coverage,actmap,ledger,qa,retry,calls,deliver,doclint}.py` | E1–E10 |
| `src/promptpipe/cli.py` | `pe` |
| `.claude/` | skills, commands, hook |
| `examples/demo-build/` | a worked build tree |
