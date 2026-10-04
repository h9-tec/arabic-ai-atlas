import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from atlas import geo
from atlas.enrich import build_hf_ids, merge_metrics
from atlas.render_geo import (BBOX, MAP_H, PROJ, WIDTH, bubble_layout, bubble_radius, choropleth_step,
                              render_geo_svg)

ROOT = Path(__file__).resolve().parent.parent
TOPO = json.loads((ROOT / "site" / "geo" / "countries-110m.json").read_text(encoding="utf-8"))
SNAPSHOT = Path(__file__).parent / "snapshots" / "geo.svg"
NS = "{http://www.w3.org/2000/svg}"


def _merged(entries):
    ids = build_hf_ids(entries)
    cache = {i: {"downloads": 10 ** n, "likes": 1, "lastModified": None} for n, i in enumerate(ids, 1)}
    return merge_metrics(entries, cache)


def _egypt():
    return next(f for f in geo.decode(TOPO) if f["id"] == "818")


# ---------- decoder ----------

def test_decoded_arc_count_matches_file():
    assert len(geo.decode_arcs(TOPO)) == len(TOPO["arcs"])


def test_arcs_are_absolute_lonlat():
    for arc in geo.decode_arcs(TOPO):
        for lon, lat in arc:
            assert -180.0001 <= lon <= 180.0001 and -90.0001 <= lat <= 90.0001


def test_features_carry_iso_numeric_ids():
    feats = geo.decode(TOPO)
    assert len(feats) == len(TOPO["objects"]["countries"]["geometries"])
    eg = _egypt()
    assert eg["name"] == "Egypt"
    assert len(eg["polygons"]) > 0 and all(len(ring) >= 4 for poly in eg["polygons"] for ring in poly)
    ring = eg["polygons"][0][0]
    assert ring[0] == pytest.approx(ring[-1])  # rings close


def test_negative_arc_index_reverses():
    topo = {"arcs": [[[0, 0], [2, 0], [0, 2]]], "objects": {"o": {"geometries": [
        {"type": "Polygon", "arcs": [[~0]], "id": "1"}]}}}
    ring = geo.decode(topo, "o")[0]["polygons"][0][0]
    assert ring == [(0, 2), (2, 0), (0, 0)]


# ---------- projection ----------

def test_cairo_lands_inside_egypt():
    for kind in ("mercator", "conic"):
        project = geo.fit(BBOX, 1600, 900, 0.06, kind=kind, rotate=-23.0 if kind == "conic" else 0.0)
        cx, cy = project(31.24, 30.04)
        rings = [[project(*p) for p in poly[0]] for poly in _egypt()["polygons"]]
        assert any(geo.point_in_ring(cx, cy, r) for r in rings), kind
        riyadh = project(46.7, 24.7)
        assert not any(geo.point_in_ring(*riyadh, r) for r in rings)


def test_fit_fills_the_padded_box():
    project = geo.fit((-10, 10, 60, 40), 1000, 500, 50)
    xs = [project(lon, lat)[0] for lon, lat in geo.bbox_outline((-10, 10, 60, 40))]
    ys = [project(lon, lat)[1] for lon, lat in geo.bbox_outline((-10, 10, 60, 40))]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    assert w == pytest.approx(900) or h == pytest.approx(400)
    assert min(xs) >= 50 - 1e-6 and max(xs) <= 950 + 1e-6 and min(ys) >= 50 - 1e-6 and max(ys) <= 450 + 1e-6
    assert project(0, 30)[1] < project(0, 20)[1]  # north is up


def test_conic_matches_d3_reference():
    # d3.geoConicConformal().parallels([18,34]).rotate([-23,0]).fitExtent([[96,60],[1504,940]], box)
    project = geo.fit(BBOX, 1600, 1000, 0.06, **PROJ)
    assert project(31.24, 30.04) == pytest.approx((933.0994159978497, 431.9346677980353))
    assert project(-13.2, 12.1) == pytest.approx((96.0, 689.6997345486745))


def test_clip_ring_to_rect():
    ring = [(-5, -5), (5, -5), (5, 5), (-5, 5)]
    assert sorted(geo.clip_ring(ring, 0, 0, 10, 10)) == [(0, 0), (0, 5), (5, 0), (5, 5)]


# ---------- helpers mirror site/map.js ----------

def test_helpers_match_map_js():
    assert choropleth_step(0, 100) == 0 and choropleth_step(100, 100) == 4
    assert bubble_radius(0, 1000) == 4 and bubble_radius(1000, 1000) == 26
    one = bubble_layout({"llm": {"n": 1, "downloads": 5}}, 100)
    assert (one[0]["x"], one[0]["y"]) == (0.0, 0.0)
    ring = bubble_layout({"llm": {"n": 2, "downloads": 100}, "asr": {"n": 1, "downloads": 1}}, 100)
    assert [it["type"] for it in ring] == ["llm", "asr"]
    assert ring[0]["x"] == pytest.approx(0, abs=0.01) and ring[0]["y"] < 0  # first bubble at 12 o'clock


# ---------- render ----------

def test_geo_svg_matches_snapshot(fixture_entries):
    out = render_geo_svg(_merged(fixture_entries), "2026-10-04")
    if os.environ.get("UPDATE_SNAPSHOTS"):
        SNAPSHOT.write_text(out, encoding="utf-8")
    assert out == SNAPSHOT.read_text(encoding="utf-8")


def test_geo_svg_is_well_formed_and_escaped(fixture_entries):
    e = dict(fixture_entries[0], id="rd", name="R&D <lab>", org='"Q" & Co', type="llm", country="EG",
             links={"hf": "https://huggingface.co/rd/lab"})
    entries = fixture_entries + [e]
    ids = build_hf_ids(entries)
    cache = {i: {"downloads": 10 ** n, "likes": 1, "lastModified": None} for n, i in enumerate(ids, 1)}
    svg = render_geo_svg(merge_metrics(entries, cache), "2026-10-04")
    root = ET.fromstring(svg)
    assert root.tag == f"{NS}svg"
    titles = [t.text for t in root.iter(f"{NS}title")]
    assert any("R&D <lab>" in t for t in titles)
    texts = [t.text for t in root.iter(f"{NS}text")]
    assert "مصر" in texts and "Egypt" in texts
    assert "دولي" in texts and any(t.startswith("International · ") for t in texts)
    assert "Generated 2026-10-04 from 7 entries · github.com/h9-tec/arabic-ai-atlas" in texts
    hrefs = [a.get("href") for a in root.iter(f"{NS}a")]
    assert "https://h9-tec.github.io/arabic-ai-atlas/#country=EG" in hrefs
    assert "https://h9-tec.github.io/arabic-ai-atlas/#country=EG&type=llm" in hrefs
    assert "https://h9-tec.github.io/arabic-ai-atlas/#country=INTL&type=tts" in hrefs


def test_geo_svg_has_dark_mode_and_frame(fixture_entries):
    svg = render_geo_svg(_merged(fixture_entries), "2026-10-04")
    assert "@media (prefers-color-scheme: dark)" in svg
    assert f'width="{WIDTH}"' in svg and f'<clipPath id="frame"><rect x="0" y="0" width="{WIDTH}" height="{MAP_H}"/>' in svg
    assert '<pattern id="hatch"' in svg


def test_geo_svg_real_data_under_600kb():
    from atlas.enrich import apply_cached_licenses
    from atlas.load import load_entries

    data = ROOT / "data"
    entries = load_entries(data)
    cache_path = data / ".cache" / "hf.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    svg = render_geo_svg(merge_metrics(apply_cached_licenses(entries, cache), cache), "2026-10-04")
    ET.fromstring(svg)
    assert len(svg.encode("utf-8")) < 600_000
    for code in ("KW", "BH", "QA", "AE", "LB"):
        block = svg.split(f'<g class="mark" data-code="{code}">', 1)[1].split("</g>", 1)[0]
        assert '<line class="leader"' in block, code
