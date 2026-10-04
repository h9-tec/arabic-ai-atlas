"""The static map site in site/: files present, no third-party scripts, and the pure filter logic."""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"


def _node() -> str | None:
    found = shutil.which("node")
    if found:
        return found
    local = Path.home() / ".local" / "opt" / "node" / "bin" / "node"
    return str(local) if local.exists() else None


def test_site_files_exist_and_are_wired():
    for name in ("index.html", "app.js", "styles.css"):
        assert (SITE / name).is_file(), name
    html = (SITE / "index.html").read_text(encoding="utf-8")
    assert re.search(r'<script[^>]+src="app\.js"', html)
    assert re.search(r'<link[^>]+href="styles\.css"', html)


def test_no_remote_scripts_or_cdns():
    html = (SITE / "index.html").read_text(encoding="utf-8")
    for src in re.findall(r'<script[^>]+src="([^"]+)"', html):
        assert not src.startswith(("http://", "https://", "//")), src
    for href in re.findall(r'<link[^>]+href="(https?://[^"]+)"', html):
        assert href.startswith(("https://fonts.googleapis.com", "https://fonts.gstatic.com")), href
    js = (SITE / "app.js").read_text(encoding="utf-8")
    assert "http://" not in js
    assert not re.search(r"(import|importScripts|src\s*=)\s*\(?[\"']https://", js)
    for url in re.findall(r"https://[^\s\"']+", js):
        assert url.startswith("https://fonts.googleapis.com"), url


NODE_SMOKE = r"""
const atlas = require(process.argv[2]);
const data = require(process.argv[3]);
const E = data.entries;
const out = {
  tts_on_device: atlas.filter(E, {type: "tts", on_device: true}).length,
  whisper: atlas.filter(E, {q: "WHISPER"}).length,
  folds: atlas.fold("\u0625\u0639\u0631\u0627\u0628") === atlas.fold("\u0627\u0639\u0631\u0627\u0628"),
  all: atlas.filter(E, {}).length,
  nc: atlas.licenseClass("cc-by-nc-4.0"), open: atlas.licenseClass("apache-2.0"),
  unknown: atlas.licenseClass("unknown"), prop: atlas.licenseClass("proprietary"),
  fair: atlas.licenseClass("fair-noncommercial-research-license"), falcon: atlas.licenseClass("falcon-llm-license"),
  parsed: atlas.parseHash("#q=whisper%20v3&type=asr,tts&country=EG&on_device=1"),
  roundtrip: atlas.serializeHash(atlas.parseHash("#q=whisper&type=asr&country=EG")),
  rec: atlas.recommendCall({type: "tts", dialect: "egy", on_device: true, license: "open"}),
};
console.log(JSON.stringify(out));
"""


def test_filter_logic_in_node(tmp_path):
    node = _node()
    if not node:
        pytest.skip("node is not installed; skipping the app.js smoke test")
    script = tmp_path / "smoke.js"
    script.write_text(NODE_SMOKE, encoding="utf-8")
    res = subprocess.run(
        [node, str(script), str(SITE / "app.js"), str(ROOT / "dist" / "atlas.json")],
        capture_output=True, text=True, timeout=60, env={**os.environ, "NODE_NO_WARNINGS": "1"},
    )
    assert res.returncode == 0, res.stderr
    out = json.loads(res.stdout)
    count = json.loads((ROOT / "dist" / "atlas.json").read_text(encoding="utf-8"))["count"]
    assert out["tts_on_device"] >= 1
    assert out["whisper"] >= 5
    assert out["all"] == count
    assert out["folds"] is True
    assert (out["nc"], out["open"], out["unknown"], out["prop"]) == ("nc", "open", "unknown", "unknown")
    assert (out["fair"], out["falcon"]) == ("nc", "open")
    assert out["parsed"] == {
        "q": "whisper v3", "type": ["asr", "tts"], "country": ["EG"], "dialect": [], "license": [], "on_device": True,
    }
    assert out["roundtrip"] == "#q=whisper&type=asr&country=EG"
    assert out["rec"] == 'recommend(task="tts", type="tts", dialect="egy", on_device=True, license_filter="open")'
