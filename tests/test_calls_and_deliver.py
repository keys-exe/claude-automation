import json

import pytest

from promptpipe import calls, deliver
from promptpipe.coverage import Phrase, reconcile


def test_gpt_image_never_leaves_quality_and_resolution_at_catalogue_defaults():
    call = calls.avatar_sheet("a sheet prompt")
    assert call.params["variant"] == "sunburst"
    assert call.params["quality"] == "high"
    assert call.params["resolution"] == "2k"
    assert call.warnings == []


def test_kling_without_a_start_image_warns():
    call = calls.i2v("prompt", start_image_job_id=None, declined_preset_id="p1")
    assert any("start_image" in w for w in call.warnings)


def test_declined_preset_id_is_mandatory():
    call = calls.i2v("prompt", start_image_job_id="job-1")
    assert any("declined_preset_id" in w for w in call.warnings)


def test_kling_direct_ceiling_is_enforced_on_the_payload():
    call = calls.i2v("x" * 3000, start_image_job_id="job-1",
                     declined_preset_id="p1", kling_direct=True)
    assert any("2,500" in w for w in call.warnings)


def test_wan_defaults_to_references_mode():
    call = calls.i2v("prompt", route="wan_references", references=["seed", "sheet"])
    assert call.params["images"] == ["seed", "sheet"]
    assert call.params["enable_prompt_expansion"] is False
    assert call.warnings == []


def test_unknown_route_is_refused():
    with pytest.raises(KeyError):
        calls.i2v("prompt", route="veo")


def test_header_carries_line_model_and_counts():
    beat = deliver.Beat(beat_id="BR-01", line="It held.", model="kling3_0",
                        params="5s/1080p", t2i="seed prompt", i2v="motion prompt",
                        face_state="NOFACE")
    header = beat.header()
    assert "BR-01" in header and '"It held."' in header
    assert "kling3_0/5s/1080p" in header and "NOFACE" in header
    assert "chars" in header


def test_a_prompt_without_its_line_label_is_undelivered():
    problems = deliver.validate(deliver.Beat(beat_id="BR-01", line="", t2i="x", model="m"))
    assert any("undelivered" in p for p in problems)


def test_a_description_of_a_prompt_is_not_a_prompt():
    problems = deliver.validate(deliver.Beat(beat_id="BR-01", line="It held."))
    assert any("not a prompt" in p for p in problems)


def test_json_beats_must_keep_camera_nested_and_negatives_a_string():
    payload = json.dumps({"camera": "slow push", "negatives": ["blur"]})
    problems = deliver.validate(
        deliver.Beat(beat_id="BR-01", line="x", model="kling3_0", i2v=payload, i2v_is_json=True)
    )
    assert any("camera" in p for p in problems)
    assert any("negatives" in p for p in problems)


def test_broll_json_never_carries_duration():
    payload = json.dumps({"type": "BR", "duration": 5,
                          "camera": {"movement": "a", "framing": "b"}, "negatives": "x"})
    problems = deliver.validate(
        deliver.Beat(beat_id="BR-01", line="x", model="kling3_0", i2v=payload, i2v_is_json=True)
    )
    assert any("duration" in p for p in problems)


def test_act_delivery_ends_on_its_reconciliation_line():
    beats = [deliver.Beat(beat_id="BR-01", line="It held.", model="kling3_0", t2i="seed")]
    phrases = [Phrase(id="P-001", text="It held.", disposition="BR-01")]
    rendered = deliver.act(beats, reconcile(phrases), title="Act 1")
    assert "**Reconciliation —**" in rendered
    assert "uncovered: 0" in rendered
    assert "UNDELIVERED" not in rendered


def test_an_act_with_an_uncovered_phrase_says_so():
    phrases = [Phrase(id="P-001", text="It held.")]
    rendered = deliver.act([], reconcile(phrases))
    assert "UNDELIVERED" in rendered


def test_correction_names_the_global_and_retroactive_halves():
    beat = deliver.Beat(beat_id="BR-04", line="x", model="kling3_0", t2i="fixed")
    text = deliver.correction(beat, ["BR-07", "BR-11"], ["BR-02"], "§9D",
                              "placement restated in full form")
    assert "Also corrected" in text and "BR-07" in text
    assert "Now invalid" in text and "BR-02" in text
    assert "Pending Amendment logged against §9D" in text
