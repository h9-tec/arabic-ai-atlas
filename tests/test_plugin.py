"""Cheap structural checks for the Claude Code plugin packaging."""

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_plugin_manifest():
    m = _load(".claude-plugin/plugin.json")
    assert m["name"] == "arabic-ai-atlas"
    assert m["version"] == "0.2.0"
    assert m["description"]
    assert m["author"]["name"] == "Hesham Haroon"


def test_marketplace_manifest():
    m = _load(".claude-plugin/marketplace.json")
    assert m["name"] == "arabic-ai-atlas"
    assert m["owner"]["name"] == "Hesham Haroon"
    assert len(m["plugins"]) == 1
    p = m["plugins"][0]
    assert p["name"] == "arabic-ai-atlas"
    assert p["source"] == "./"
    assert p["category"] == "development"
    assert p["description"]


def test_skills_frontmatter():
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    assert skills, "no skills shipped"
    for path in skills:
        text = path.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n", text, re.S)
        assert m, f"{path} has no frontmatter"
        fm = dict(
            line.split(":", 1) for line in m.group(1).splitlines() if ":" in line
        )
        name = fm["name"].strip()
        desc = fm["description"].strip()
        assert name and name == path.parent.name
        assert desc.startswith("Use when")
        assert len(desc) <= 250


def test_mcp_json_names_server():
    cfg = _load(".mcp.json")
    assert "arabic-ai-atlas" in cfg["mcpServers"]
    srv = cfg["mcpServers"]["arabic-ai-atlas"]
    assert srv["command"] == "uv"
    assert srv["args"] == ["run", "--frozen", "--no-dev", "--directory", "${CLAUDE_PLUGIN_ROOT}", "python", "mcp/server.py"]


def test_readme_template_states_uv_requirement_and_snippet():
    tmpl = (ROOT / "templates" / "README.tmpl.md").read_text(encoding="utf-8")
    assert "Requires [uv](https://docs.astral.sh/uv/) on PATH." in tmpl
    assert '"run", "--frozen", "--no-dev", "--directory", "/path/to/arabic-ai-atlas"' in tmpl


def test_pyproject_version_matches_plugin():
    py = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert py["project"]["version"] == _load(".claude-plugin/plugin.json")["version"]
