from promptpipe import qa, retry
from promptpipe.ledger import Ledger


def test_two_rerolls_then_human(tmp_path):
    ledger = Ledger(tmp_path / "run_ledger.json")
    first = retry.apply(ledger, "BR-01", "QUALITY_FAIL")
    second = retry.apply(ledger, "BR-01", "QUALITY_FAIL")
    third = retry.apply(ledger, "BR-01", "QUALITY_FAIL")
    assert (first.action, second.action, third.action) == ("retry", "retry", "human")
    assert third.history and len(third.history) == 2


def test_budgets_are_per_class_not_per_beat(tmp_path):
    ledger = Ledger(tmp_path / "run_ledger.json")
    retry.apply(ledger, "BR-01", "QUALITY_FAIL")
    retry.apply(ledger, "BR-01", "QUALITY_FAIL")
    assert retry.apply(ledger, "BR-01", "CONSISTENCY_FAIL").action == "retry"


def test_preset_override_gets_three_declines(tmp_path):
    ledger = Ledger(tmp_path / "run_ledger.json")
    actions = [retry.apply(ledger, "BR-01", "PRESET_OVERRIDE").action for _ in range(4)]
    assert actions == ["retry", "retry", "retry", "human"]


def test_classify_maps_signals_to_e2_classes():
    assert retry.classify("Request blocked by safety system") == "SAFETY_REJECT"
    assert retry.classify("preset offer returned") == "PRESET_OVERRIDE"
    assert retry.classify("404 media input not found") == "COMPLETION_404"
    assert retry.classify("logged model differs from passed") == "ALIAS_MISMATCH"


def test_human_queue_lands_on_the_ledger(tmp_path):
    ledger = Ledger(tmp_path / "run_ledger.json")
    for _ in range(3):
        retry.apply(ledger, "BR-01", "QUALITY_FAIL")
    assert "BR-01:i2v_qa:QUALITY_FAIL" in ledger.pending_human()


def test_start_frame_must_be_completed_not_merely_submitted(tmp_path):
    ledger = Ledger(tmp_path / "run_ledger.json")
    ledger.update("BR-01", t2i_status="queued", i2v_job_id="job-9")
    assert ledger.blocked_on_start_frame() == ["BR-01"]
    ledger.update("BR-01", t2i_status="completed")
    assert ledger.blocked_on_start_frame() == []


def test_qa_auto_flags_an_over_ceiling_prompt():
    results = qa.run_auto({"type": "BR", "kling_direct": True}, {"i2v": "x" * 3000})
    assert any(r.check == "char_count" and r.status == "FAIL" for r in results)


def test_qa_flags_an_alias_mismatch():
    results = qa.run_auto(
        {"type": "BR"}, {"i2v": "short"},
        job={"model_requested": "kling3_0", "model_logged": "kling2_5"},
    )
    assert any(r.check == "model_run" and r.status == "FAIL" for r in results)


def test_traversed_locations_carry_no_plate():
    results = qa.run_auto({"type": "BR", "location_tier": "TRAVERSED", "plate_job_id": "j1"}, {})
    assert any(r.check == "location_tier" and r.status == "FAIL" for r in results)


def test_human_checks_are_queued_not_skipped():
    queued = qa.queue_manual({"type": "TH", "location_id": "L-01"})
    checks = {r.check for r in queued}
    assert {"closure_sync", "scene_hold", "entry_latency"} <= checks
    assert all(r.status == "QUEUED" for r in queued)
