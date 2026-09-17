import pytest

from promptpipe import standards


@pytest.fixture(scope="module")
def doc():
    return standards.parse()


def test_version_and_scale(doc):
    assert doc.version == "7.49.8"
    # Appendix A carries ~240 strings; a parser that finds far fewer has broken.
    assert len(doc.blocks) > 200


def test_known_strings_round_trip(doc):
    block = doc.block("CAP-A")
    assert block.declared_lo == 427
    assert block.actual == 427
    assert block.count_ok()
    assert "Smart HDR 5" in block.body


def test_counts_are_measured_on_the_minified_string(doc):
    block = doc.block("CAM-LOCK")
    assert standards.minify("a\nb  c") == "a b c"
    assert block.actual == len(standards.minify(block.body))


def test_patterns_expose_their_slots(doc):
    block = doc.block("PLACE-LOCK")
    assert block.is_pattern
    assert "SIDE" in block.slots


def test_missing_string_names_the_document(doc):
    with pytest.raises(KeyError, match="does not exist|no Appendix A string"):
        doc.block("NOT-A-STRING")
