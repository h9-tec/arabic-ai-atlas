import pytest

from atlas.enrich import build_hf_ids, hf_id_from_url, merge_metrics
from atlas.render_json import build_atlas_json, build_llms_txt


def _merged(fixture_entries):
    ids = build_hf_ids(fixture_entries)
    cache = {i: {"downloads": n * 10, "likes": 1, "lastModified": None} for n, i in enumerate(ids, 1)}
    return merge_metrics(fixture_entries, cache), cache


def test_atlas_json_sorted_and_clean(fixture_entries):
    merged, cache = _merged(fixture_entries)
    doc = build_atlas_json(merged, "2026-10-04")
    assert doc["count"] == 6
    assert doc["generated_at"] == "2026-10-04"
    assert all("_file" not in e for e in doc["entries"])
    downloads = [(e["metrics"] or {}).get("downloads", 0) for e in doc["entries"]]
    assert downloads == sorted(downloads, reverse=True)
    assert doc["entries"][0]["metrics"]["downloads"] == max(m["downloads"] for m in cache.values())


@pytest.mark.parametrize("year", [2025, 0])
def test_atlas_json_mixed_entries_with_tied_sort_keys(year):
    merged = [
        {"id": "model-b", "name": "Beta", "type": "llm", "metrics": {"downloads": year}},
        {"id": "paper-b", "name": "Bravo", "type": "paper", "year": year},
        {"id": "model-a", "name": "Alpha", "type": "llm", "metrics": {"downloads": year}},
        {"id": "paper-a", "name": "Alfa", "type": "paper", "year": year},
        {"id": "paper-cited", "name": "Cited", "type": "paper", "year": year, "citations": 9},
    ]
    doc = build_atlas_json(merged, "2026-10-06")
    assert [e["id"] for e in doc["entries"]] == [
        "paper-cited", "paper-a", "model-a", "model-b", "paper-b",
    ]


def test_llms_txt_has_sections_and_links(fixture_entries):
    merged, _ = _merged(fixture_entries)
    txt = build_llms_txt(merged, "2026-10-04")
    assert txt.startswith("# Arabic AI Atlas\n\n> ")
    assert "6 entries, generated 2026-10-04." in txt
    assert "## Models" in txt
    assert "## Datasets" in txt
    assert "https://huggingface.co/inceptionai/jais-30b-v3" in txt
    assert "## Optional" in txt
    assert "(https://raw.githubusercontent.com/h9-tec/arabic-ai-atlas/main/dist/atlas.json)" in txt
    assert "(https://github.com/h9-tec/arabic-ai-atlas#readme)" in txt
    assert "](dist/" not in txt  # relative links 404 when llms.txt is fetched raw
    assert "## Organizations" not in txt


def test_llms_txt_caps_section_at_25():
    merged = [
        {"id": f"m{i}", "name": f"M{i:02d}", "type": "llm", "links": {"github": f"https://g/{i}"}, "notes": "", "metrics": None}
        for i in range(40)
    ]
    txt = build_llms_txt(merged, "2026-10-04")
    assert txt.count("- [M") == 25
    assert "- [M00](https://g/0)\n" in txt


def test_llms_txt_papers_section(fixture_entries):
    merged, _ = _merged(fixture_entries)
    base = dict(merged[0], type="paper", metrics=None, links={"paper": "https://arxiv.org/abs/2506.01340"})
    papers = [dict(base, id="p1", name="Older", year=2020), dict(base, id="p2", name="Newer", year=2025),
              dict(base, id="p3", name="Newer cited", year=2025, citations=9)]
    txt = build_llms_txt(merged + papers, "2026-10-04")
    section = txt.split("## Papers")[1].split("## Optional")[0]
    assert [l.split("]")[0][3:] for l in section.splitlines() if l.startswith("- ")] == ["Newer cited", "Newer", "Older"]
    assert "(https://arxiv.org/abs/2506.01340)" in section
    many = [dict(base, id=f"m{i}", name=f"P{i:02d}", year=2024) for i in range(40)]
    capped = build_llms_txt(merged + many, "2026-10-04").split("## Papers")[1].split("## Optional")[0]
    assert capped.count("\n- ") == 25
