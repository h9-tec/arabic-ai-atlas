"""Pure query functions over atlas entries (the `entries` list of dist/atlas.json)."""

import json
from pathlib import Path


def load_atlas(path: Path) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))["entries"]


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
    embedding) rank above datasets, benchmarks, tools and orgs at equal score.
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
    scored.sort(key=lambda r: (-r["score"], r.get("type") not in MODEL_TYPES, *_order(r)))
    return scored[:limit]


def get(entries: list[dict], id: str) -> dict | None:
    return next((e for e in entries if e.get("id") == id), None)
