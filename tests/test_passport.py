import importlib.util
import json
import sys
from pathlib import Path

from atlas.passport import load_probes, verify_passport

ROOT = Path(__file__).resolve().parent.parent
PROBES = load_probes(ROOT / "probes")
EXP = {"min_digits": 4}


def _cli():
    spec = importlib.util.spec_from_file_location("passport_cli", ROOT / "scripts" / "passport.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.main


def test_probe_loads():
    p = PROBES["arabic-indic-digits"]
    assert p["expected"] == EXP
    assert len(p["prompts"]) == 2
    assert list(PROBES) == sorted(PROBES)


def test_check():
    check = PROBES["arabic-indic-digits"]["check"]
    assert check("٢٠٢٦/١٠/٠٥", EXP) is True
    assert check("2026/10/05", EXP) is False
    assert check("٢٠٢٦ and 5", EXP) is False
    assert check("٢٠", EXP) is False


def _passport(output, passed, pid="arabic-indic-digits"):
    return {"model": "x/y", "date": "2026-10-05", "runner": "t", "results": {pid: {"pass": passed, "outputs": [output]}}}


def test_verify_consistent():
    assert verify_passport(_passport("٢٠٢٦/١٠/٠٥", True), PROBES) == []
    assert verify_passport(_passport("2026", False), PROBES) == []


def test_verify_mismatch_and_unknown():
    msgs = verify_passport(_passport("2026", True), PROBES)
    assert len(msgs) == 1 and "arabic-indic-digits" in msgs[0]
    msgs = verify_passport(_passport("x", True, pid="nope"), PROBES)
    assert len(msgs) == 1 and "nope" in msgs[0]


def test_cli(tmp_path, capsys):
    main = _cli()
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(_passport("2026", True)), encoding="utf-8")
    good = tmp_path / "good.json"
    good.write_text(json.dumps(_passport("٢٠٢٦/١٠/٠٥", True)), encoding="utf-8")
    assert main(["verify", str(good)]) == 0
    assert main(["verify", str(bad)]) == 1
    assert main(["run", "x/y"]) == 2
    assert "model-passport-followup.md" in capsys.readouterr().out
    assert "torch" not in sys.modules and "transformers" not in sys.modules
