import json
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path

from atlas.enrich import build_hf_ids, merge_metrics
from atlas.lineage import build_lineage
from atlas.render_tree import MAX_PER_ROOT, render_tree_block, render_tree_svg, reused_datasets

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = Path(__file__).parent / "snapshots" / "tree.svg"
NS = "{http://www.w3.org/2000/svg}"


def _merged(entries):
    ids = build_hf_ids(entries)
    cache = {i: {"downloads": 10 ** n, "likes": 1, "lastModified": None} for n, i in enumerate(ids, 1)}
    return merge_metrics(entries, cache)


def _with_bases(fixture_entries):
    out = []
    for e in fixture_entries:
        e = dict(e)
        if e["id"] == "silma-9b":
            e["base_model"] = ["google/gemma-2-9b"]
        elif e["id"] == "allam-7b":
            e["base_model"] = ["from-scratch"]
        out.append(e)
    return out


def _render(entries):
    merged = _merged(entries)
    return render_tree_svg(merged, build_lineage(merged), "2026-10-04")


def _llama_tunes(n):
    return [{"id": f"tune-{i:02d}", "name": f"Tune {i:02d}", "type": "llm", "country": "EG", "org": "Lab",
             "license": "mit", "modality": "text", "tasks": ["chat"], "base_model": ["meta-llama/Llama-3.1-8B"],
             "links": {"hf": f"https://huggingface.co/lab/tune-{i:02d}"}} for i in range(n)]


def test_tree_svg_matches_snapshot(fixture_entries):
    out = _render(_with_bases(fixture_entries))
    if os.environ.get("UPDATE_SNAPSHOTS"):
        SNAPSHOT.write_text(out, encoding="utf-8")
    assert out == SNAPSHOT.read_text(encoding="utf-8")


def test_tree_svg_well_formed_and_escaped(fixture_entries):
    odd = dict(_llama_tunes(1)[0], id="odd", name="A&B <x>")
    svg = _render(_with_bases(fixture_entries) + [odd])
    root = ET.fromstring(svg)
    assert root.tag == f"{NS}svg"
    titles = [t.text or "" for t in root.iter(f"{NS}title")]
    assert any("A&B <x>" in t for t in titles)
    assert "A&amp;B &lt;x&gt;" in svg


def test_tree_has_dark_mode(fixture_entries):
    assert "prefers-color-scheme: dark" in _render(_with_bases(fixture_entries))


def test_tree_caps_per_root():
    svg = _render(_llama_tunes(20))
    root = ET.fromstring(svg)
    links = [a for a in root.iter(f"{NS}a") if a.find(f"{NS}rect") is not None]
    models = [a for a in links if "huggingface.co/lab/tune-" in a.get("href", "")]
    assert len(models) == MAX_PER_ROOT == 12
    assert svg.count("+8 more") == 1


def test_tree_deterministic(fixture_entries):
    merged = _merged(_with_bases(fixture_entries) + _llama_tunes(15))
    shuffled = merged[:]
    random.Random(7).shuffle(shuffled)
    a = render_tree_svg(merged, build_lineage(merged), "2026-10-04")
    assert a == render_tree_svg(shuffled, build_lineage(shuffled), "2026-10-04")


def test_tree_real_data_under_600kb():
    from atlas.enrich import apply_cached_licenses
    from atlas.load import load_entries

    data = ROOT / "data"
    entries = load_entries(data)
    cache_path = data / ".cache" / "hf.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    merged = merge_metrics(apply_cached_licenses(entries, cache), cache)
    svg = render_tree_svg(merged, build_lineage(merged), "2026-10-04")
    ET.fromstring(svg)
    assert len(svg.encode("utf-8")) < 600_000


def test_reused_datasets():
    merged = [
        {"id": "ds-a", "name": "DS A", "type": "dataset", "tasks": ["x"]},
        {"id": "ds-b", "name": "DS B", "type": "dataset", "tasks": ["x"]},
        {"id": "m1", "name": "M1", "type": "llm", "tasks": ["chat"], "tags": ["DS-A"]},
        {"id": "m2", "name": "M2", "type": "asr", "tasks": ["ds-a"]},
        {"id": "d3", "name": "D3", "type": "dataset", "tasks": ["ds-b"]},
    ]
    assert reused_datasets(merged) == [("ds-a", "DS A", 2)]


def test_tree_block(fixture_entries):
    merged = _merged(_with_bases(fixture_entries))
    merged.append({"id": "m-tag", "name": "Tagger", "type": "llm", "tasks": ["chat"], "tags": ["cidar"], "links": {}})
    block = render_tree_block(merged, build_lineage(merged))
    assert '<img src="assets/tree.svg"' in block
    assert "| Base family | Models | Most downloaded |" in block
    assert "| Dataset | Models citing it |" in block
    no_ds = render_tree_block(_merged(_with_bases(fixture_entries)), build_lineage(_merged(_with_bases(fixture_entries))))
    assert "| Dataset | Models citing it |" not in no_ds
