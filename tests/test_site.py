"""The static map site in site/: files present, no third-party scripts, and the pure filter logic."""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"


def _node() -> str | None:
    found = shutil.which("node")
    if found:
        return found
    local = Path.home() / ".local" / "opt" / "node" / "bin" / "node"
    return str(local) if local.exists() else None


def test_site_files_exist_and_are_wired():
    for name in ("index.html", "app.js", "map.js", "styles.css", "vendor/d3.min.js", "vendor/topojson-client.min.js",
                 "vendor/README.md", "geo/countries-110m.json", "geo/centroids.json"):
        assert (SITE / name).is_file(), name
    html = (SITE / "index.html").read_text(encoding="utf-8")
    assert re.search(r'<script[^>]+src="app\.js"', html)
    assert re.search(r'<script[^>]+src="map\.js"', html)
    centroids = json.loads((SITE / "geo" / "centroids.json").read_text(encoding="utf-8"))
    assert set(centroids["countries"]) == {"SA", "AE", "EG", "QA", "MA", "JO", "TN", "LB", "KW", "OM", "BH",
                                         "DZ", "LY", "SD", "IQ", "SY", "YE", "PS", "MR", "SO", "DJ", "KM"}
    assert re.search(r'<link[^>]+href="styles\.css"', html)
    assert 'id="wanted"' in html and 'id="wanted-list"' in html and 'id="wanted-recent"' in html


def test_no_remote_scripts_or_cdns():
    html = (SITE / "index.html").read_text(encoding="utf-8")
    srcs = re.findall(r'<script[^>]+src="([^"]+)"', html)
    assert srcs, "no scripts found"
    for src in srcs:
        assert src in ("app.js", "map.js") or (src.startswith("vendor/") and ".." not in src), src
        assert (SITE / src).is_file(), src
    for href in re.findall(r'<link[^>]+href="(https?://[^"]+)"', html):
        assert href.startswith(("https://fonts.googleapis.com", "https://fonts.gstatic.com")), href
    for name in ("app.js", "map.js"):
        js = (SITE / name).read_text(encoding="utf-8")
        assert "http://" not in js, name
        assert not re.search(r"(import|importScripts|src\s*=)\s*\(?[\"']https://", js), name
        for url in re.findall(r"https://[^\s\"']+", js):
            assert url.startswith("https://fonts.googleapis.com"), url


NODE_SMOKE = r"""
const atlas = require(process.argv[2]);
const data = require(process.argv[3]);
const map = require(process.argv[4]);
const E = data.entries;
const out = {
  tts_on_device: atlas.filter(E, {type: "tts", on_device: true}).length,
  whisper: atlas.filter(E, {q: "WHISPER"}).length,
  folds: atlas.fold("\u0625\u0639\u0631\u0627\u0628") === atlas.fold("\u0627\u0639\u0631\u0627\u0628"),
  all: atlas.filter(E, {}).length,
  paper_n: atlas.filter(E, {type: "paper"}).length,
  paper_all_papers: atlas.filter(E, {type: "paper"}).every(e => e.type === "paper"),
  paper_parsed: atlas.parseHash("#type=paper").type,
  paper_cell: map.cellMax(E.concat([{type: "paper", country: "INTL", metrics: {downloads: 9e12}}]), true).key,
  intl_cell: map.cellMax(E, true).key,
  nc: atlas.licenseClass("cc-by-nc-4.0"), open: atlas.licenseClass("apache-2.0"),
  unknown: atlas.licenseClass("unknown"), prop: atlas.licenseClass("proprietary"),
  fair: atlas.licenseClass("fair-noncommercial-research-license"), falcon: atlas.licenseClass("falcon-llm-license"),
  parsed: atlas.parseHash("#q=whisper%20v3&type=asr,tts&country=EG&on_device=1"),
  roundtrip: atlas.serializeHash(atlas.parseHash("#q=whisper&type=asr&country=EG")),
  rec: atlas.recommendCall({type: "tts", dialect: "egy", on_device: true, license: "open"}),
  srch: atlas.searchCall({q: "speech", country: "EG", type: "tts"}),
  view_grid: map.hashState("#view=grid"),
  view_mixed: map.hashState("#country=EG&view=grid&type=tts"),
  view_map: map.hashState("#view=map&country=EG"),
  steps: [0, 1, 7, 29, 86, 161].map(n => map.choroplethStep(n, 161)),
  step_range: [0, 1, 2, 5, 10, 50, 100, 1000].every(m => [0, 1, 2, 3, 5, 9, 40, 100].every(n => {
    const s = map.choroplethStep(n, m); return s >= 0 && s <= 4 && Number.isInteger(s); })),
  radius: [map.bubbleRadius(0, 1e6), map.bubbleRadius(1e6, 1e6), map.bubbleRadius(1e9, 1e6)],
  layout: map.bubbleLayout({tts: {n: 2, downloads: 50}, llm: {n: 5, downloads: 9000}, asr: {n: 1, downloads: 0}}),
  layout_again: map.bubbleLayout({asr: {n: 1, downloads: 0}, llm: {n: 5, downloads: 9000}, tts: {n: 2, downloads: 50}}),
  layout_one: map.bubbleLayout({dataset: {n: 3, downloads: 10}}),
  arab_max: map.cellMax(E, false),
  intl_max: map.cellMax(E, true),
  arab_top_r: map.bubbleRadius(map.cellMax(E, false).downloads, map.cellMax(E, false).downloads),
  wanted_rows: atlas.wantedRows(data.wanted),
  wanted_absent: atlas.wantedRows(undefined),
  wanted_synth: atlas.wantedRows([
    {id: "a", title: "A", why: "w", status: "open", recent: false, hash: "#type=tts"},
    {id: "b", title: "B", why: "w", status: "filled", recent: true, filled_on: "2026-10-01", by: ["x/y"], hash: "#q=z"},
    {id: "c", title: "C", why: "w", status: "filled", recent: false, by: ["q"], hash: ""},
    {id: "d", title: "D", why: "w", status: "open", recent: false}]),
  wanted_canon: (data.wanted || []).every(w => !w.hash || atlas.serializeHash(atlas.parseHash(w.hash)) === w.hash),
  layout_skip: map.bubbleLayout({llm: {n: 0, downloads: 0}, ocr: {n: 1, downloads: 0}}).length,
};
console.log(JSON.stringify(out));
"""


def test_filter_logic_in_node(tmp_path):
    node = _node()
    if not node:
        pytest.skip("node is not installed; skipping the app.js smoke test")
    script = tmp_path / "smoke.js"
    script.write_text(NODE_SMOKE, encoding="utf-8")
    res = subprocess.run(
        [node, str(script), str(SITE / "app.js"), str(ROOT / "dist" / "atlas.json"), str(SITE / "map.js")],
        capture_output=True, text=True, timeout=60, env={**os.environ, "NODE_NO_WARNINGS": "1"},
    )
    assert res.returncode == 0, res.stderr
    out = json.loads(res.stdout)
    count = json.loads((ROOT / "dist" / "atlas.json").read_text(encoding="utf-8"))["count"]
    assert out["tts_on_device"] >= 1
    assert out["whisper"] >= 5
    assert out["all"] == count
    assert out["paper_n"] == sum(1 for e in json.loads((ROOT / "dist" / "atlas.json").read_text(encoding="utf-8"))["entries"] if e["type"] == "paper")
    assert out["paper_all_papers"] is True
    assert out["paper_parsed"] == ["paper"]
    assert out["paper_cell"] == out["intl_cell"]  # papers never count toward map bubbles
    assert out["folds"] is True
    assert (out["nc"], out["open"], out["unknown"], out["prop"]) == ("nc", "open", "unknown", "unknown")
    assert (out["fair"], out["falcon"]) == ("nc", "open")
    assert out["parsed"] == {
        "q": "whisper v3", "type": ["asr", "tts"], "country": ["EG"], "dialect": [], "license": [], "on_device": True,
        "view": "map",
    }
    assert out["roundtrip"] == "#q=whisper&type=asr&country=EG"
    assert out["rec"] == 'recommend(task="tts", type="tts", dialect="egy", on_device=True, license_filter="open")'
    assert out["srch"] == 'search(query="speech", country="EG", type="tts")'

    # map.js pure helpers
    assert out["view_grid"] == "#view=grid"
    assert out["view_mixed"] == "#type=tts&country=EG&view=grid"
    assert out["view_map"] == "#country=EG"
    assert out["steps"] == sorted(out["steps"]) and out["steps"][0] == 0 and out["steps"][-1] == 4
    assert out["step_range"] is True
    assert out["radius"][0] == 4 and out["radius"][1] == 26 and out["radius"][2] == 26
    layout = out["layout"]
    assert [b["type"] for b in layout] == ["llm", "asr", "tts"]
    assert layout == out["layout_again"]
    pos = {(round(b["x"], 1), round(b["y"], 1)) for b in layout}
    assert len(pos) == 3
    for i, a in enumerate(layout):
        for b in layout[i + 1:]:
            assert ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5 >= a["r"] + b["r"] - 0.01
    assert layout[0]["x"] == 0 and layout[0]["y"] < 0  # first type sits at 12 o'clock
    assert len(out["layout_one"]) == 1 and out["layout_one"][0]["x"] == 0 and out["layout_one"][0]["y"] == 0
    assert out["layout_skip"] == 1
    assert not out["arab_max"]["key"].startswith("INTL|")
    assert out["intl_max"]["key"].startswith("INTL|")
    assert out["arab_top_r"] == 26

    # most-wanted panel
    wanted = json.loads((ROOT / "dist" / "atlas.json").read_text(encoding="utf-8"))["wanted"]
    rows = out["wanted_rows"]
    assert [r["id"] for r in rows["open"]] == [w["id"] for w in wanted if w["status"] == "open"]
    assert len(rows["open"]) > 0
    assert all(r["href"] == w["hash"] for r, w in zip(rows["open"], [w for w in wanted if w["status"] == "open"]))
    assert out["wanted_canon"] is True  # Python hash and JS hash agree
    assert out["wanted_absent"] == {"open": [], "recent": []}
    synth = out["wanted_synth"]
    assert [r["id"] for r in synth["open"]] == ["a", "d"] and synth["open"][1]["href"] == "#"
    assert [r["id"] for r in synth["recent"]] == ["b"]
    assert synth["recent"][0]["href"] == "#q=x%2Fy" and synth["recent"][0]["filled_on"] == "2026-10-01"
