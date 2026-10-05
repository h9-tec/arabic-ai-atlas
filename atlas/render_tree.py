"""Render the family tree (assets/tree.svg) and its README block from the lineage doc.

One band per base family: the root card on the left, curved branches to that family's atlas
models flowing on the right. Deeper lineage (fine-tune of a fine-tune) is the live site's job.
Stdlib only and deterministic: no randomness, no clock, everything sorted.
"""
import math

from atlas.render_geo import _DARK, _LIGHT, TYPE_LABELS
from atlas.render_map import COLORS, FONT_PX, MIN_W, NODE_H, RADIUS, _attr, _n, _primary_link, node_width, \
    text_width, truncate
from atlas.render_readme import SITE, esc, fmt_downloads

MAX_PER_ROOT = 12
WIDTH = 1600
PAD = 24
HEAD_H = 96  # title strip
ROOT_W, ROOT_H = 268, 36
FLOW_X = PAD + ROOT_W + 64  # where model rows start
FLOW_W = WIDTH - PAD - FLOW_X
GAP_X, GAP_Y = 6, 7
BAND_PAD = 7
TREE_URL = f"{SITE}#view=tree"
FONT = '"IBM Plex Sans Arabic", -apple-system, "Segoe UI", Tahoma, Roboto, Helvetica, Arial, sans-serif'
MODEL_TYPES = ("llm", "asr", "tts", "ocr", "embedding")
TYPE_ORDER = ("llm", "asr", "tts", "ocr", "embedding", "tool", "benchmark", "dataset")

_STYLE = f"""
svg {{ {_LIGHT} }}
@media (prefers-color-scheme: dark) {{
  svg {{ {_DARK} }}
}}
text {{ font-family: {FONT}; fill: var(--ink); }}
.bg {{ fill: var(--bg); }}
.title {{ font-size: 32px; font-weight: 700; }}
.sub {{ font-size: 17px; fill: var(--muted); }}
.lg-h {{ font-size: 16px; font-weight: 600; }}
.lg {{ font-size: 15px; fill: var(--muted); }}
.rule {{ stroke: var(--rule); stroke-width: 1; }}
.root {{ fill: var(--sheet); stroke: var(--rule-strong); stroke-width: 1.2; }}
.root.scratch {{ stroke-dasharray: 5 4; }}
.r-en {{ font-size: 16px; font-weight: 700; }}
.r-n {{ font-size: 14px; fill: var(--muted); }}
.r-ar {{ font-size: 19px; font-weight: 700; }}
.branch {{ fill: none; stroke: var(--rule-strong); stroke-width: 1.4; }}
.knot {{ fill: var(--rule-strong); }}
.n {{ stroke: var(--bubble-stroke); stroke-width: .8; }}
.nl {{ font-size: {FONT_PX}px; font-weight: 600; fill: #FFFFFF; pointer-events: none; }}
a:hover .n, a:hover .root {{ opacity: .85; }}
.footer {{ font-size: 15px; fill: var(--muted); }}
"""


def _downloads(e: dict) -> int | None:
    return (e.get("metrics") or {}).get("downloads")


def _sort_key(e: dict):
    return (-(_downloads(e) or 0), e["name"].lower(), e["id"])


def _ordered_roots(lineage: dict) -> list[dict]:
    """lineage["roots"] order, except the catch-all `other` always comes last."""
    roots = lineage.get("roots") or []
    return [r for r in roots if r["id"] != "other"] + [r for r in roots if r["id"] == "other"]


def _members(merged: list[dict], lineage: dict) -> dict[str, list[dict]]:
    root_of = lineage.get("root_of") or {}
    out: dict[str, list[dict]] = {}
    for e in merged:
        r = root_of.get(e["id"])
        if r:
            out.setdefault(r, []).append(e)
    return {r: sorted(es, key=_sort_key) for r, es in out.items()}


def _root_label(root: dict) -> str:
    return "Other" if root["id"] == "other" else root["label"]


def _pills(entries: list[dict]) -> list[dict]:
    shown, hidden = entries[:MAX_PER_ROOT], entries[MAX_PER_ROOT:]
    pills = []
    for e in shown:
        w = node_width(_downloads(e), FLOW_W)
        d = _downloads(e)
        dl = f"{fmt_downloads(d)} downloads" if d is not None else "downloads unknown"
        pills.append({"cls": e["type"] if e["type"] in COLORS else "more", "w": w, "label": truncate(e["name"], w),
                      "href": _primary_link(e), "title": f"{e['name']} · {TYPE_LABELS.get(e['type'], e['type'])} · {dl}"})
    if hidden:
        label = f"+{len(hidden)} more"
        pills.append({"cls": "more", "w": max(MIN_W, math.ceil(text_width(label) + 22)), "label": label,
                      "href": TREE_URL, "title": f"{len(hidden)} more in this family on the live tree"})
    return pills


def _rows(pills: list[dict]) -> list[list[dict]]:
    rows: list[list[dict]] = []
    for p in pills:
        if rows and sum(q["w"] + GAP_X for q in rows[-1]) + p["w"] <= FLOW_W:
            rows[-1].append(p)
        else:
            rows.append([p])
    return rows


def _pill_svg(p: dict, x: float, y: float) -> str:
    rect = (f'<rect class="n {p["cls"]}" x="{_n(x)}" y="{_n(y)}" width="{_n(p["w"])}" height="{NODE_H}" '
            f'rx="{RADIUS}"/>')
    text = (f'<text class="nl" x="{_n(x + p["w"] / 2)}" y="{_n(y + NODE_H / 2 + 4)}" text-anchor="middle">'
            f'{_attr(p["label"])}</text>')
    title = f"<title>{_attr(p['title'])}</title>"
    if p["href"]:
        return f'<a href="{_attr(p["href"])}" target="_blank" rel="noopener">{title}{rect}{text}</a>'
    return f"<g>{title}{rect}{text}</g>"


def _root_svg(root: dict, n: int, y: float) -> str:
    en, ar = _root_label(root), root.get("label_ar") or ""
    cls = "root scratch" if root["id"] == "from-scratch" else "root"
    x = PAD
    parts = [f'<a href="{_attr(TREE_URL)}" target="_blank" rel="noopener">',
             f"<title>{_attr(f'{en} · {ar} ({n})' if ar else f'{en} ({n})')}</title>",
             f'<rect class="{cls}" x="{x}" y="{_n(y)}" width="{ROOT_W}" height="{ROOT_H}" rx="{ROOT_H // 2}"/>',
             f'<text class="r-en" x="{x + 18}" y="{_n(y + 23.5)}">{_attr(en)}</text>',
             f'<text class="r-n" x="{_n(x + 18 + text_width(en) * 16 / FONT_PX * 1.04 + 7)}" y="{_n(y + 23.5)}">{n}</text>']
    if ar and ar != en:
        parts.append(f'<text class="r-ar" x="{x + ROOT_W - 18}" y="{_n(y + ROOT_H / 2 + 6.5)}" text-anchor="end" '
                     f'lang="ar">{_attr(ar)}</text>')
    parts.append("</a>")
    return "".join(parts)


def render_tree_svg(merged: list[dict], lineage: dict, generated_at: str) -> str:
    members = _members(merged, lineage)
    roots = [r for r in _ordered_roots(lineage) if members.get(r["id"])]
    n_models = sum(len(es) for es in members.values())

    body: list[str] = []
    y = float(HEAD_H)
    body.append(f'<line class="rule" x1="{PAD}" y1="{_n(y)}" x2="{WIDTH - PAD}" y2="{_n(y)}"/>')
    for root in roots:
        es = members[root["id"]]
        rows = _rows(_pills(es))
        content_h = len(rows) * NODE_H + (len(rows) - 1) * GAP_Y
        band_h = max(ROOT_H, content_h) + 2 * BAND_PAD
        mid = y + band_h / 2
        ry = mid - ROOT_H / 2
        top = mid - content_h / 2
        x1 = PAD + ROOT_W
        for i, row in enumerate(rows):
            ry_row = top + i * (NODE_H + GAP_Y)
            cy = ry_row + NODE_H / 2
            x2 = FLOW_X - 4
            body.append(f'<path class="branch" d="M{_n(x1)} {_n(mid)}C{_n(x1 + 34)} {_n(mid)} '
                        f'{_n(x2 - 34)} {_n(cy)} {_n(x2)} {_n(cy)}"/>')
            x = float(FLOW_X)
            for p in row:
                body.append(_pill_svg(p, x, ry_row))
                x += p["w"] + GAP_X
        body.append(f'<circle class="knot" cx="{_n(x1)}" cy="{_n(mid)}" r="3"/>')
        body.append(_root_svg(root, len(es), ry))
        y += band_h
        body.append(f'<line class="rule" x1="{PAD}" y1="{_n(y)}" x2="{WIDTH - PAD}" y2="{_n(y)}"/>')

    height = math.ceil(y + 44)
    sub = f"Arabic AI family tree · {n_models} models from {len(roots)} base families · {generated_at}"
    head = [f'<text class="title" x="{PAD}" y="42">Arabic AI Atlas</text>',
            f'<text class="sub" x="{PAD}" y="70">{_attr(sub)}</text>',
            f'<text class="lg-h" x="{WIDTH - PAD}" y="38" text-anchor="end">'
            f"One band per base family · pill width grows with Hugging Face downloads</text>"]
    present = {e["type"] for es in members.values() for e in es}
    types = [t for t in TYPE_ORDER if t in present]
    kx = WIDTH - PAD
    key = []
    for t in reversed(types):
        label = TYPE_LABELS.get(t, t)
        kx -= len(label) * 8.6
        key.append(f'<text class="lg" x="{_n(kx)}" y="70">{_attr(label)}</text>')
        kx -= 20
        key.append(f'<rect class="{t}" x="{_n(kx)}" y="58" width="14" height="14" rx="3"/>')
        kx -= 18
    head += reversed(key)
    footer = (f'<text class="footer" x="{WIDTH - PAD}" y="{height - 16}" text-anchor="end">'
              f"{_attr(f'Generated {generated_at} · full lineage on the live site · github.com/h9-tec/arabic-ai-atlas')}</text>")
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="Arabic AI Atlas: family tree of Arabic models by base model">',
        "<title>Arabic AI family tree</title>",
        f"<style>{_STYLE}" + "".join(f".{k} {{ fill: {v}; }}\n" for k, v in COLORS.items()) + "</style>",
        f'<rect class="bg" x="0" y="0" width="{WIDTH}" height="{height}"/>',
        *head,
        *body,
        footer,
        "</svg>",
    ]) + "\n"


def reused_datasets(merged: list[dict], limit: int = 10) -> list[tuple[str, str, int]]:
    """(dataset_id, dataset_name, n_models): models whose lowercase tasks or tags name the dataset id."""
    datasets = {e["id"]: e["name"] for e in merged if e.get("type") == "dataset"}
    counts: dict[str, int] = {}
    for e in merged:
        if e.get("type") not in MODEL_TYPES:
            continue
        for t in {str(x).lower() for x in (e.get("tasks") or []) + (e.get("tags") or [])}:
            if t in datasets:
                counts[t] = counts.get(t, 0) + 1
    rows = [(d, datasets[d], n) for d, n in counts.items() if n >= 1]
    return sorted(rows, key=lambda r: (-r[2], r[1].lower(), r[0]))[:limit]


def _linked(e: dict) -> str:
    link = _primary_link(e)
    return f"[{esc(e['name'])}]({link})" if link else esc(e["name"])


def render_tree_block(merged: list[dict], lineage: dict) -> str:
    members = _members(merged, lineage)
    roots = [r for r in _ordered_roots(lineage) if members.get(r["id"])]
    n = sum(len(es) for es in members.values())
    lines = [
        f'<a href="{TREE_URL}"><img src="assets/tree.svg" alt="Family tree of Arabic models: base model families '
        f'and the Arabic models built on them" width="100%"/></a>',
        "",
        f"_{n} models with known lineage · [explore the tree]({TREE_URL}) · add a base model with the base_model "
        f"field ([CONTRIBUTING](CONTRIBUTING.md))_",
        "",
        "| Base family | Models | Most downloaded |",
        "| --- | --- | --- |",
    ]
    for r in roots:
        en, ar = _root_label(r), r.get("label_ar") or ""
        name = f"{en} · {ar}" if ar and ar != en else en
        top = members[r["id"]][0]
        d = _downloads(top)
        lines.append(f"| {esc(name)} | {len(members[r['id']])} | {_linked(top)}"
                     f"{f' ({fmt_downloads(d)} ⬇)' if d else ''} |")
    ds = reused_datasets(merged)
    if ds:
        by_id = {e["id"]: e for e in merged}
        lines += ["", "| Dataset | Models citing it |", "| --- | --- |"]
        lines += [f"| {_linked(by_id[d])} | {k} |" for d, _name, k in ds]
    return "\n".join(lines)
