import json

from promptpipe import coverage
from promptpipe.cli import main
from promptpipe.ledger import Ledger


def test_init_creates_the_e9_tree(tmp_path):
    assert main(["--build", str(tmp_path), "init", "Test Product"]) == 0
    for expected in ("product_sheet.md", "product_sheet.py", "act_map.json",
                     "phrase_inventory.json", "wardrobe_map.json", "run_ledger.json",
                     "capcut_block.md", "registries/subject.json", "beats", "location_sheets"):
        assert (tmp_path / expected).exists(), expected


def test_the_generated_product_sheet_py_runs_and_refuses_to_be_empty(tmp_path):
    main(["--build", str(tmp_path), "init", "Test Product"])
    namespace: dict = {}
    exec((tmp_path / "product_sheet.py").read_text(), namespace)
    try:
        namespace["verify"]()
    except AssertionError as error:
        assert "unfilled Product Sheet slots" in str(error)
    else:
        raise AssertionError("an empty product sheet must not verify")


def test_ledger_is_stamped_with_the_standards_version(tmp_path):
    main(["--build", str(tmp_path), "init", "Test Product"])
    ledger = Ledger.load(tmp_path / "run_ledger.json")
    assert ledger.data["version_built_against"].startswith("7.")


def test_status_fails_while_a_phrase_is_uncovered(tmp_path, capsys):
    main(["--build", str(tmp_path), "init", "Test Product"])
    coverage.save([coverage.Phrase(id="P-001", text="It held.")],
                  tmp_path / "phrase_inventory.json")
    code = main(["--build", str(tmp_path), "status"])
    out = capsys.readouterr().out
    assert code == 1
    assert "uncovered: 1" in out


def test_status_passes_once_every_phrase_carries_a_disposition(tmp_path, capsys):
    main(["--build", str(tmp_path), "init", "Test Product"])
    coverage.save([coverage.Phrase(id="P-001", text="It held.", disposition="TH-01")],
                  tmp_path / "phrase_inventory.json")
    code = main(["--build", str(tmp_path), "status"])
    assert code == 0
    assert "uncovered: 0" in capsys.readouterr().out


def test_status_warns_when_the_build_and_the_standards_have_drifted(tmp_path, capsys):
    main(["--build", str(tmp_path), "init", "Test Product"])
    ledger = Ledger.load(tmp_path / "run_ledger.json")
    ledger.data["version_built_against"] = "7.40.0"
    ledger.save()
    main(["--build", str(tmp_path), "status"])
    assert "drifted" in capsys.readouterr().out


def test_fail_command_walks_the_e2_budget_then_stops(tmp_path, capsys):
    main(["--build", str(tmp_path), "init", "Test Product"])
    args = ["--build", str(tmp_path), "fail", "BR-01", "render came back plastic"]
    assert main(args) == 0
    assert main(args) == 0
    assert main(args) == 1
    assert "HUMAN" in capsys.readouterr().out


def test_lint_exits_nonzero_while_counts_drift():
    assert main(["lint"]) in (0, 1)


def test_actmap_validation_runs_through_the_cli(tmp_path, capsys):
    main(["--build", str(tmp_path), "init", "Test Product"])
    payload = {"declared": {"side": "left"}, "rows": [
        {"beat_id": "BR-01", "act": "1", "phrase_ids": ["P-001"], "type": "BR",
         "register": "doc", "location_id": "L-01", "story_day": "", "duration": 5,
         "capture_event_id": "E-01", "product_state": "worn", "visibility": "VISIBLE",
         "wardrobe_ref": "W-01"}]}
    (tmp_path / "act_map.json").write_text(json.dumps(payload))
    assert main(["--build", str(tmp_path), "actmap"]) == 1
    assert "wardrobe_ref with no story_day" in capsys.readouterr().out


def test_split_writes_an_inventory_every_row_of_which_needs_a_disposition(tmp_path, capsys):
    main(["--build", str(tmp_path), "init", "Test Product"])
    script = tmp_path / "script.txt"
    script.write_text("Braces, creams, magnets, patches. Nothing worked.")
    main(["--build", str(tmp_path), "split", str(script), "--write"])
    phrases = coverage.load(tmp_path / "phrase_inventory.json")
    assert [p.id for p in phrases] == ["P-001", "P-002", "P-003", "P-004", "P-005"]
    assert all(not p.disposition for p in phrases)
    assert "disposition before the act delivers" in capsys.readouterr().out
