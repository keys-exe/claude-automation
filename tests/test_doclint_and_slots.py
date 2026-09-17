from promptpipe import doclint, slots
from promptpipe.standards import parse


def test_lint_runs_over_the_shipped_standards():
    findings = doclint.run()
    rules = {f.rule for f in findings}
    assert rules <= {"count", "normative-id", "slot-manifest", "retired-phrase",
                     "retired-id", "changelog", "pending", "open-decisions"}


def test_retirement_notices_are_not_reported_as_survivals():
    findings = doclint.run()
    assert not [f for f in findings if f.rule in ("retired-id", "retired-phrase")]


def test_changelogs_are_current_plus_one_prior():
    assert doclint.check_changelogs(parse()) == []


def test_pending_amendments_are_empty_at_a_cut():
    assert doclint.check_pending_amendments(parse()) == []


def test_every_normative_id_resolves():
    assert doclint.check_id_resolution(parse()) == []


def test_summary_states_whether_the_cut_ships():
    assert "DOES NOT SHIP" in doclint.summary([doclint.Finding("count", "x")])
    assert "ships" in doclint.summary([])


def test_slots_fill_verbatim_and_report_what_is_missing():
    result = slots.fill("worn on the [SIDE] [REGION]", {"SIDE": "left"})
    assert result.text == "worn on the left [REGION]"
    assert result.unfilled == ["REGION"]
    assert not result.ok


def test_every_slot_names_its_source():
    assert "product_sheet" in slots.source_for("SITE")
    assert "UNDECLARED" in slots.source_for("MADE-UP")


def test_bracketed_fill_instructions_are_caught_even_when_they_are_prose():
    text = "sitting flush [ITS CONTACT RELATIONSHIP TO the wrist bone]"
    assert slots.tokens(text) == []
    assert slots.residual_brackets(text)


def test_worn_beats_require_site_and_side():
    required = slots.required_for({"product_state": "worn"})
    assert {"SITE", "SIDE"} <= set(required)


def test_rear_beats_require_the_inner_face_slots():
    required = slots.required_for({"product_state": "worn", "frame_side": "rear"})
    assert {"BAND-INNER", "REAR-PATH"} <= set(required)


def test_stress_register_requires_the_load_cadence():
    assert "LOAD-CADENCE" in slots.required_for({"register": "ANAT-STRESS"})
