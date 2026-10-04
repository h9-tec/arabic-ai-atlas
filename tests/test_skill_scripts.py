import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
NAMES = ["arabic-ai-advisor", "tashkeel-check", "rtl-bidi-lint",
         "arabic-dialect-prompts", "arabic-token-cost"]
DIALECTS = ["msa", "egy", "gulf", "lev", "magh", "iraqi", "sudanese", "yemeni",
            "classical", "mixed"]


def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, SKILLS / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bidi = _load("rtl-bidi-lint/bidi_lint.py", "bidi_lint")
tc = _load("arabic-token-cost/token_cost.py", "token_cost")


def codes(text):
    return [c for _, c, _ in bidi.lint_text(text)]


def test_bidi_mixed_digits():
    assert "MIXED_DIGITS" in codes("عدد 3 و ٤")


def test_bidi_unbalanced_isolate():
    assert "UNBALANCED_ISOLATE" in codes("نص ⁨ بدون إغلاق")
    assert "UNBALANCED_ISOLATE" not in codes("نص ⁨abc⁩ مغلق")


def test_bidi_clean_text_no_findings():
    assert bidi.lint_text("مرحبا بالعالم") == []


def test_bidi_ltr_mark_in_arabic():
    assert "LTR_MARK_IN_ARABIC" in codes("مر‎حبا")
    assert "LTR_MARK_IN_ARABIC" not in codes("abc‎ def")


def test_bidi_hardcoded_ltr_and_line_numbers():
    res = bidi.lint_text('ok\n<p dir="ltr">مرحبا</p>')
    assert res[0][0] == 2 and res[0][1] == "HARDCODED_LTR"
    assert bidi.lint_text('<p dir="ltr">hello</p>') == []


def test_bidi_cli_exit_codes(tmp_path):
    bad = tmp_path / "a.txt"
    bad.write_text("عدد 3 و ٤\n", encoding="utf-8")
    good = tmp_path / "b.txt"
    good.write_text("مرحبا\n", encoding="utf-8")
    script = str(SKILLS / "rtl-bidi-lint/bidi_lint.py")
    r = subprocess.run([sys.executable, script, str(bad)], capture_output=True, text=True)
    assert r.returncode == 1 and f"{bad}:1: MIXED_DIGITS" in r.stdout
    r = subprocess.run([sys.executable, script, str(good)], capture_output=True, text=True)
    assert r.returncode == 0


def test_fertility():
    assert tc.fertility(10, "a b c d") == 2.5
    assert tc.fertility(5, "   ") == 0.0


def test_token_cost_import_error_exit_2():
    script = str(SKILLS / "arabic-token-cost/token_cost.py")
    code = ("import sys, runpy; sys.modules['transformers'] = None; "
            f"sys.argv = ['t', '--text', 'مرحبا بالعالم']; runpy.run_path({script!r}, run_name='__main__')")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert r.returncode == 2
    assert "install transformers to run token cost: uv pip install transformers" in r.stderr


def test_skill_dirs_and_readme_list_five_skills():
    for n in NAMES:
        assert (SKILLS / n / "SKILL.md").is_file(), n
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for n in NAMES:
        assert f"| {n} |" in readme, n


def test_dialects_table_has_ten_rows():
    text = (SKILLS / "arabic-dialect-prompts/dialects.md").read_text(encoding="utf-8")
    rows = [l for l in text.splitlines() if l.startswith("| ") and not l.startswith("| Code") and not l.startswith("| ---")]
    assert [r.split("|")[1].strip().strip("`") for r in rows] == DIALECTS
    assert "Common failure: drift to MSA" in text
