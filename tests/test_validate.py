import pytest

from atlas.load import load_entries
from atlas.validate import validate_entries


def test_load_merges_files_and_tags_source(fixture_dir):
    entries = load_entries(fixture_dir)
    assert len(entries) == 6
    assert {e["_file"] for e in entries} == {"llms.yaml", "tts.yaml", "datasets.yaml"}


def test_valid_fixture_passes(fixture_dir, schema):
    assert validate_entries(load_entries(fixture_dir), schema) == []


@pytest.mark.parametrize("field,value", [
    ("country", "XX"), ("type", "robot"), ("id", "Bad_ID"),
    ("notes", "x" * 161), ("links", {}), ("links", {"hf": "ftp://x"}),
])
def test_bad_field_fails(field, value, schema, good_entry):
    bad = {**good_entry, field: value}
    errs = validate_entries([bad], schema)
    assert len(errs) == 1 and errs[0].startswith("llms.yaml:")


@pytest.mark.parametrize("code", ["DZ", "LY", "SD", "IQ", "SY", "YE", "PS", "MR", "SO", "DJ", "KM"])
def test_every_arab_league_country_validates(code, schema, good_entry):
    assert validate_entries([{**good_entry, "country": code}], schema) == []


def test_duplicate_ids_name_both_files(schema, good_entry):
    a = {**good_entry, "_file": "llms.yaml"}
    b = {**good_entry, "_file": "tts.yaml"}
    errs = validate_entries([a, b], schema)
    assert any("llms.yaml" in e and "tts.yaml" in e and "duplicate id" in e for e in errs)


def test_non_list_yaml_raises(tmp_path):
    (tmp_path / "bad.yaml").write_text("id: x\n")
    with pytest.raises(ValueError, match="bad.yaml"):
        load_entries(tmp_path)


def test_missing_id_falls_back(schema, good_entry):
    bad = {k: v for k, v in good_entry.items() if k != "id"}
    errs = validate_entries([bad], schema)
    assert errs and all(e.startswith("llms.yaml:<no id>:") for e in errs)


@pytest.mark.parametrize("field", ["modality", "name"])
def test_missing_required_field_fails(field, schema, good_entry):
    bad = {k: v for k, v in good_entry.items() if k != field}
    errs = validate_entries([bad], schema)
    assert len(errs) == 1 and errs[0].startswith("llms.yaml:")
