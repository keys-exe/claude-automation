import pytest

from promptpipe import budget


@pytest.mark.parametrize(
    "words,pace,expected",
    [(9, "brisk", 5), (10, "brisk", 10), (20, "brisk", 10), (21, "brisk", None),
     (8, "unhurried", 5), (9, "unhurried", 10), (18, "unhurried", 10), (19, "unhurried", None)],
)
def test_e6_duration_function(words, pace, expected):
    assert budget.duration_for(words, pace) == expected


def test_talking_while_doing_reads_the_unhurried_column():
    # 9 words is inside the brisk 5s ceiling but over the unhurried one.
    assert budget.duration_for(9, "brisk") == 5
    assert budget.duration_for(9, "brisk", talking_while_doing=True) == 10


def test_word_budget_never_squeezes():
    verdict = budget.check_word_budget("one two three four five six seven eight nine ten", 5)
    assert not verdict.ok
    assert "never squeeze" in verdict.remedy
    assert "10s" in verdict.remedy


def test_word_budget_passes_inside_the_table():
    assert budget.check_word_budget("one two three four five six seven eight", 5).ok


def test_char_ceiling_counted_minified():
    # The measured case from §37: 2,474 minified passed, 2,506 pretty-printed failed.
    prompt = "x" * 2474
    assert budget.check_char_budget(prompt).ok
    padded = "x" * 2400 + "\n" + "y" * 110
    assert not budget.check_char_budget(padded).ok


def test_higgsfield_route_has_no_ceiling():
    assert budget.check_char_budget("x" * 4000, kling_direct=False).ok


def test_banned_punctuation():
    assert not budget.check_punctuation("Well... it worked").ok
    assert not budget.check_punctuation("It worked — finally").ok
    assert budget.check_punctuation("It worked, finally.").ok


def test_closure_word_prefers_mbp():
    assert budget.closure_word("I can climb the stairs") == "climb"
    # No m/b/p anywhere falls through to f/v.
    assert budget.closure_word("She rests, finally") == "finally"
    assert budget.closure_word("She rests easy") is None


def test_sync_anchor_requires_one_of_the_two():
    assert not budget.check_sync_anchor("It worked", None, None).ok
    assert budget.check_sync_anchor("It worked", "down", None).ok
    assert budget.check_sync_anchor("It worked", None, "worked").ok
