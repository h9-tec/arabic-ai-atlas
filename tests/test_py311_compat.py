import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_compiles_under_python_311():
    if subprocess.run(["uv", "python", "find", "3.11"], capture_output=True).returncode != 0:
        pytest.skip("python 3.11 not available")
    r = subprocess.run(["uv", "run", "--python", "3.11", "python", "-m", "compileall", "-q", "atlas", "scripts", "mcp"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
