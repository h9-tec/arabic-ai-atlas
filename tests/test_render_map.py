import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from atlas.enrich import build_hf_ids, merge_metrics
from atlas.render_map import render_svg

SNAPSHOT = Path(__file__).parent / "snapshots" / "map.svg"
NS = "{http://www.w3.org/2000/svg}"


def _merged(entries):
    ids = build_hf_ids(entries)
    cache = {i: {"downloads": 10 ** n, "likes": 1, "lastModified": None} for n, i in enumerate(ids, 1)}
    return merge_metrics(entries, cache)


def _titles(svg):
    root = ET.fromstring(svg)
    return [t.text for t in root.iter(f"{NS}title")]


def test_svg_matches_snapshot(fixture_entries):
    out = render_svg(_merged(fixture_entries), "2026-10-04")
    if os.environ.get("UPDATE_SNAPSHOTS"):
        SNAPSHOT.write_text(out, encoding="utf-8")
    assert out == SNAPSHOT.read_text(encoding="utf-8")


def test_svg_is_well_formed_xml(fixture_entries):
    e = dict(fixture_entries[0], id="rd", name="R&D <lab>", org='"Q" & Co', type="llm")
    svg = render_svg(_merged(fixture_entries + [e]), "2026-10-04")
    root = ET.fromstring(svg)
    assert root.tag == f"{NS}svg"
    assert any(t.startswith("R&D <lab> · \"Q\" & Co") for t in _titles(svg))
    assert "Generated 2026-10-04 from 7 entries · github.com/h9-tec/arabic-ai-atlas" in svg


def test_no_hf_entry_has_min_width(fixture_entries):
    svg = render_svg(_merged(fixture_entries), "2026-10-04")
    m = re.search(r"<title>Fish Speech \(Arabic\)[^<]*</title><rect ([^>]*)/>", svg)
    assert m, "fish-speech-ar node missing"
    assert 'width="72"' in m.group(1)
    assert 'href="https://github.com/fishaudio/fish-speech"' in svg


def test_cell_caps_at_8_with_more_node(fixture_entries):
    base = next(e for e in fixture_entries if e["id"] == "allam-7b")
    entries, cache = [], {}
    for i in range(12):
        hf = f"https://huggingface.co/synth/m{i:02d}"
        entries.append(dict(base, id=f"synth-{i:02d}", name=f"Synth {i:02d}", links={"hf": hf}))
        cache[f"synth/m{i:02d}"] = {"downloads": (i + 1) * 1000, "likes": 0, "lastModified": None}
    svg = render_svg(merge_metrics(entries, cache), "2026-10-04")
    named = [t for t in _titles(svg) if t.startswith("Synth ")]
    assert sorted(t.split(" · ")[0] for t in named) == [f"Synth {i:02d}" for i in range(7, 12)]
    assert svg.count(">+7 more<") == 1
    assert 'href="https://github.com/h9-tec/arabic-ai-atlas#-large-language-models"' in svg


def test_orgs_not_drawn(fixture_entries):
    org = dict(fixture_entries[0], id="some-org", name="Zebra Org", type="org")
    skill = dict(fixture_entries[0], id="some-skill", name="Yak Skill", type="agent-skill")
    svg = render_svg(_merged(fixture_entries + [org, skill]), "2026-10-04")
    assert "Zebra Org" not in svg
    assert "Yak Skill" not in svg


def test_svg_has_dark_mode_media_query(fixture_entries):
    svg = render_svg(_merged(fixture_entries), "2026-10-04")
    assert "@media (prefers-color-scheme: dark)" in svg
    assert "#0D1117" in svg and "#FFFFFF" in svg
    assert 'class="bg"' in svg


def test_more_node_contrast_and_intl_symbol(fixture_entries):
    svg = render_svg(_merged(fixture_entries), "2026-10-04")
    assert ".more { fill: #6B7280; }" in svg  # white label needs >= 4.5:1
    assert "🌍 INTL</text>" in svg  # same globe as the README country column
    assert "🌐 OTHER</text>" in svg


def test_new_arab_league_country_lands_in_other_column(fixture_entries):
    from atlas.render_map import COL_X, GUTTER, OTHER, PAD, _column

    assert {"DZ", "LY", "SD", "IQ", "SY", "YE", "PS", "MR", "SO", "DJ", "KM"} <= OTHER
    e = dict(fixture_entries[0], id="dz-model", name="DZ Model", type="llm", country="DZ",
             links={"hf": "https://huggingface.co/dz/model"})
    assert _column(e) == "OTHER"
    svg = render_svg(_merged(fixture_entries + [e]), "2026-10-04")
    x = float(re.search(r'<a [^>]*>\s*<title>DZ Model[^<]*</title><rect [^>]*? x="([\d.]+)"', svg).group(1))
    left = PAD + GUTTER + COL_X["OTHER"][0]
    assert left <= x <= left + COL_X["OTHER"][1]


def test_papers_not_drawn_on_grid(fixture_entries):
    paper = dict(fixture_entries[0], id="some-paper", name="Quokka Paper", type="paper", year=2024, links={"paper": "https://arxiv.org/abs/1"})
    base = render_svg(_merged(fixture_entries), "2026-10-04")
    svg = render_svg(_merged(fixture_entries + [paper]), "2026-10-04")
    assert "Quokka Paper" not in svg
    n = len(fixture_entries)
    assert svg.replace(f"{n + 1} entries", f"{n} entries") == base  # only the header totals change
