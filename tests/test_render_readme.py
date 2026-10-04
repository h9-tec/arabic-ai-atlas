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
