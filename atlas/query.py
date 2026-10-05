"""Pure query functions over atlas entries (the `entries` list of dist/atlas.json)."""

import json
import re
from pathlib import Path

_NC_RE = re.compile(r"(^|[-_.\s])nc([-_.\s]|$)")


def load_doc(path: Path) -> dict:
    """The whole dist/atlas.json document (entries, lineage, wanted, ...)."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_atlas(path: Path) -> list[dict]:
    return load_doc(path)["entries"]


def license_class(license: str | None) -> str:
    """Return "open", "nc" or "unknown"; mirrors `licenseClass` in site/app.js."""
    lic = str(license or "unknown").lower()
    if _NC_RE.search(lic) or "noncommercial" in lic or "non-commercial" in lic:
        return "nc"
    if lic in ("unknown", "proprietary", ""):
        return "unknown"
    return "open"


def _downloads(e: dict) -> int:
    return (e.get("metrics") or {}).get("downloads") or 0


def _order(e: dict) -> tuple:
    return (-_downloads(e), e.get("name", "").lower())


def search(
    entries: list[dict],
    query: str,
    type: str | None = None,
    country: str | None = None,
    modality: str | None = None,
    limit: int = 10,
) -> list[dict]:
    q = query.lower()
    out = []
    for e in entries:
        if type is not None and e.get("type") != type:
            continue
        if country is not None and e.get("country") != country:
            continue
        if modality is not None and e.get("modality") != modality:
            continue
        hay = [e.get("name", ""), e.get("org", ""), e.get("notes", ""), *e.get("tasks", []), *e.get("tags", [])]
        if any(q in h.lower() for h in hay):
            out.append(e)
    return sorted(out, key=_order)[:limit]


def _fmt_downloads(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M downloads"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K downloads"
    return f"{n} downloads"


MODEL_TYPES = ("llm", "asr", "tts", "ocr", "embedding")


def _tier(e: dict) -> int:
    """Tie-break tier: models 0, datasets/benchmarks/tools/orgs 1, papers 2 (not model picks)."""
    t = e.get("type")
    return 0 if t in MODEL_TYPES else 2 if t == "paper" else 1


def recommend(
    entries: list[dict],
    task: str,
    dialect: str | None = None,
    on_device: bool | None = None,
    license_filter: str | None = None,
    limit: int = 3,
    type: str | None = None,
) -> list[dict]:
    """Rank entries for a task; each result carries `score` and `why`.

    on_device: True keeps only entries marked `on_device: true`; False drops those
    and keeps everything else (most entries leave the field unset); None: no filter.
    type: exact filter on entry type. When None, model types (llm, asr, tts, ocr,
    embedding) rank above datasets, benchmarks, tools and orgs, and papers rank last, at equal score.
    """
    t = task.lower()
    d = dialect.lower() if dialect else None
    lic = license_filter.lower() if license_filter else None
    scored = []
    for e in entries:
        if type is not None and e.get("type") != type:
            continue
        marked = e.get("on_device") is True
        if on_device is True and not marked:
            continue
        if on_device is False and marked:
            continue
        elic = str(e.get("license", "")).lower()
        if lic == "open":
            if elic in {"proprietary", "unknown"}:
                continue
        elif lic is not None and elic != lic:
            continue
        score, why = 0, []
        if t in [x.lower() for x in e.get("tasks", [])]:
            score += 3
            why.append(f"task match: {task}")
        if d and d in [x.lower() for x in e.get("dialects", [])]:
            score += 2
            why.append(f"dialect match: {dialect}")
        if t in e.get("notes", "").lower():
            score += 1
            why.append(f"mentioned in notes: {task}")
        if score == 0:
            continue
        if _downloads(e):
            why.append(_fmt_downloads(_downloads(e)))
        scored.append({**e, "score": score, "why": "; ".join(why)})
    scored.sort(key=lambda r: (-r["score"], _tier(r), *_order(r)))
    return scored[:limit]


def get(entries: list[dict], id: str) -> dict | None:
    return next((e for e in entries if e.get("id") == id), None)


def _walk(start: str, step: dict[str, list[str]]) -> list[str]:
    """Breadth-first from start, each level sorted, never revisiting a node or start."""
    seen, out, frontier = {start}, [], [start]
    while frontier:
        level = sorted({n for f in frontier for n in step.get(f, []) if n not in seen})
        seen.update(level)
        out += level
        frontier = level
    return out


def lineage(doc: dict, id: str) -> dict:
    """Ancestors (nearest first) and descendants (breadth-first) of an atlas or external id.

    An id that is neither an entry id nor a lineage node is retried as its canonical HF id
    (lowercased, URL prefix stripped, renamed org aliased), then as the atlas entry whose HF
    link has that canonical id. A resolved lookup echoes the original as `query`.
    """
    from atlas.lineage import _atlas_index, canonical, root_family

    lin = doc.get("lineage") or {}
    edges = lin.get("edges") or []
    root_of = lin.get("root_of") or {}
    entries = doc.get("entries") or []
    entry_ids = {e.get("id") for e in entries}
    nodes = entry_ids | set(root_of) | {n for edge in edges for n in edge}
    query = id
    if id not in nodes:
        c = canonical(id)
        id = c if c in nodes else _atlas_index([e for e in entries if e.get("id")]).get(c, id)
    if id not in nodes:
        return {"error": "unknown id", "id": query}
    up: dict[str, list[str]] = {}
    down: dict[str, list[str]] = {}
    for parent, child in edges:
        up.setdefault(child, []).append(parent)
        down.setdefault(parent, []).append(child)
    if id in root_of:
        root = root_of[id]
    elif id in entry_ids or id not in down:
        root = None  # atlas entry without a recorded base
    else:
        root = root_family(id)  # external base id
    out = {"id": id, "root": root, "ancestors": _walk(id, up), "descendants": _walk(id, down)}
    return out if id == query else {**out, "query": query}
