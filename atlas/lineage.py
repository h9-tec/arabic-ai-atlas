"""Model lineage: resolve base_model ids to atlas entries and group models into root families."""

import re

from atlas.enrich import hf_id_from_url, normalize_base

# (root_id, regex over the lowercased external base id, English label, Arabic label), matched in order.
ROOTS: list[tuple[str, str, str, str]] = [
    ("whisper", r"whisper", "Whisper", "ويسبر"),
    ("mms", r"(^|[/_-])mms([/_-]|$)", "MMS", "إم إم إس"),
    ("xlsr", r"xls-?r", "XLS-R", "إكس إل إس-آر"),
    ("wav2vec", r"wav2vec", "wav2vec", "واف تو فيك"),
    ("electra", r"electra", "ELECTRA", "إلكترا"),
    ("bert", r"bert|roberta", "BERT", "بيرت"),
    ("t5", r"(^|[/_-])(m|by|ara)?t5(v[0-9]+)?([/_.-]|$)", "T5", "تي 5"),
    ("llama", r"llama", "Llama", "لاما"),
    ("qwen", r"qwen", "Qwen", "كوين"),
    ("gemma", r"gemma", "Gemma", "جيما"),
    ("mistral", r"mistral|mixtral", "Mistral", "ميسترال"),
    ("falcon", r"falcon", "Falcon", "فالكون"),
    ("bloom", r"bloom", "BLOOM", "بلوم"),
    ("phi", r"(^|[/_-])phi-?[0-9]", "Phi", "فاي"),
    ("deepseek", r"deepseek", "DeepSeek", "ديب سيك"),
    ("xtts", r"xtts", "XTTS", "XTTS"),
    ("f5", r"f5-?tts|f5tts", "F5-TTS", "F5-TTS"),
    ("bge", r"(^|[/_-])bge", "BGE", "BGE"),
    ("e5", r"(^|[/_-])(multilingual-)?e5", "E5", "E5"),
    ("nllb", r"nllb", "NLLB", "NLLB"),
    ("cohere", r"command-?r|c4ai|cohere|(^|[/_-])aya([/_-]|$)", "Cohere", "Cohere"),
    ("seamless", r"seamless|m4t", "SeamlessM4T", "SeamlessM4T"),
    ("from-scratch", r"^from-scratch$", "From scratch", "من الصفر"),
]
OTHER = ("other", "", "Other", "أخرى")
_COMPILED = [(rid, re.compile(rx)) for rid, rx, _, _ in ROOTS]
_LABELS = {rid: (en, ar) for rid, _, en, ar in [*ROOTS, OTHER]}

# Hugging Face org renames: old namespace -> current one, applied to both sides before matching.
ORG_ALIASES: dict[str, str] = {
    "allam-ai": "humain-ai",
    "inception-mbzuai": "inception42",
    "inceptionai": "inception42",
    "core42": "inception42",
}


def canonical(value: str) -> str:
    """normalize_base, then rewrite a renamed `org/` prefix (also after `datasets/`)."""
    v = normalize_base(value)
    segs = v.split("/")
    i = 1 if segs[0] == "datasets" and len(segs) > 2 else 0
    if len(segs) > i + 1 and segs[i] in ORG_ALIASES:
        segs[i] = ORG_ALIASES[segs[i]]
    return "/".join(segs)


def root_family(base_id: str) -> str:
    v = base_id.lower()
    return next((rid for rid, rx in _COMPILED if rx.search(v)), OTHER[0])


def _atlas_index(merged: list[dict]) -> dict[str, str]:
    """Map atlas ids and canonical HF ids to atlas ids.

    When two entries share a canonical HF id (one under an old org name), the entry whose
    link already uses the current name wins, then the smaller id.
    """
    cands: dict[str, list[tuple[int, str]]] = {}
    for e in merged:
        hf = hf_id_from_url((e.get("links") or {}).get("hf") or "")
        if hf:
            raw = hf.lower()
            cands.setdefault(canonical(raw), []).append((int(canonical(raw) != raw), e["id"]))
    index = {key: min(c)[1] for key, c in cands.items()}
    index.update({e["id"]: e["id"] for e in merged})  # an exact atlas id beats an HF id
    return index


def _parents(merged: list[dict]) -> dict[str, list[str]]:
    index = _atlas_index(merged)
    out: dict[str, list[str]] = {}
    for e in sorted(merged, key=lambda x: x["id"]):
        bases = e.get("base_model") or []
        if not bases:
            continue
        ps: list[str] = []
        for b in bases:
            n = normalize_base(b)
            p = index.get(n) or index.get(canonical(n)) or canonical(n)
            if p and p != e["id"] and p not in ps:
                ps.append(p)
        out[e["id"]] = ps
    return out


def _terminal(eid: str, hf_of: dict[str, str]) -> str:
    """Family of an atlas entry with no recorded base: from its HF id, else its atlas id."""
    return root_family(hf_of.get(eid) or eid)


def _root(eid: str, parents: dict[str, list[str]], atlas_ids: set[str], hf_of: dict[str, str]) -> str:
    """Breadth-first up the parents (base_model order) to the first id with no parents.

    That is an external id, or an atlas entry with no base_model (classified by its HF id).
    An entry outside `parents`, or whose only base is itself (no parents left), is itself such a
    terminal; an atlas-only cycle gives other.
    """
    if not parents.get(eid):
        return _terminal(eid, hf_of)
    seen, frontier = {eid}, [eid]
    while frontier:
        nxt = []
        for node in frontier:
            for p in parents[node]:
                if p not in atlas_ids:
                    return root_family(p)
                if not parents.get(p):
                    return _terminal(p, hf_of)
                if p not in seen:
                    seen.add(p)
                    nxt.append(p)
        frontier = nxt
    return OTHER[0]


def build_lineage(merged: list[dict]) -> dict:
    """{"roots": [{id, label, label_ar, count}], "edges": [[parent, child]], "root_of": {entry_id: root_id}}.

    Entries with a base_model, and atlas entries named as someone's base, get a root. A walk that
    ends at an atlas entry with no base_model classifies that entry by root_family of its canonical
    HF id (else its atlas id), e.g. a fine-tune of an atlas AraBERT entry roots as bert. Parents are atlas ids when the base resolves to
    an entry (by id or by its HF link, org renames aliased), else the canonical lowercase HF id.
    """
    atlas_ids = {e["id"] for e in merged}
    hf_of = {e["id"]: canonical(h) for e in merged if (h := hf_id_from_url((e.get("links") or {}).get("hf") or ""))}
    parents = _parents(merged)
    members = set(parents) | {p for ps in parents.values() for p in ps if p in atlas_ids}
    root_of = {eid: _root(eid, parents, atlas_ids, hf_of) for eid in sorted(members)}
    counts: dict[str, int] = {}
    for r in root_of.values():
        counts[r] = counts.get(r, 0) + 1
    roots = [
        {"id": r, "label": _LABELS[r][0], "label_ar": _LABELS[r][1], "count": n}
        for r, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    edges = sorted([p, c] for c, ps in parents.items() for p in ps)
    return {"roots": roots, "edges": edges, "root_of": root_of}
