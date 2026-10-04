"""Hugging Face metrics enrichment with an on-disk-friendly cache dict."""

import json
import urllib.request
from collections.abc import Callable
from urllib.parse import urlsplit

_HF_HOSTS = {"huggingface.co", "www.huggingface.co"}
_EXPAND = "?expand[]=downloads&expand[]=likes&expand[]=lastModified&expand[]=cardData"
FETCHED_AT = "fetched_at"  # single top-level cache key; per-entry dates churned every nightly diff
METRIC_KEYS = ("downloads", "likes", "lastModified")
_VAGUE_LICENSES = {"other", "unknown", "custom", "cc", "gpl"}  # no usable terms or version: stay unknown
_NOT_REPOS = {"spaces", "collections", "papers", "docs", "blog", "organizations"}  # no models API


def hf_id_from_url(url: str) -> str | None:
    """Return 'owner/name' or 'datasets/owner/name' for a HF URL, else None."""
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https") or parts.hostname not in _HF_HOSTS:
        return None
    segs = [s for s in parts.path.split("/") if s]
    if segs and segs[0] in _NOT_REPOS:
        return None
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


def card_license(data: dict) -> str | None:
    """Lowercased license from a HF API response's cardData, or None.

    `other` defers to `license_name` when the card gives one; lists keep the first item;
    vague values (custom, cc, gpl without a version) count as no license.
    """
    card = data.get("cardData") or {}
    lic = card.get("license")
    if isinstance(lic, list):
        lic = lic[0] if lic else None
    if isinstance(lic, str) and lic.strip().lower() == "other":
        lic = card.get("license_name")
    if not isinstance(lic, str) or lic.strip().lower() in _VAGUE_LICENSES | {""}:
        return None
    return lic.strip().lower()


def fetch_hf_metrics(
    hf_ids: list[str],
    cache: dict,
    fetch: Callable[[str], dict] = _default_fetch,
    now: str = "",
) -> tuple[dict, list[str]]:
    """Fetch metrics sequentially; on failure keep any old entry and warn.

    The cache maps hf_id -> {downloads, likes, lastModified[, license]} plus one
    top-level `fetched_at` date.
    """
    new = {k: ({x: y for x, y in v.items() if x != "fetched"} if isinstance(v, dict) else v)
           for k, v in cache.items()}  # drop the legacy per-entry `fetched` stamp
    warnings: list[str] = []
    for hf_id in hf_ids:
        try:
            data = fetch(hf_id)
            modified = data.get("lastModified")
            row = {
                "downloads": data.get("downloads") or 0,
                "likes": data.get("likes") or 0,
                "lastModified": modified[:10] if modified else None,
            }
            lic = card_license(data)
            if lic:
                row["license"] = lic
            new[hf_id] = row
        except Exception as exc:  # noqa: BLE001 - never raise from enrichment
            warnings.append(f"{hf_id}: {type(exc).__name__}: {exc}")
    new[FETCHED_AT] = now
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


def _cached(entry: dict, cache: dict) -> dict | None:
    url = entry.get("links", {}).get("hf")
    hf_id = hf_id_from_url(url) if url else None
    row = cache.get(hf_id) if hf_id else None
    return row if isinstance(row, dict) else None


def merge_metrics(entries: list[dict], cache: dict) -> list[dict]:
    """Return copies of entries with a `metrics` key (downloads/likes/lastModified, or None)."""
    merged = []
    for entry in entries:
        row = _cached(entry, cache)
        metrics = {k: row[k] for k in METRIC_KEYS if k in row} if row else None
        merged.append({**entry, "metrics": metrics or None})
    return merged


def apply_cached_licenses(entries: list[dict], cache: dict) -> list[dict]:
    """Return copies of entries whose `unknown` license is filled from the HF card cache.

    A license set in the YAML always wins; only `unknown` (or a missing license) is replaced.
    """
    out = []
    for entry in entries:
        row = _cached(entry, cache)
        lic = row.get("license") if row else None
        if lic and str(entry.get("license", "unknown")).lower() == "unknown":
            entry = {**entry, "license": lic}
        out.append(entry)
    return out
