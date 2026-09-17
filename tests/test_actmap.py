import pytest

from promptpipe import actmap


def row(**overrides):
    base = actmap.blank_row(
        "BR-01", act="1", phrase_ids=["P-001"], type="BR", register="doc",
        location_id="L-01", story_day="1", capture_event_id="E-01", duration=5,
        product_state="absent", visibility="CONCEALED",
    )
    base.update(overrides)
    return base


def test_clean_row_passes():
    assert actmap.validate(actmap.ActMap(rows=[row(product_state="worn", visibility="VISIBLE")], declared={})) == []


def test_story_day_is_mandatory():
    problems = actmap.validate(actmap.ActMap(rows=[row(story_day="", product_state="worn")], declared={}))
    assert any("story_day" in p for p in problems)


def test_capture_event_is_mandatory():
    problems = actmap.validate(actmap.ActMap(rows=[row(capture_event_id="", product_state="worn")], declared={}))
    assert any("capture_event_id" in p for p in problems)


def test_wardrobe_ref_without_story_day_is_the_named_failure():
    problems = actmap.validate(
        actmap.ActMap(rows=[row(story_day="", wardrobe_ref="W-01", product_state="worn")], declared={})
    )
    assert any("wardrobe_ref with no story_day" in p for p in problems)


def test_unlocated_first_appearance_is_caught_at_the_act_map():
    problems = actmap.validate(actmap.ActMap(rows=[row()], declared={}))
    assert any("first appearance unlocated" in p for p in problems)


def test_story_day_must_resolve_to_an_outfit():
    wardrobe = {"outfits": {"2": {"BASE": "", "MID": "", "OUTER": "", "LOWER": "", "FOOT": "", "ACCENT": ""}}}
    problems = actmap.validate(
        actmap.ActMap(rows=[row(product_state="worn", visibility="VISIBLE")], declared={}), wardrobe
    )
    assert any("resolves to no outfit row" in p for p in problems)


def test_a_story_day_carries_exactly_one_outfit():
    wardrobe = {"outfits": {"1": [{"BASE": "a"}, {"BASE": "b"}]}}
    problems = actmap.validate(actmap.ActMap(rows=[], declared={}), wardrobe)
    assert any("exactly one" in p for p in problems)


def test_fields_outside_the_schema_are_rejected():
    problems = actmap.validate(
        actmap.ActMap(rows=[row(product_state="worn", visibility="VISIBLE") | {"vibe": "cosy"}], declared={})
    )
    assert any("not in the E4 schema" in p for p in problems)
