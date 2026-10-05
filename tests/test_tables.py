import re

from atlas.render_readme import COLUMNS, render_tables

DATE = "2026-10-05"


def test_llm_table_has_all_rows_and_index_counts(fixture_entries):
    base = dict(fixture_entries[0], type="llm", links={})
    many = [dict(base, id=f"syn-{i:02d}", name=f"Syn {i:02d}", metrics={"downloads": 1000 - i}) for i in range(25)]
    entries = [e for e in fixture_entries if e["type"] != "llm"] + many
    out = render_tables(entries, DATE)
    llm = out["docs/tables/llm.md"]
    assert len([l for l in llm.splitlines() if l.startswith("| Syn ")]) == 25
    assert "](../../README.md)" in llm and "#type=llm" in llm
    assert llm.rstrip().endswith(f"_Generated {DATE}. Do not edit by hand._")
    index = out["docs/tables/README.md"]
    for t in COLUMNS:
        n = sum(1 for e in entries if e["type"] == t)
        assert re.search(rf"\]\({t}\.md\) \| {n} \|", index), t
        assert f"docs/tables/{t}.md" in out
    assert "| 25 |" in index


def test_build_writes_tables(tmp_path):
    import subprocess, sys
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    r = subprocess.run([sys.executable, "scripts/build.py", "build", "--skip-enrich", "--date", DATE,
                        "--data", "tests/fixtures/data", "--out", str(tmp_path)], cwd=root, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "docs" / "tables" / "llm.md").is_file()
    assert (tmp_path / "docs" / "tables" / "README.md").is_file()
