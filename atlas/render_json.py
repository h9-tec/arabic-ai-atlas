"""Machine-readable outputs: dist/atlas.json and dist/llms.txt."""

LINK_ORDER = ("hf", "github", "paper", "website")
MAX_PER_SECTION = 25
SECTIONS = (
    ("Models", ("llm", "asr", "tts", "ocr", "embedding")),
    ("Datasets", ("dataset",)),
    ("Tools & Benchmarks", ("tool", "benchmark")),
    ("Organizations", ("org",)),
    ("Agent Skills", ("agent-skill",)),
)


def _downloads(entry: dict) -> int:
    return (entry.get("metrics") or {}).get("downloads") or 0


def _sort_key(entry: dict):
    return (-_downloads(entry), entry["name"].lower())


def build_atlas_json(merged: list[dict], generated_at: str) -> dict:
    entries = [{k: v for k, v in e.items() if k != "_file"} for e in sorted(merged, key=_sort_key)]
    return {"generated_at": generated_at, "count": len(entries), "entries": entries}


def _primary_link(entry: dict) -> str | None:
    links = entry.get("links") or {}
    for key in LINK_ORDER:
        if links.get(key):
            return links[key]
    return None


def build_llms_txt(merged: list[dict], generated_at: str) -> str:
    lines = [
        "# Arabic AI Atlas",
        "",
        "> The Arabic AI ecosystem as a map, a list, and a skill your agent can install. "
        f"{len(merged)} entries, generated {generated_at}.",
    ]
    for title, types in SECTIONS:
        members = sorted((e for e in merged if e.get("type") in types), key=_sort_key)[:MAX_PER_SECTION]
        if not members:
            continue
        lines += ["", f"## {title}", ""]
        for e in members:
            link = _primary_link(e)
            head = f"[{e['name']}]({link})" if link else e["name"]
            notes = (e.get("notes") or "").strip()
            lines.append(f"- {head}: {notes}" if notes else f"- {head}")
    lines += ["", "## Optional", "", "- [Full dataset (JSON)](dist/atlas.json): every entry with metadata and metrics"]
    return "\n".join(lines) + "\n"
