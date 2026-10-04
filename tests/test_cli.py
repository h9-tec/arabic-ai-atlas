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
    readme.write_text(readme.read_text(encoding="utf-8") + "x", encoding="utf-8")
    bad = run("build", "--check", "--skip-enrich", "--date", "2026-10-04", "--data", FIX, "--out", str(tmp_path))
    assert bad.returncode == 1
    assert "README.md" in bad.stderr
