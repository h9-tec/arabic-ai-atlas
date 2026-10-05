from pathlib import Path

from atlas.load import load_entries
from atlas.query import license_class
from atlas.validate import load_schema
from atlas.wanted import load_rules, match_rule, matches, validate_rules

ROOT = Path(__file__).resolve().parent.parent


def test_load_entries_skips_wanted_yaml(tmp_path):
    (tmp_path / "llms.yaml").write_text("- {id: a, name: A}\n")
    (tmp_path / "wanted.yaml").write_text("- {id: w, title: W, why: x, query: {type: tts}}\n")
    assert [e["id"] for e in load_entries(tmp_path)] == ["a"]

def test_license_class_matches_site():
    assert [license_class(x) for x in ("apache-2.0", "cc-by-nc-4.0", "proprietary", "unknown", None,
            "fair-noncommercial-research-license", "falcon-llm-license")] == \
           ["open", "nc", "unknown", "unknown", "unknown", "nc", "open"]

def test_match_rule_semantics():
    e = {"id": "x", "type": "tts", "country": "SA", "dialects": ["gulf"], "license": "apache-2.0",
         "tasks": ["tts"], "tags": ["voice"]}
    assert match_rule(e, {"type": "tts", "dialects": ["gulf", "egy"], "license_class": "open"})
    assert not match_rule({**e, "license": "cc-by-nc-4.0"}, {"type": "tts", "license_class": "open"})
    assert match_rule({**e, "license": "cc-by-nc-4.0"}, {"type": "tts", "license_class": "any"})
    assert match_rule(e, {"country": ["SA", "KW"], "tasks": "VOICE"})
    assert not match_rule(e, {"type": "tts", "on_device": True})
    assert not match_rule({**e, "type": "paper"}, {"country": "SA"})

def test_validate_rules_rejects_unknown_key_and_empty_query(schema):
    errs = validate_rules([{"id": "a", "title": "A", "why": "x", "query": {"dialect": "gulf"}},
                           {"id": "b", "title": "B", "why": "x", "query": {}}], schema)
    assert any("wanted.yaml:a:" in e and "dialect" in e for e in errs)
    assert any("wanted.yaml:b:" in e and "empty" in e for e in errs)

def test_validate_rules_enums_length_and_duplicates(schema):
    bad = [{"id": "c", "title": "C", "why": "x" * 161, "query": {"country": "XX", "license_class": "nc"}},
           {"id": "c", "title": "C", "why": "x", "query": {"type": "tts"}},
           {"id": "Bad Id", "title": "", "why": "x", "query": {"type": "tts"}}]
    errs = validate_rules(bad, schema)
    for needle in ("160", "XX", "license_class", "duplicate id", "Bad Id"):
        assert any(needle in e for e in errs), needle

def test_seed_rules_valid():
    rules = load_rules(ROOT / "data" / "wanted.yaml")
    assert len(rules) == 15 and validate_rules(rules, load_schema(ROOT / "data" / "schema.json")) == []


def test_load_rules_rejects_non_list(tmp_path):
    import pytest

    (tmp_path / "wanted.yaml").write_text("id: a\n")
    with pytest.raises(ValueError):
        load_rules(tmp_path / "wanted.yaml")


def test_every_seed_rule_matches_nothing_today():
    # Invariant: a wanted rule is a gap. This WILL fail when a contribution fills one;
    # the fix is to move that rule to the filled cache (Task 2), not to delete this test.
    entries = load_entries(ROOT / "data")
    filled = {r["id"]: matches(r, entries) for r in load_rules(ROOT / "data" / "wanted.yaml")}
    assert {k: v for k, v in filled.items() if v} == {}
