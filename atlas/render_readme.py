"""Render README.md from merged entries and templates/README.tmpl.md."""
from pathlib import Path
from urllib.parse import urlparse

import yaml

FLAGS = {
    "SA": "🇸🇦", "AE": "🇦🇪", "EG": "🇪🇬", "QA": "🇶🇦", "MA": "🇲🇦", "JO": "🇯🇴",
    "TN": "🇹🇳", "LB": "🇱🇧", "KW": "🇰🇼", "OM": "🇴🇲", "BH": "🇧🇭",
    "DZ": "🇩🇿", "LY": "🇱🇾", "SD": "🇸🇩", "IQ": "🇮🇶", "SY": "🇸🇾", "YE": "🇾🇪", "PS": "🇵🇸", "MR": "🇲🇷",
    "SO": "🇸🇴", "DJ": "🇩🇯", "KM": "🇰🇲", "INTL": "🌍",
}
DASH = "—"
SITE = "https://h9-tec.github.io/arabic-ai-atlas/"
README_CAP = 20

COUNTRY_NAMES = {
    "SA": "Saudi Arabia", "AE": "United Arab Emirates", "EG": "Egypt", "QA": "Qatar", "MA": "Morocco",
    "JO": "Jordan", "TN": "Tunisia", "LB": "Lebanon", "KW": "Kuwait", "OM": "Oman", "BH": "Bahrain",
    "DZ": "Algeria", "LY": "Libya", "SD": "Sudan", "IQ": "Iraq", "SY": "Syria", "YE": "Yemen",
    "PS": "Palestine", "MR": "Mauritania", "SO": "Somalia", "DJ": "Djibouti", "KM": "Comoros",
    "INTL": "International",
}
TYPE_TITLES = {
    "llm": "Large Language Models", "asr": "Speech Recognition", "tts": "Text-to-Speech", "ocr": "OCR",
    "embedding": "Embeddings", "dataset": "Datasets", "tool": "Tools", "benchmark": "Benchmarks",
    "paper": "Papers", "org": "Organizations", "agent-skill": "Arabic Agent Skills",
}
# (column header, entry type) for the country summary table
COUNTRY_COLS = [("LLM", "llm"), ("ASR", "asr"), ("TTS", "tts"), ("OCR", "ocr"), ("Embedding", "embedding"),
                ("Datasets", "dataset"), ("Tools", "tool"), ("Benchmarks", "benchmark"), ("Papers", "paper"), ("Orgs", "org")]

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
    "paper": ["Title", "Venue", "Year", "Topic", "Links"],
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
    if col in ("Name", "Title"):
        return esc(entry.get("name"))
    if col == "Venue":
        return esc(entry.get("venue"))
    if col == "Year":
        return esc(entry.get("year"))
    if col == "Topic":
        return esc(", ".join(entry.get("tasks") or []))
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


def sorted_rows(entries: list[dict], type_: str) -> list[dict]:
    rows = [e for e in entries if e.get("type") == type_]
    if type_ == "paper":
        rows.sort(key=lambda e: (-(e.get("year") or 0), -(e.get("citations") or 0), str(e.get("name", "")).lower()))
    else:
        rows.sort(key=lambda e: (-((e.get("metrics") or {}).get("downloads") or 0), str(e.get("name", "")).lower()))
    return rows


def render_table(entries: list[dict], type_: str, limit: int | None = None) -> str:
    rows = sorted_rows(entries, type_)
    if limit is not None:
        rows = rows[:limit]
    cols = COLUMNS[type_]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(" --- " for _ in cols) + "|"]
    for e in rows:
        lines.append("| " + " | ".join(_cell(e, c) for c in cols) + " |")
    return "\n".join(lines)


def render_section_table(entries: list[dict], type_: str, cap: int = README_CAP) -> str:
    """Top `cap` rows for the README, plus a pointer to the full table when rows were cut."""
    total = sum(1 for e in entries if e.get("type") == type_)
    table = render_table(entries, type_, cap)
    if total <= cap:
        return table
    return (f"{table}\n\n_Showing {cap} of {total} · [see all {total} on the interactive map]({SITE}#type={type_})"
            f" · [full table](docs/tables/{type_}.md)_")


def render_country_table(entries: list[dict]) -> str:
    counts: dict[str, dict[str, int]] = {}
    for e in entries:
        c = e.get("country") or ""
        counts.setdefault(c, {})
        counts[c][e.get("type")] = counts[c].get(e.get("type"), 0) + 1
    order = sorted((c for c in counts if c), key=lambda c: (-sum(counts[c].values()), COUNTRY_NAMES.get(c, c)))
    head = ["Country", "Entries"] + [h for h, _ in COUNTRY_COLS]
    lines = ["| " + " | ".join(head) + " |", "|" + "|".join(" --- " for _ in head) + "|"]
    for c in order:
        name = f"{FLAGS.get(c, '')} [{COUNTRY_NAMES.get(c, c)}]({SITE}#country={c})".strip()
        cells = [name, str(sum(counts[c].values()))] + [str(counts[c].get(t, 0)) for _, t in COUNTRY_COLS]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_tables(merged: list[dict], generated_at: str) -> dict[str, str]:
    """Full per-type tables under docs/tables/, plus an index. Keyed by repo-relative path."""
    out = {}
    index = ["# Full tables", "",
             f"Every entry of each type. The [README](../../README.md) shows only the top {README_CAP} per type; "
             f"the [interactive map]({SITE}) has search and filters.", "",
             "| Type | Entries |", "| --- | --- |"]
    for t in COLUMNS:
        n = sum(1 for e in merged if e.get("type") == t)
        title = TYPE_TITLES[t]
        index.append(f"| [{title}]({t}.md) | {n} |")
        out[f"docs/tables/{t}.md"] = (
            f"# {title} ({n})\n\n[← README](../../README.md) · [interactive map]({SITE}#type={t})\n\n"
            f"{render_table(merged, t)}\n\n---\n\n_Generated {generated_at}. Do not edit by hand._\n")
    index += ["", "---", "", f"_Generated {generated_at}. Do not edit by hand._"]
    out["docs/tables/README.md"] = "\n".join(index) + "\n"
    return out


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
        out = out.replace("{{TABLE:%s}}" % t, render_section_table(merged, t))
        out = out.replace("{{COUNT:%s}}" % t, str(sum(1 for e in merged if e.get("type") == t)))
    out = out.replace("{{COUNTRY_TABLE}}", render_country_table(merged))
    out = out.replace("{{SHIPPED_SKILLS}}", render_shipped(shipped_skills))
    out = out.replace("{{COUNT}}", str(len(merged))).replace("{{DATE_BADGE}}", generated_at.replace("-", "--")).replace("{{DATE}}", generated_at)
    return out
