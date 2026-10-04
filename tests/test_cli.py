import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = str(ROOT / "scripts" / "build.py")
FIX = "tests/fixtures/data"


def run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args], cwd=ROOT, capture_output=True, text=True)


def test_cli_validate_exit_code(tmp_path):
    ok = run("validate", "--data", FIX)
    assert ok.returncode == 0, ok.stderr
    broken = tmp_path / "data"
    shutil.copytree(ROOT / FIX, broken)
    path = broken / "llms.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("country: AE", "country: XX", 1), encoding="utf-8")
    bad = run("validate", "--data", str(broken))
    assert bad.returncode == 1
    assert "llms.yaml:" in bad.stderr


def test_cli_build_writes_dist(tmp_path):
    res = run("build", "--skip-enrich", "--date", "2026-10-04", "--data", FIX, "--out", str(tmp_path))
    assert res.returncode == 0, res.stderr
    doc = json.loads((tmp_path / "dist" / "atlas.json").read_text(encoding="utf-8"))
    assert doc["count"] == 6
    assert doc["generated_at"] == "2026-10-04"
    assert (tmp_path / "dist" / "llms.txt").exists()


def test_cli_check_detects_drift(tmp_path):
    build = run("build", "--skip-enrich", "--date", "2026-10-04", "--data", FIX, "--out", str(tmp_path))
    assert build.returncode == 0, build.stderr
    ok = run("build", "--check", "--skip-enrich", "--date", "2026-10-04", "--data", FIX, "--out", str(tmp_path))
    assert ok.returncode == 0, ok.stderr
    # a different date alone is not drift
    redated = run("build", "--check", "--skip-enrich", "--date", "1999-01-01", "--data", FIX, "--out", str(tmp_path))
    assert redated.returncode == 0, redated.stderr
    readme = tmp_path / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\nx", encoding="utf-8")
    bad = run("build", "--check", "--skip-enrich", "--date", "2026-10-04", "--data", FIX, "--out", str(tmp_path))
    assert bad.returncode == 1
    assert "README.md" in bad.stderr
    assert "uv run python scripts/build.py build" in bad.stderr


def test_cli_check_catches_edit_on_dated_line(tmp_path):
    data = tmp_path / "data"
    shutil.copytree(ROOT / FIX, data)
    (data / ".cache").mkdir()
    cache = {"humain-ai/ALLaM-7B-Instruct-preview": {"downloads": 5, "likes": 1, "lastModified": "2026-09-01"}}
    (data / ".cache" / "hf.json").write_text(json.dumps(cache), encoding="utf-8")
    out = tmp_path / "out"
    build = run("build", "--skip-enrich", "--date", "2026-10-04", "--data", str(data), "--out", str(out))
    assert build.returncode == 0, build.stderr
    readme = out / "README.md"
    text = readme.read_text(encoding="utf-8")
    row = next(line for line in text.splitlines() if line.startswith("| ALLaM 7B |"))
    assert "2026-09-01" in row  # a dated row: the old check dropped it from the comparison
    readme.write_text(text.replace("| ALLaM 7B |", "| ALLaM HACKED |", 1), encoding="utf-8")
    bad = run("build", "--check", "--skip-enrich", "--data", str(data), "--out", str(out))
    assert bad.returncode == 1
    assert "drift: README.md" in bad.stderr


def test_cli_check_catches_edited_footer_date(tmp_path):
    build = run("build", "--skip-enrich", "--date", "2026-10-04", "--data", FIX, "--out", str(tmp_path))
    assert build.returncode == 0, build.stderr
    svg = tmp_path / "assets" / "map.svg"
    # the footer is a dated line; the old line-dropping check ignored edits here
    svg.write_text(svg.read_text(encoding="utf-8").replace("from 6 entries", "from 600 entries"), encoding="utf-8")
    bad = run("build", "--check", "--skip-enrich", "--data", FIX, "--out", str(tmp_path))
    assert bad.returncode == 1
    assert "drift: assets/map.svg" in bad.stderr
