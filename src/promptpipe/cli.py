"""`pe` — one command per gate in the §18 flow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import actmap, budget, calls, coverage, deliver, doclint, qa, retry, scaffold, slots
from .ledger import Ledger
from .standards import load as load_standards
from .tables import BUILD_STEPS, QA_CHECKS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pe",
        description="Prompt-engineering pipeline: Appendix E of the Global Standards, executable.",
    )
    parser.add_argument("--build", default=".", help="build directory (E9 layout)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create an E9 build tree")
    p.add_argument("name")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("steps", help="print the §18 eight-step flow and where the gate is")
    p.set_defaults(func=cmd_steps)

    p = sub.add_parser("lint", help="E10 doc-lint over the Standards")
    p.add_argument("--path", default=None)
    p.set_defaults(func=cmd_lint)

    p = sub.add_parser("string", help="print an Appendix A string, filled")
    p.add_argument("id")
    p.add_argument("--fill", action="append", default=[], metavar="SLOT=VALUE")
    p.add_argument("--raw", action="store_true", help="body only, no header")
    p.set_defaults(func=cmd_string)

    p = sub.add_parser("strings", help="list Appendix A strings")
    p.add_argument("--section", default=None)
    p.add_argument("--pattern", action="store_true", help="PATTERN strings only")
    p.set_defaults(func=cmd_strings)

    p = sub.add_parser("split", help="§27 mechanical phrase pass over a script")
    p.add_argument("script", help="path to the script, or - for stdin")
    p.add_argument("--write", action="store_true", help="write phrase_inventory.json")
    p.set_defaults(func=cmd_split)

    p = sub.add_parser("coverage", help="§27B ledger audit + reconciliation line")
    p.set_defaults(func=cmd_coverage)

    p = sub.add_parser("actmap", help="E4 act-map schema validation")
    p.set_defaults(func=cmd_actmap)

    p = sub.add_parser("check", help="pre-submission gates on one beat")
    p.add_argument("beat_id")
    p.add_argument("--t2i", default=None, help="path to the T2I prompt")
    p.add_argument("--i2v", default=None, help="path to the I2V prompt")
    p.add_argument("--kling-direct", action="store_true")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("qa", help="E1 matrix: run AUTO rows, queue the rest")
    p.add_argument("beat_id", nargs="?")
    p.add_argument("--matrix", action="store_true", help="print the matrix and exit")
    p.set_defaults(func=cmd_qa)

    p = sub.add_parser("call", help="E7 call payload for a beat")
    p.add_argument("stage", choices=["t2i", "i2v", "sheet", "wait"])
    p.add_argument("--route", default=None)
    p.add_argument("--prompt", default=None, help="path to the prompt file, or - for stdin")
    p.add_argument("--start-image", default=None)
    p.add_argument("--duration", type=int, default=5)
    p.add_argument("--media", action="append", default=[])
    p.add_argument("--declined-preset-id", default=None)
    p.add_argument("--job", action="append", default=[])
    p.set_defaults(func=cmd_call)

    p = sub.add_parser("fail", help="E2: record a failure and get the retry decision")
    p.add_argument("beat_id")
    p.add_argument("signal", help="raw API/QA signal, or an E2 class name")
    p.set_defaults(func=cmd_fail)

    p = sub.add_parser("ledger", help="E3 run ledger views")
    p.add_argument("view", nargs="?", default="summary",
                   choices=["summary", "undelivered", "human", "reissues", "stalled", "json"])
    p.set_defaults(func=cmd_ledger)

    p = sub.add_parser("status", help="every gate at once — the one command before you ship")
    p.set_defaults(func=cmd_status)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, KeyError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


# --- commands -------------------------------------------------------------


def cmd_init(args) -> int:
    created = scaffold.create(Path(args.build), args.name, force=args.force)
    for relative in created:
        print(f"created {relative}")
    print(f"\nBuild tree ready (E9). Next: §18 step 1 — absorb the inspo video.")
    return 0


def cmd_steps(args) -> int:
    for number, name, klass, carries in BUILD_STEPS:
        gate = "  <-- THE ONLY GATE" if klass == "HG" else ""
        print(f"{number}. [{klass}] {name}{gate}\n     {carries}")
    print("\nSteps 1-5 ship as one opening delivery. Nothing inside it waits (§18).")
    return 0


def cmd_lint(args) -> int:
    standards = load_standards(args.path)
    findings = doclint.run(standards)
    for finding in findings:
        print(finding)
    print(f"\n{standards.path.name} v{standards.version}: {doclint.summary(findings)}")
    return 1 if any(f.severity == "FAIL" for f in findings) else 0


def cmd_string(args) -> int:
    standards = load_standards()
    block = standards.block(args.id)
    values = dict(pair.split("=", 1) for pair in args.fill)
    result = slots.fill(block.body, values)
    if not args.raw:
        declared = (str(block.declared_lo) if block.declared_lo == block.declared_hi
                    else f"{block.declared_lo}-{block.declared_hi}")
        note = f" {block.note}" if block.note else ""
        print(f"# {block.id} (§{block.section}) — declared {declared}{note}, "
              f"filled {budget.char_count(result.text)}")
    print(result.text)
    if result.unfilled:
        print(f"\nUNFILLED: " + ", ".join(
            f"[{slot}] <- {slots.source_for(slot)}" for slot in result.unfilled),
            file=sys.stderr)
        return 1
    return 0


def cmd_strings(args) -> int:
    standards = load_standards()
    for block_id in standards.block_ids():
        block = standards.blocks[block_id]
        if args.section and block.section != args.section:
            continue
        if args.pattern and not block.is_pattern:
            continue
        flag = "P" if block.is_pattern else " "
        mark = " " if block.count_ok() else "!"
        print(f"{flag}{mark} {block_id:20} §{block.section:5} {block.declared_lo:>5}  {block.description[:70]}")
    return 0


def cmd_split(args) -> int:
    text = sys.stdin.read() if args.script == "-" else Path(args.script).read_text(encoding="utf-8")
    phrases = coverage.split_script(text)
    for phrase in phrases:
        flags = f"  [{', '.join(phrase.triggers)}]" if phrase.triggers else ""
        print(f"{phrase.id}  {phrase.text}{flags}")
    review = [p.id for p in phrases if any(t.startswith("REVIEW") for t in p.triggers)]
    merge = [p.id for p in phrases if "merge-candidate" in p.triggers]
    print(f"\n{len(phrases)} phrases. "
          f"Confirm the non-mechanical triggers: {', '.join(review) or 'none'}. "
          f"MERGED candidates: {', '.join(merge) or 'none'}.")
    print("Every row needs a disposition before the act delivers (§27B).")
    if args.write:
        target = Path(args.build) / "phrase_inventory.json"
        coverage.save(phrases, target)
        print(f"wrote {target}")
    return 0


def cmd_coverage(args) -> int:
    path = Path(args.build) / "phrase_inventory.json"
    phrases = coverage.load(path)
    problems = coverage.audit(phrases)
    for problem in problems:
        print(f"FAIL  {problem}")
    reconciliation = coverage.reconcile(phrases)
    print(f"\nReconciliation — {reconciliation.line()}")
    if not reconciliation.delivered:
        print("UNDELIVERED: uncovered must read zero (§27B).")
    if reconciliation.blocked:
        print(f"{reconciliation.blocked} BLOCKED row(s) — reported, never resolved (§27B).")
    return 0 if reconciliation.delivered and not problems else 1


def cmd_actmap(args) -> int:
    root = Path(args.build)
    act_map = actmap.load(root / "act_map.json")
    wardrobe_path = root / "wardrobe_map.json"
    wardrobe = json.loads(wardrobe_path.read_text(encoding="utf-8")) if wardrobe_path.exists() else None
    problems = actmap.validate(act_map, wardrobe)
    for problem in problems:
        print(f"FAIL  {problem}")
    print(f"\n{len(act_map.rows)} rows · {len(act_map.story_days())} story day(s) · "
          f"{len(act_map.capture_events())} capture event(s) · {len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_check(args) -> int:
    root = Path(args.build)
    act_map = actmap.load(root / "act_map.json")
    beat = act_map.by_id(args.beat_id) or {}
    if not beat:
        print(f"warn: {args.beat_id} is not on the act map", file=sys.stderr)

    prompts = {}
    for stage, given in (("t2i", args.t2i), ("i2v", args.i2v)):
        path = Path(given) if given else root / "beats" / f"{args.beat_id}.{stage}.{'txt' if stage == 't2i' else 'json'}"
        if path.exists():
            prompts[stage] = path.read_text(encoding="utf-8")

    failures = 0
    for stage, text in prompts.items():
        verdict = budget.check_char_budget(text, kling_direct=args.kling_direct)
        print(f"{stage}: {verdict}")
        failures += 0 if verdict.ok else 1
        missing = slots.tokens(text)
        if missing:
            print("  FAIL  unfilled slots: " + ", ".join(
                f"[{s}] <- {slots.source_for(s)}" for s in missing))
            failures += 1
        residual = [b for b in slots.residual_brackets(text)
                    if b.strip("[]") not in missing]
        if residual:
            print("  FAIL  bracketed fill instructions left in the prompt: "
                  + " · ".join(r[:60] for r in residual))
            failures += 1

    dialogue = beat.get("dialogue") or ""
    if dialogue:
        for verdict in (
            budget.check_word_budget(dialogue, int(beat.get("duration") or 0),
                                     beat.get("pace") or "brisk",
                                     bool(beat.get("bound_move_word"))),
            budget.check_punctuation(dialogue),
            budget.check_sync_anchor(dialogue, beat.get("bound_move_word"),
                                     beat.get("closure_word")),
        ):
            print(verdict)
            failures += 0 if verdict.ok else 1

    for slot in slots.required_for(beat):
        present = any(f"[{slot}]" not in text for text in prompts.values())
        if not present and prompts:
            print(f"FAIL  {slot} is mandatory on this beat class (E5)")
            failures += 1

    print(f"\n{args.beat_id}: {'clear to submit' if not failures else f'{failures} gate(s) failed'}")
    return 1 if failures else 0


def cmd_qa(args) -> int:
    if args.matrix or not args.beat_id:
        for check_id, instrument, threshold, klass, on_fail in QA_CHECKS:
            print(f"{klass:11} {check_id:22} {instrument}\n            threshold: {threshold}\n            on fail:   {on_fail}")
        return 0
    root = Path(args.build)
    act_map = actmap.load(root / "act_map.json")
    beat = act_map.by_id(args.beat_id) or {"beat_id": args.beat_id}
    prompts = {}
    for stage, suffix in (("t2i", "t2i.txt"), ("i2v", "i2v.json")):
        path = root / "beats" / f"{args.beat_id}.{suffix}"
        if path.exists():
            prompts[stage] = path.read_text(encoding="utf-8")
    results = qa.run_auto(beat, prompts)
    queued = qa.queue_manual(beat)
    for result in results + queued:
        print(result)
        if result.status == "FAIL":
            print(f"       -> {result.on_fail}")
    failures = sum(1 for r in results if r.status == "FAIL")
    print(f"\n{len(results)} auto · {failures} failed · {len(queued)} queued for human")
    return 1 if failures else 0


def cmd_call(args) -> int:
    prompt = ""
    if args.prompt:
        prompt = sys.stdin.read() if args.prompt == "-" else Path(args.prompt).read_text(encoding="utf-8")
    if args.stage == "wait":
        print(calls.wait(args.job))
        return 0
    if args.stage == "sheet":
        print(calls.avatar_sheet(prompt))
        return 0
    if args.stage == "t2i":
        call = calls.t2i(prompt, route=args.route or "nano_banana_pro", medias=args.media)
    else:
        call = calls.i2v(prompt, route=args.route or "kling3_0",
                         start_image_job_id=args.start_image, duration=args.duration,
                         references=args.media or None,
                         declined_preset_id=args.declined_preset_id)
    print(call)
    return 1 if call.warnings else 0


def cmd_fail(args) -> int:
    ledger = Ledger.load(Path(args.build) / "run_ledger.json")
    failure_class = args.signal if args.signal.isupper() and "_" in args.signal else retry.classify(args.signal)
    decision = retry.apply(ledger, args.beat_id, failure_class)
    ledger.save()
    print(decision)
    if decision.history:
        print("history:")
        for entry in decision.history:
            print(f"  {entry['ts']}  {entry['class']}  {entry['action']}")
    print("\nRetries never change the prompt silently — a changed prompt is a delivered iteration (§16).")
    return 1 if decision.to_human else 0


def cmd_ledger(args) -> int:
    ledger = Ledger.load(Path(args.build) / "run_ledger.json")
    views = {
        "summary": lambda: json.dumps(ledger.summary(), indent=2),
        "undelivered": lambda: "\n".join(ledger.undelivered()) or "none",
        "human": lambda: "\n".join(ledger.pending_human()) or "none",
        "reissues": lambda: json.dumps(ledger.reissues(), indent=2),
        "stalled": lambda: "\n".join(ledger.blocked_on_start_frame()) or "none",
        "json": lambda: json.dumps(ledger.data, indent=2),
    }
    print(views[args.view]())
    return 0


def cmd_status(args) -> int:
    root = Path(args.build)
    print(f"# Build status — {root.resolve().name}\n")
    standards = load_standards()
    findings = doclint.run(standards)
    fails = sum(1 for f in findings if f.severity == "FAIL")
    print(f"Standards v{standards.version} · doc-lint: {fails} fail, {len(findings) - fails} warn")

    ledger = Ledger.load(root / "run_ledger.json")
    built_against = ledger.data.get("version_built_against")
    if built_against and built_against != standards.version:
        print(f"WARN  ledger built against v{built_against}, Standards are v{standards.version} "
              f"— the mirror and the file have drifted (§34)")

    code = 0
    inventory = root / "phrase_inventory.json"
    if inventory.exists():
        phrases = coverage.load(inventory)
        reconciliation = coverage.reconcile(phrases)
        problems = coverage.audit(phrases)
        print(f"Coverage: {reconciliation.line()}")
        if not reconciliation.delivered or problems:
            code = 1
        for problem in problems[:10]:
            print(f"  FAIL  {problem}")

    map_path = root / "act_map.json"
    if map_path.exists():
        act_map = actmap.load(map_path)
        wardrobe_path = root / "wardrobe_map.json"
        wardrobe = json.loads(wardrobe_path.read_text(encoding="utf-8")) if wardrobe_path.exists() else None
        problems = actmap.validate(act_map, wardrobe)
        print(f"Act map: {len(act_map.rows)} rows · {len(problems)} problem(s)")
        for problem in problems[:10]:
            print(f"  FAIL  {problem}")
        if problems:
            code = 1

    summary = ledger.summary()
    print(f"Ledger: {summary['beats']} beats · {summary['undelivered']} undelivered · "
          f"{summary['pending_human']} queued for human · {summary['reissues']} reissue flag(s)")
    stalled = ledger.blocked_on_start_frame()
    if stalled:
        print(f"  FAIL  I2V submitted before a completed start frame: {', '.join(stalled)} (§5)")
        code = 1
    return code


if __name__ == "__main__":
    raise SystemExit(main())
