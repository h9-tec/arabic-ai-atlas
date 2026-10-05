from atlas.enrich import build_hf_ids, merge_metrics
import json

from atlas.query import get, load_atlas, load_doc, recommend, search


def _merged(fixture_entries):
    ids = build_hf_ids(fixture_entries)
    cache = {i: {"downloads": n * 10, "likes": 1, "lastModified": None} for n, i in enumerate(ids, 1)}
    return merge_metrics(fixture_entries, cache)


def test_search_by_org_case_insensitive(fixture_entries):
    m = _merged(fixture_entries)
    org = m[0]["org"]
    hits = search(m, org.upper())
    assert hits and all(
        org.lower() in " ".join([h["name"], h["org"], h.get("notes", ""), *h.get("tasks", []), *h.get("tags", [])]).lower()
        for h in hits
    )


def test_search_filter_type(fixture_entries):
    m = _merged(fixture_entries)
    hits = search(m, "", type="llm")
    assert hits and all(h["type"] == "llm" for h in hits)
    assert len(hits) == sum(1 for e in m if e["type"] == "llm")


def _jais_and_undialected(fixture_entries):
    m = _merged(fixture_entries)
    jais = get(m, "jais-30b")
    other = {k: v for k, v in get(m, "allam-7b").items() if k != "dialects"}
    return [other, jais]  # other listed first; ranking must still put jais first


def test_recommend_ranks_task_and_dialect(fixture_entries):
    res = recommend(_jais_and_undialected(fixture_entries), "chat", dialect="msa")
    assert [r["id"] for r in res] == ["jais-30b", "allam-7b"]
    assert res[0]["score"] == 5
    assert "task match" in res[0]["why"] and "dialect match" in res[0]["why"]


def test_recommend_no_match_returns_empty(fixture_entries):
    assert recommend(_merged(fixture_entries), "no-such-task-xyz") == []


def test_recommend_dialect_filter_tolerates_missing_dialects(fixture_entries):
    res = recommend(_jais_and_undialected(fixture_entries), "chat", dialect="msa", limit=10)
    assert {r["id"]: r["score"] for r in res}["allam-7b"] == 3


def test_recommend_license_open_excludes_unknown():
    es = [
        {"id": "a", "name": "A", "tasks": ["chat"], "license": "apache-2.0"},
        {"id": "b", "name": "B", "tasks": ["chat"], "license": "unknown"},
        {"id": "c", "name": "C", "tasks": ["chat"], "license": "Proprietary"},
    ]
    assert [r["id"] for r in recommend(es, "chat", license_filter="open")] == ["a"]
    assert [r["id"] for r in recommend(es, "chat", license_filter="unknown")] == ["b"]


def _device_entries():
    return [
        {"id": "phone", "name": "Phone", "type": "tts", "tasks": ["tts"], "on_device": True},
        {"id": "server", "name": "Server", "type": "tts", "tasks": ["tts"], "on_device": False},
        {"id": "unset", "name": "Unset", "type": "tts", "tasks": ["tts"]},
    ]


def test_recommend_on_device_true_keeps_only_marked():
    assert [r["id"] for r in recommend(_device_entries(), "tts", on_device=True, limit=10)] == ["phone"]


def test_recommend_on_device_false_excludes_only_marked():
    assert {r["id"] for r in recommend(_device_entries(), "tts", on_device=False, limit=10)} == {"server", "unset"}


def test_recommend_on_device_none_is_no_filter():
    assert len(recommend(_device_entries(), "tts", on_device=None, limit=10)) == 3


def test_recommend_on_device_false_keeps_unset_fixture_entries(fixture_entries):
    res = recommend(_merged(fixture_entries), "chat", on_device=False, limit=10)
    assert {r["id"] for r in res} == {"jais-30b", "allam-7b", "silma-9b"}


def _typed_entries():
    return [
        {"id": "corpus", "name": "Corpus", "type": "dataset", "tasks": ["tts"], "metrics": {"downloads": 9000}},
        {"id": "voice", "name": "Voice", "type": "tts", "tasks": ["tts"], "metrics": {"downloads": 10}},
        {"id": "bench", "name": "Bench", "type": "benchmark", "tasks": ["tts"], "metrics": {"downloads": 50}},
    ]


def test_recommend_type_filter_is_exact():
    res = recommend(_typed_entries(), "tts", type="tts", limit=10)
    assert [r["id"] for r in res] == ["voice"]
    assert [r["id"] for r in recommend(_typed_entries(), "tts", type="dataset", limit=10)] == ["corpus"]


def test_recommend_ranks_models_above_datasets_at_equal_score():
    res = recommend(_typed_entries(), "tts", limit=10)
    assert [r["id"] for r in res] == ["voice", "corpus", "bench"]


def test_get_missing_returns_none(fixture_entries):
    m = _merged(fixture_entries)
    assert get(m, "nope") is None
    assert get(m, "jais-30b")["id"] == "jais-30b"


def test_recommend_ranks_papers_below_datasets_unless_requested():
    base = {"country": "INTL", "org": "x", "license": "mit", "modality": "text", "tasks": ["asr"], "links": {"paper": "https://arxiv.org/abs/1"}}
    entries = [
        dict(base, id="p", name="Aaa Paper", type="paper", year=2024),
        dict(base, id="d", name="Zzz Data", type="dataset"),
        dict(base, id="m", name="Mmm Model", type="asr"),
    ]
    assert [r["id"] for r in recommend(entries, "asr", limit=5)] == ["m", "d", "p"]
    assert [r["id"] for r in recommend(entries, "asr", type="paper")] == ["p"]


def test_load_doc_returns_whole_json(tmp_path):
    p = tmp_path / "atlas.json"
    p.write_text(json.dumps({"entries": [{"id": "x"}], "lineage": {"roots": []}}), encoding="utf-8")
    assert load_doc(p) == {"entries": [{"id": "x"}], "lineage": {"roots": []}}
    assert load_atlas(p) == [{"id": "x"}]
