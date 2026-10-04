"""Render README.md from merged entries and templates/README.tmpl.md."""
from pathlib import Path
from urllib.parse import urlparse

import yaml

FLAGS = {
    "SA": "🇸🇦", "AE": "🇦🇪", "EG": "🇪🇬", "QA": "🇶🇦", "MA": "🇲🇦", "JO": "🇯🇴",
    "TN": "🇹🇳", "LB": "🇱🇧", "KW": "🇰🇼", "OM": "🇴🇲", "BH": "🇧🇭", "INTL": "🌍",
}
DASH = "—"

_MEDIA = ("llm", "asr", "tts", "ocr", "embedding", "dataset")
COLUMNS = {
    "llm": ["Name", "Org", "Country", "Size", "License", "⬇ Downloads", "Updated", "Links"],
    "asr": ["Name", "Org", "Country", "License", "⬇ Downloads", "Updated", "Links"],
    "tts": ["Name", "Org", "Country", "License", "⬇ Downloads", "Updated", "Links"],
    "ocr": ["Name", "Org", "Country", "License", "⬇ Downloads", "Updated", "Links"],
    "embedding": ["Name", "Org", "Country", "License", "⬇ Downloads", "Updated", "Links"],
    "dataset": ["Name", "Org", "Country", "Size", "License", "⬇", "Updated", "Links"],
    "tool": ["Name", "Org", "Country", "License", "Links", "Notes"],
    "benchmark": ["Name", "Org", "Country", "License", "Links", "Notes"],
    "org": ["Name", "Country", "Focus", "Links"],
    "agent-skill": ["Name", "Org", "Notes", "Links"],
}


def fmt_downloads(n: int | None) -> str:
    if n is None:
        return DASH
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n // 1_000}K"
    return str(n)


def esc(value) -> str:
    if value is None or value == "":
        return DASH
    return " ".join(str(value).split()).replace("|", "\\|")


def hf_label(url: str) -> str:
    segs = [x for x in urlparse(url).path.split("/") if x]
    prefixes = {"datasets": "Dataset", "papers": "Paper", "spaces": "Space", "collections": "Collection"}
    if segs and segs[0] in prefixes:
        return prefixes[segs[0]]
    return "Model" if len(segs) == 2 else "Hub"


def badges(entry: dict) -> str:
    links = entry.get("links") or {}
    out = []
    if links.get("hf"):
        label = hf_label(links["hf"])
        out.append(f"[![HF](https://img.shields.io/badge/-{label}-FFD21E?logo=huggingface&logoColor=black)]({links['hf']})")
    if links.get("github"):
        out.append(f"[![GitHub](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white)]({links['github']})")
    if links.get("paper"):
        out.append(f"[![Paper](https://img.shields.io/badge/-Paper-B31B1B?logo=arxiv&logoColor=white)]({links['paper']})")
    if links.get("website"):
        out.append(f"[![Web](https://img.shields.io/badge/-Website-4285F4?logo=googlechrome&logoColor=white)]({links['website']})")
    return " ".join(out) if out else DASH


def _country(entry: dict) -> str:
    code = entry.get("country") or ""
    return f"{FLAGS.get(code, '')} {code}".strip() or DASH


def _cell(entry: dict, col: str) -> str:
    m = entry.get("metrics") or {}
    if col == "Name":
        return esc(entry.get("name"))
    if col == "Org":
        return esc(entry.get("org"))
    if col == "Country":
        return _country(entry)
    if col == "Size":
        return esc(entry.get("size"))
    if col == "License":
        return esc(entry.get("license"))
    if col in ("⬇ Downloads", "⬇"):
        return fmt_downloads(m.get("downloads"))
    if col == "Updated":
        return esc(m.get("lastModified"))
    if col == "Links":
        return badges(entry)
    return esc(entry.get("notes"))  # Notes / Focus


def render_table(entries: list[dict], type_: str) -> str:
    rows = [e for e in entries if e.get("type") == type_]
    rows.sort(key=lambda e: (-((e.get("metrics") or {}).get("downloads") or 0), str(e.get("name", "")).lower()))
    cols = COLUMNS[type_]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(" --- " for _ in cols) + "|"]
    for e in rows:
        lines.append("| " + " | ".join(_cell(e, c) for c in cols) + " |")
    return "\n".join(lines)


def render_shipped(skills: list[dict]) -> str:
    if not skills:
        return "_No skills shipped yet._"
    lines = ["| Skill | What it does | Install |", "| --- | --- | --- |"]
    for s in skills:
        lines.append(f"| {esc(s['name'])} | {esc(s['description'])} | `{s['path']}` |")
    return "\n".join(lines)


def load_shipped_skills(skills_dir: Path) -> list[dict]:
    skills_dir = Path(skills_dir)
    if not skills_dir.is_dir():
        return []
    out = []
    for md in sorted(skills_dir.glob("*/SKILL.md")):
        parts = md.read_text(encoding="utf-8").split("---")
        if len(parts) < 3 or parts[0].strip():
            continue
        meta = yaml.safe_load(parts[1]) or {}
        out.append({
            "name": str(meta.get("name", md.parent.name)),
            "description": " ".join(str(meta.get("description", "")).split()),
            "path": f"skills/{md.parent.name}",
        })
    return sorted(out, key=lambda s: s["name"])


def render_readme(merged: list[dict], template: str, generated_at: str, shipped_skills: list[dict]) -> str:
    out = template
    for t in COLUMNS:
        out = out.replace("{{TABLE:%s}}" % t, render_table(merged, t))
    out = out.replace("{{SHIPPED_SKILLS}}", render_shipped(shipped_skills))
    out = out.replace("{{COUNT}}", str(len(merged))).replace("{{DATE_BADGE}}", generated_at.replace("-", "--")).replace("{{DATE}}", generated_at)
    return out
