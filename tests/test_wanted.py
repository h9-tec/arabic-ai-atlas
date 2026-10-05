from pathlib import Path

from atlas.load import load_entries
from atlas.query import license_class
from atlas.validate import load_schema
from atlas.render_wanted import render_wanted_block
from atlas.wanted import evaluate, load_rules, match_rule, matches, newly_filled, validate_rules, wanted_hash

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


def test_seed_rules_consistent_with_filled_cache():
    # A rule that a contribution fills is recorded in data/.cache/wanted.json (build does it)
    # and listed under Recently filled; it is not deleted. So the committed cache must equal
    # exactly the set of seed rules that currently match something.
    import json

    entries = load_entries(ROOT / "data")
    rules = load_rules(ROOT / "data" / "wanted.yaml")
    cache = json.loads((ROOT / "data" / ".cache" / "wanted.json").read_text(encoding="utf-8"))
    filled = {r["id"] for r in rules if matches(r, entries)}
    assert set(cache) == filled


RULES = [{"id": "gulf-tts", "title": "Gulf TTS", "why": "None open.", "query": {"type": "tts", "dialects": ["gulf"], "license_class": "open"}}]
TTS = {"id": "t1", "type": "tts", "dialects": ["gulf"], "license": "mit", "tasks": ["tts"]}


def test_newly_filled_gets_build_date():
    st, cache = evaluate(RULES, [TTS], {}, "2026-10-05")
    assert st[0]["status"] == "filled" and st[0]["recent"] and st[0]["by"] == ["t1"]
    assert cache == {"gulf-tts": {"filled_on": "2026-10-05", "by": ["t1"]}}


def test_filled_on_is_sticky_and_window_is_30_days():
    cache = {"gulf-tts": {"filled_on": "2026-09-05", "by": ["t1"]}}
    assert evaluate(RULES, [TTS], cache, "2026-10-05")[0][0]["recent"] is True   # day 30
    st, c = evaluate(RULES, [TTS], cache, "2026-10-06")                            # day 31
    assert st[0]["recent"] is False and c["gulf-tts"]["filled_on"] == "2026-09-05"


def test_unfilled_again_returns_to_board():
    cache = {"gulf-tts": {"filled_on": "2026-10-01", "by": ["t1"]}}
    st, c = evaluate(RULES, [{**TTS, "license": "cc-by-nc-4.0"}], cache, "2026-10-05")
    assert st[0]["status"] == "open" and c == {}


def test_removed_rule_dropped_from_cache():
    assert evaluate([], [TTS], {"gone": {"filled_on": "2026-10-01", "by": ["t1"]}}, "2026-10-05") == ([], {})


def test_wanted_hash_matches_site_order():
    assert wanted_hash(RULES[0]["query"]) == "#type=tts&dialect=gulf&license=open"
    assert wanted_hash({"country": ["KM", "DJ"], "tasks": ["ocr"], "on_device": True}) == "#q=ocr&country=KM,DJ&on_device=1"
    assert wanted_hash({"tasks": ["handwriting", "htr"], "type": "benchmark"}) == "#type=benchmark"


def test_block_lists_open_and_recent_only():
    st, _ = evaluate(RULES + [{"id": "mr", "title": "Mauritania", "why": "Nothing yet.", "query": {"country": "MR"}}],
                     [TTS], {}, "2026-10-05")
    out = render_wanted_block(st)
    assert "| Gap | Why | Rule |" in out and "Mauritania" in out
    assert "Recently filled" in out and "Gulf TTS" in out.split("Recently filled")[-1]


def test_block_when_every_rule_filled():
    st, _ = evaluate(RULES, [TTS], {"gulf-tts": {"filled_on": "2026-01-01", "by": ["t1"]}}, "2026-10-05")
    assert "Every wanted gap is filled" in render_wanted_block(st)


def test_rule_text_example():
    from atlas.wanted import rule_text
    assert rule_text(RULES[0]["query"]) == "type=tts · dialects=gulf · license=open"


def test_newly_filled():
    base = {"a": {"filled_on": "2026-10-01", "by": ["x"]}}
    new = {"a": {"filled_on": "2026-10-01", "by": ["x"]}, "c": {"by": []}, "b": {"by": []}}
    assert newly_filled(base, new) == ["b", "c"]


def test_mauritania_rule_needs_a_resource_not_an_org():
    rule = next(r for r in load_rules(ROOT / "data" / "wanted.yaml") if r["id"] == "mauritania-anything")
    assert not matches(rule, [{"id": "mr-org", "type": "org", "country": "MR"},
                              {"id": "mr-paper", "type": "paper", "country": "MR"}])
    assert matches(rule, [{"id": "mr-ds", "type": "dataset", "country": "MR", "license": "cc-by-4.0"}]) == ["mr-ds"]
    assert matches(rule, load_entries(ROOT / "data")) == []  # seed: still open
