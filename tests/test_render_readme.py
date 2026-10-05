import os
from pathlib import Path

from atlas.render_readme import fmt_downloads, load_shipped_skills, render_readme

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = (ROOT / "templates" / "README.tmpl.md").read_text(encoding="utf-8")
SNAPSHOT = Path(__file__).parent / "snapshots" / "README.md"


def render(entries, skills=()):
    return render_readme(entries, TEMPLATE, "2026-10-04", list(skills))


def test_readme_matches_snapshot(fixture_entries):
    out = render(fixture_entries)
    if os.environ.get("UPDATE_SNAPSHOTS"):
        SNAPSHOT.write_text(out, encoding="utf-8")
    assert out == SNAPSHOT.read_text(encoding="utf-8")


def test_missing_metrics_show_dash(fixture_entries):
    row = next(l for l in render(fixture_entries).splitlines() if "Fish Speech (Arabic)" in l and l.startswith("|"))
    assert "| — | — |" in row


def test_pipe_in_name_is_escaped(fixture_entries):
    e = dict(fixture_entries[0], id="ab", name="A|B", type="llm")
    out = render(fixture_entries + [e])
    assert "A\\|B" in out


def test_ampersand_safe(fixture_entries):
    e = dict(fixture_entries[0], id="rd", name="R&D Lab", type="org")
    assert "R&D Lab" in render(fixture_entries + [e])


def test_fmt_downloads():
    assert [fmt_downloads(n) for n in (None, 980, 340_000, 1_200_000)] == ["—", "980", "340K", "1.2M"]


def test_shipped_skills(tmp_path):
    assert load_shipped_skills(tmp_path / "nope") == []
    d = tmp_path / "x-skill"
    d.mkdir()
    (d / "SKILL.md").write_text("---\nname: x\ndescription: Does x\n---\nbody\n", encoding="utf-8")
    assert load_shipped_skills(tmp_path) == [{"name": "x", "description": "Does x", "path": "skills/x-skill"}]


def test_date_badge_doubles_dashes(fixture_entries):
    out = render(fixture_entries)
    assert "updated-2026--10--04-555" in out
    assert "updated-2026-10-04-" not in out


import pytest


@pytest.mark.parametrize("url,label", [
    ("https://huggingface.co/org/model", "Model"),
    ("https://huggingface.co/datasets/org/ds", "Dataset"),
    ("https://huggingface.co/papers/2401.00001", "Paper"),
    ("https://huggingface.co/spaces/org/app", "Space"),
    ("https://huggingface.co/collections/org/c-123", "Collection"),
    ("https://huggingface.co/org", "Hub"),
])
def test_hf_badge_label(url, label):
    from atlas.render_readme import badges
    assert f"https://img.shields.io/badge/-{label}-FFD21E" in badges({"links": {"hf": url}})


def test_papers_section_sorted_year_citations_title(fixture_entries):
    base = dict(fixture_entries[0], type="paper", modality="text", license="unknown", org="Various", links={"paper": "https://arxiv.org/abs/1"})
    papers = [
        dict(base, id="p-old", name="Old", year=2020, venue="ACL 2020", tasks=["survey", "llm"]),
        dict(base, id="p-new-lo", name="Zeta", year=2025, venue="arXiv 2025", tasks=["asr"], citations=1),
        dict(base, id="p-new-hi", name="Alpha", year=2025, venue="arXiv 2025", tasks=["asr"], citations=50),
    ]
    out = render(fixture_entries + papers)
    assert "- [📄 Papers](#-papers)" in out
    section = out.split("## 📄 Papers")[1].split("## 🏢")[0]
    assert "| Title | Venue | Year | Topic | Links |" in section
    rows = [l for l in section.splitlines() if l.startswith("| ") and "Title" not in l and "---" not in l[:6]]
    assert [r.split(" | ")[0][2:] for r in rows] == ["Alpha", "Zeta", "Old"]
    assert "| Old | ACL 2020 | 2020 | survey, llm |" in section
    assert out.index("## 🏆 Benchmarks") < out.index("## 📄 Papers")
    assert "from 9 entries" in out  # hero total counts papers


def _many(fixture_entries, n, type_="llm"):
    base = dict(fixture_entries[0], type=type_, links={})
    return [dict(base, id=f"syn-{i:02d}", name=f"Syn {i:02d}", metrics={"downloads": 1000 - i}) for i in range(n)]


def test_section_capped_at_20_rows(fixture_entries):
    others = [e for e in fixture_entries if e["type"] != "llm"]
    out = render(others + _many(fixture_entries, 25))
    section = out.split("## 🧠 Large Language Models")[1].split("\n## ")[0]
    rows = [l for l in section.splitlines() if l.startswith("| Syn ")]
    assert len(rows) == 20
    assert rows[0].startswith("| Syn 00 |") and rows[-1].startswith("| Syn 19 |")
    assert ("_Showing 20 of 25 · [see all 25 on the interactive map]"
            "(https://h9-tec.github.io/arabic-ai-atlas/#type=llm) · [full table](docs/tables/llm.md)_") in section


def test_no_showing_line_when_not_capped(fixture_entries):
    assert "_Showing" not in render(fixture_entries)


def test_country_table(fixture_entries):
    out = render(fixture_entries)
    sec = out.split("### Entries by country")[1].split("###")[0]
    assert "| Country | Entries | LLM | ASR | TTS | OCR | Embedding | Datasets | Tools | Benchmarks | Papers | Orgs |" in sec
    assert "(https://h9-tec.github.io/arabic-ai-atlas/#country=" in sec


def test_heading_anchors_match_map_anchors(fixture_entries):
    import re
    from urllib.parse import unquote
    from atlas.render_map import ANCHORS
    out = render(fixture_entries)
    found = {}
    for line in out.splitlines():
        m = re.match(r"## (.+)$", line)
        if m:
            h = m.group(1)
            slug = "".join(c for c in h.lower() if c.isalnum() or c in " -_" or ord(c) == 0xFE0F).replace(" ", "-")
            found[slug] = h
    for anchor in ANCHORS.values():
        assert unquote(anchor.lstrip("#")) in found, anchor
