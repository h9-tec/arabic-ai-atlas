"""Machine-readable outputs: dist/atlas.json and dist/llms.txt."""

LINK_ORDER = ("hf", "github", "paper", "website")
REPO_URL = "https://github.com/h9-tec/arabic-ai-atlas"
ATLAS_JSON_URL = "https://raw.githubusercontent.com/h9-tec/arabic-ai-atlas/main/dist/atlas.json"
MAX_PER_SECTION = 25
SECTIONS = (
    ("Models", ("llm", "asr", "tts", "ocr", "embedding")),
    ("Datasets", ("dataset",)),
    ("Tools & Benchmarks", ("tool", "benchmark")),
    ("Papers", ("paper",)),
    ("Organizations", ("org",)),
    ("Agent Skills", ("agent-skill",)),
)


def _downloads(entry: dict) -> int:
    return (entry.get("metrics") or {}).get("downloads") or 0


def _sort_key(entry: dict):
    if entry.get("type") == "paper":  # literature: newest, then most cited
        return (-(entry.get("year") or 0), -(entry.get("citations") or 0), entry["name"].lower())
    return (-_downloads(entry), 0, entry["name"].lower())


def build_atlas_json(merged: list[dict], generated_at: str, extras: dict | None = None) -> dict:
    entries = [{k: v for k, v in e.items() if k != "_file"} for e in sorted(merged, key=_sort_key)]
    return {"generated_at": generated_at, "count": len(entries), "entries": entries, **(extras or {})}


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
    lines += [
        "",
        "## Optional",
        "",
        f"- [Full dataset (JSON)]({ATLAS_JSON_URL}): every entry with metadata and metrics",
        f"- [README]({REPO_URL}#readme): the human-readable atlas with every table",
    ]
    return "\n".join(lines) + "\n"
