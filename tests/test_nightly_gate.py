"""scripts/nightly_should_commit.sh: commit real changes, skip date-only refreshes."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "nightly_should_commit.sh"

pytestmark = pytest.mark.skipif(not shutil.which("git") or not shutil.which("bash"), reason="needs git and bash")


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "dist").mkdir()
    (tmp_path / "README.md").write_text("# Atlas\n_Generated 2026-10-03 from 5 entries._\n![x](badge-2026--10--03)\n")
    (tmp_path / "dist" / "atlas.json").write_text('{\n  "generated_at": "2026-10-03",\n  "count": 5\n}\n')
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "init")
    return tmp_path


def _gate(repo: Path) -> subprocess.CompletedProcess:
    _git(repo, "add", "-A")
    return subprocess.run(["bash", str(SCRIPT)], cwd=repo, capture_output=True, text=True)


def test_nothing_staged_skips(repo):
    assert _gate(repo).returncode == 1


def test_date_only_diff_skips(repo):
    (repo / "README.md").write_text("# Atlas\n_Generated 2026-10-04 from 5 entries._\n![x](badge-2026--10--04)\n")
    (repo / "dist" / "atlas.json").write_text('{\n  "generated_at": "2026-10-04",\n  "count": 5\n}\n')
    res = _gate(repo)
    assert res.returncode == 1, res.stdout
    assert "only dates" in res.stdout


def test_content_change_commits(repo):
    (repo / "dist" / "atlas.json").write_text('{\n  "generated_at": "2026-10-04",\n  "count": 6\n}\n')
    assert _gate(repo).returncode == 0


def test_added_line_commits(repo):
    (repo / "README.md").write_text("# Atlas\n_Generated 2026-10-03 from 5 entries._\n![x](badge-2026--10--03)\nnew row 2026-10-04\n")
    assert _gate(repo).returncode == 0


def test_other_file_commits(repo):
    (repo / "notes.txt").write_text("2026-10-04\n")
    assert _gate(repo).returncode == 0
