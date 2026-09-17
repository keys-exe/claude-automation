from promptpipe import coverage


def test_list_of_nouns_splits_one_beat_each():
    phrases = coverage.split_script("Braces, creams, magnets, patches.")
    assert [p.text for p in phrases] == ["Braces", "creams", "magnets", "patches"]


def test_clause_with_no_internal_shift_is_flagged_as_a_merge_candidate():
    phrases = coverage.split_script("It held, so I kept going.")
    assert any("merge-candidate" in p.triggers for p in phrases)


def test_cut_is_withdrawn_as_a_disposition():
    error = coverage.validate_disposition("CUT")
    assert error and "withdrawn" in error


def test_blocked_must_carry_a_reason_and_a_section():
    phrases = [coverage.Phrase(id="P-001", text="x", disposition="BLOCKED")]
    assert any("reason and section" in problem for problem in coverage.audit(phrases))


def test_uncovered_makes_the_act_undelivered():
    phrases = [
        coverage.Phrase(id="P-001", text="a", disposition="BR-01"),
        coverage.Phrase(id="P-002", text="b"),
    ]
    reconciliation = coverage.reconcile(phrases)
    assert reconciliation.uncovered == 1
    assert not reconciliation.delivered


def test_reconciliation_line_reports_every_column():
    phrases = [
        coverage.Phrase(id="P-001", text="a", disposition="BR-01", plant="act3"),
        coverage.Phrase(id="P-002", text="b", disposition="TH-01"),
        coverage.Phrase(id="P-003", text="c", disposition="MERGED→P-001"),
        coverage.Phrase(id="P-004", text="d", disposition="BLOCKED",
                        blocked_reason="Tier 3 claim", blocked_section="§43A"),
    ]
    line = coverage.reconcile(phrases).line()
    for fragment in ("uncovered: 0", "blocked: 1", "TH-carried: TH-01", "merged: P-003"):
        assert fragment in line
    assert "act3" in line  # the plant is unpaid and says so


def test_beat_id_gaps_are_their_own_alarm():
    phrases = [
        coverage.Phrase(id="P-001", text="a", disposition="BR-01"),
        coverage.Phrase(id="P-002", text="b", disposition="BR-03"),
    ]
    assert any("numbering has gaps" in problem for problem in coverage.audit(phrases))


def test_merged_target_must_exist():
    phrases = [coverage.Phrase(id="P-001", text="a", disposition="MERGED→P-099")]
    assert any("not in the inventory" in problem for problem in coverage.audit(phrases))
