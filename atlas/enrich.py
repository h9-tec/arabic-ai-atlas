"""Hugging Face metrics enrichment with an on-disk-friendly cache dict."""

import json
import urllib.request
from collections.abc import Callable
from urllib.parse import urlsplit

_HF_HOSTS = {"huggingface.co", "www.huggingface.co"}
_EXPAND = "?expand[]=downloads&expand[]=likes&expand[]=lastModified"


def hf_id_from_url(url: str) -> str | None:
    """Return 'owner/name' or 'datasets/owner/name' for a HF URL, else None."""
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https") or parts.hostname not in _HF_HOSTS:
        return None
    segs = [s for s in parts.path.split("/") if s]
    prefix = []
    if segs and segs[0] == "datasets":
        prefix = ["datasets"]
        segs = segs[1:]
    if len(segs) < 2:
        return None
    return "/".join(prefix + segs[:2])


def _default_fetch(hf_id: str) -> dict:
    kind, _, rest = hf_id.partition("/") if hf_id.startswith("datasets/") else ("models", "", hf_id)
    req = urllib.request.Request(
        f"https://huggingface.co/api/{kind}/{rest}{_EXPAND}",
        headers={"User-Agent": "arabic-ai-atlas"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def fetch_hf_metrics(
    hf_ids: list[str],
    cache: dict,
    fetch: Callable[[str], dict] = _default_fetch,
    now: str = "",
) -> tuple[dict, list[str]]:
    """Fetch metrics sequentially; on failure keep any old entry and warn."""
    new = dict(cache)
    warnings: list[str] = []
    for hf_id in hf_ids:
        try:
            data = fetch(hf_id)
            modified = data.get("lastModified")
            new[hf_id] = {
                "downloads": data.get("downloads") or 0,
                "likes": data.get("likes") or 0,
                "lastModified": modified[:10] if modified else None,
                "fetched": now,
            }
        except Exception as exc:  # noqa: BLE001 - never raise from enrichment
            warnings.append(f"{hf_id}: {type(exc).__name__}: {exc}")
    return new, warnings


def build_hf_ids(entries: list[dict]) -> list[str]:
    """Unique HF ids across entries, in first-seen order."""
    seen: dict[str, None] = {}
    for entry in entries:
        url = entry.get("links", {}).get("hf")
        hf_id = hf_id_from_url(url) if url else None
        if hf_id:
            seen.setdefault(hf_id)
    return list(seen)


def merge_metrics(entries: list[dict], cache: dict) -> list[dict]:
    """Return copies of entries with a `metrics` key (cache dict or None)."""
    merged = []
    for entry in entries:
        url = entry.get("links", {}).get("hf")
        hf_id = hf_id_from_url(url) if url else None
        metrics = cache.get(hf_id) if hf_id else None
        merged.append({**entry, "metrics": dict(metrics) if metrics else None})
    return merged
