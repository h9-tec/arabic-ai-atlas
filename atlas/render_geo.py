"""Render the geographic map (assets/geo.svg): a static twin of the live site's map view.

Same framing, choropleth, hatching, bubble rings, callouts and International dock as
site/map.js, drawn with the stdlib only. Deterministic: no randomness, no clock, sorted input.
"""
import json
import math
from functools import lru_cache
from pathlib import Path

from atlas import geo
from atlas.render_map import _attr, _n

ROOT = Path(__file__).resolve().parent.parent
GEO_DIR = ROOT / "site" / "geo"
SITE_URL = "https://h9-tec.github.io/arabic-ai-atlas/"
FONT = ('"IBM Plex Sans Arabic", "Noto Sans Arabic", -apple-system, "Segoe UI", Tahoma, Roboto, '
        'Helvetica, Arial, sans-serif')

WIDTH = 1600
HEAD_H = 76  # title strip above the map
BBOX = (-13.2, 12.1, 59.8, 37.3)  # west, south, east, north: Morocco's coast to Oman, Yemen to Syria
PAD = 0.06
PROJ = {"kind": "conic", "parallels": (18.0, 34.0), "rotate": -23.0}
MAP_H = round(WIDTH * (1 - 2 * PAD) * geo.plane_aspect(BBOX, **PROJ) / (1 - 2 * PAD))
WINDOW = (-40.0, -5.0, 90.0, 58.0)  # lon/lat prefilter: polygons outside never reach the frame
CLIP_MARGIN = 12  # px beyond the frame, so clip edges and coast strokes stay off-canvas

TYPE_ORDER = ["llm", "asr", "tts", "ocr", "embedding", "tool", "benchmark", "dataset", "org", "agent-skill"]
TYPE_LABELS = {
    "llm": "LLM", "asr": "ASR", "tts": "TTS", "ocr": "OCR", "embedding": "Embedding", "tool": "Tool",
    "benchmark": "Benchmark", "dataset": "Dataset", "org": "Organisation", "agent-skill": "Agent skill",
}
COLORS = {
    "llm": "#4F46E5", "asr": "#0891B2", "tts": "#0E7490", "ocr": "#B45309", "embedding": "#7C3AED",
    "tool": "#475569", "benchmark": "#B91C1C", "dataset": "#047857", "org": "#334155", "agent-skill": "#9D174D",
}
R_MIN, R_MAX, RING_GAP = 4, 26, 3

FS_AR, FS_EN, FS_N = 22, 15, 15


# ---------- the same pure helpers as site/map.js ----------

def _jsround(x: float) -> int:
    return math.floor(x + 0.5)


def choropleth_step(count: int, top: int) -> int:
    if count <= 0 or top <= 0:
        return 0
    s = math.log(count + 1) / math.log(max(top, count) + 1)
    return max(0, min(4, math.floor(s * 5 - 1e-9)))


def bubble_radius(downloads: float, top: float) -> float:
    d, m = max(0, downloads or 0), max(1, top or 0)
    if d >= m:
        return R_MAX
    r = R_MIN + (R_MAX - R_MIN) * (math.sqrt(d + 1) - 1) / ((math.sqrt(m + 1) - 1) or 1)
    return max(R_MIN, min(R_MAX, r))


def bubble_layout(totals: dict, top: float) -> list[dict]:
    """One bubble per type in TYPE_ORDER, clockwise from 12 o'clock, arc share ∝ diameter."""
    order = TYPE_ORDER + sorted(k for k in totals if k not in TYPE_ORDER)
    items = [{"type": t, "n": totals[t]["n"], "downloads": totals[t]["downloads"],
              "r": bubble_radius(totals[t]["downloads"], top), "x": 0.0, "y": 0.0}
             for t in order if t in totals and totals[t]["n"] > 0]
    if len(items) <= 1:
        return items
    span = sum(2 * it["r"] + RING_GAP for it in items)
    ring = max(span / (2 * math.pi) * 1.1, 9)
    if len(items) == 2:
        ring = max(ring, (items[0]["r"] + items[1]["r"] + RING_GAP) / 2)
    acc = -(2 * items[0]["r"] + RING_GAP) / span * math.pi
    for it in items:
        share = (2 * it["r"] + RING_GAP) / span * 2 * math.pi
        a = -math.pi / 2 + acc + share / 2
        acc += share
        it["x"] = _jsround(ring * math.cos(a) * 100) / 100
        it["y"] = _jsround(ring * math.sin(a) * 100) / 100
    return items


def ring_extent(items: list[dict]) -> float:
    return max((math.hypot(it["x"], it["y"]) + it["r"] for it in items), default=0.0)


def fmt(n: float) -> str:
    if not n:
        return "0"
    if n >= 1e6:
        s = f"{n / 1e6:.1f}"
        return (s[:-2] if s.endswith(".0") else s) + "M"
    if n >= 1e3:
        return f"{_jsround(n / 1e3)}K"
    return str(int(n))


def plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def _downloads(e: dict) -> int:
    return (e.get("metrics") or {}).get("downloads") or 0


def aggregate(entries: list[dict]) -> tuple[dict, dict]:
    by: dict[str, dict] = {}
    intl: dict[str, dict] = {}
    for e in entries:
        c = e.get("country") or "INTL"
        bucket = intl if c == "INTL" else by.setdefault(c, {})
        t = bucket.setdefault(e["type"], {"n": 0, "downloads": 0, "entries": []})
        t["n"] += 1
        t["downloads"] += _downloads(e)
        t["entries"].append(e)
    return by, intl


def cell_max(entries: list[dict], intl: bool) -> int:
    cells: dict[tuple[str, str], int] = {}
    for e in entries:
        c = e.get("country") or "INTL"
        if (c == "INTL") != intl:
            continue
        cells[(c, e["type"])] = cells.get((c, e["type"]), 0) + _downloads(e)
    return max(cells.values(), default=0)


# ---------- geometry ----------

@lru_cache(maxsize=1)
def _geo_data() -> tuple[list[dict], dict]:
    topo = json.loads((GEO_DIR / "countries-110m.json").read_text(encoding="utf-8"))
    meta = json.loads((GEO_DIR / "centroids.json").read_text(encoding="utf-8"))
    return geo.decode(topo, "countries"), meta


def projection():
    return geo.fit(BBOX, WIDTH, MAP_H, PAD, **PROJ)


def _in_window(ring) -> bool:
    w, s, e, n = WINDOW
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return max(xs) >= w and min(xs) <= e and max(ys) >= s and min(ys) <= n


def _path(polygons, project) -> str:
    """SVG path data for polygons projected and clipped to the frame (plus margin)."""
    x0, y0, x1, y1 = -CLIP_MARGIN, -CLIP_MARGIN, WIDTH + CLIP_MARGIN, MAP_H + CLIP_MARGIN
    parts = []
    for poly in polygons:
        if not poly or not _in_window(poly[0]):
            continue
        for ring in poly:
            pts = geo.clip_ring([project(lon, lat) for lon, lat in ring], x0, y0, x1, y1)
            out: list[str] = []
            for x, y in pts:
                p = f"{_n(x)} {_n(y)}"
                if not out or out[-1] != p:
                    out.append(p)
            if len(out) >= 3:
                parts.append("M" + out[0] + "L" + " ".join(out[1:]) + "Z")
    return "".join(parts)


def _graticule(project) -> str:
    parts = []
    for lon in range(-40, 95, 5):
        pts = [project(lon, lat) for lat in range(-10, 61, 2)]
        parts.append("M" + "L".join(f"{_n(x)} {_n(y)}" for x, y in pts))
    for lat in range(-10, 61, 5):
        pts = [project(lon, lat) for lon in range(-40, 91, 2)]
        parts.append("M" + "L".join(f"{_n(x)} {_n(y)}" for x, y in pts))
    return "".join(parts)


# ---------- style ----------

_LIGHT = ("--bg: #E6ECEA; --sheet: #F5F8F7; --ink: #15203A; --muted: #55627A; --rule: #C3CDC9; "
          "--rule-strong: #8A99A8; --sea: #D9E3E6; --sea-line: #B4C5CB; --grat: #BFCDD2; --land-x: #EDF1EF; "
          "--border-x: #D3DBD8; --ch0: #D3DCE9; --ch1: #B2C1D8; --ch2: #8EA2C3; --ch3: #6981AA; --ch4: #4B6390; "
          "--hatch-bg: #E4E9EC; --hatch-line: #A3B0BF; --halo: rgba(245, 248, 247, .92); "
          "--bubble-stroke: #FFFFFF; --ctry-line: #FFFFFF;")
_DARK = ("--bg: #0E1724; --sheet: #142032; --ink: #E3E9F0; --muted: #98A6BA; --rule: #26354B; "
         "--rule-strong: #4A5D78; --sea: #0A111D; --sea-line: #182740; --grat: #16233A; --land-x: #152031; "
         "--border-x: #1E2B40; --ch0: #22324C; --ch1: #2A3F62; --ch2: #35517F; --ch3: #44659C; --ch4: #5A7EB8; "
         "--hatch-bg: #172336; --hatch-line: #33445E; --halo: rgba(10, 17, 29, .9); "
         "--bubble-stroke: #0E1724; --ctry-line: #0E1724;")

_STYLE = f"""
svg {{ {_LIGHT} }}
@media (prefers-color-scheme: dark) {{
  svg {{ {_DARK} }}
}}
text {{ font-family: {FONT}; fill: var(--ink); }}
.bg {{ fill: var(--bg); }}
.sea {{ fill: var(--sea); }}
.frame {{ fill: none; stroke: var(--rule-strong); stroke-width: 1; }}
.graticule {{ fill: none; stroke: var(--grat); stroke-width: .6; }}
.wl {{ fill: none; stroke-linejoin: round; }}
.wl-0, .wl-2 {{ stroke: var(--sea-line); }}
.wl-1, .wl-3 {{ stroke: var(--sea); }}
.wl-0 {{ opacity: .45; stroke-width: 16; }}
.wl-1 {{ stroke-width: 12; }}
.wl-2 {{ opacity: .9; stroke-width: 8; }}
.wl-3 {{ stroke-width: 4; }}
.land {{ fill: var(--land-x); stroke: none; }}
.borders-foreign {{ fill: none; stroke: var(--border-x); stroke-width: .7; }}
.borders-arab {{ fill: none; stroke: var(--ctry-line); stroke-width: 1; }}
.unlisted {{ fill: url(#hatch); }}
.hatch-bg {{ fill: var(--hatch-bg); }}
.hatch-line {{ stroke: var(--hatch-line); stroke-width: 1.4; }}
.s-none {{ fill: var(--hatch-bg); }}
.s0 {{ fill: var(--ch0); }}
.s1 {{ fill: var(--ch1); }}
.s2 {{ fill: var(--ch2); }}
.s3 {{ fill: var(--ch3); }}
.s4 {{ fill: var(--ch4); }}
.pt {{ stroke: var(--ink); stroke-width: 1; }}
.ghost {{ font-size: 17px; font-weight: 500; fill: var(--muted); opacity: .8; }}
.halo, .ghost {{ paint-order: stroke; stroke: var(--halo); stroke-width: 4px; stroke-linejoin: round; }}
.bubble {{ stroke: var(--bubble-stroke); stroke-width: 1.2; fill-opacity: .85; }}
a:hover .bubble {{ fill-opacity: 1; }}
.over {{ fill: none; stroke: var(--muted); stroke-dasharray: 2 2; }}
.leader {{ stroke: var(--ink); stroke-width: 1; opacity: .55; }}
.leader-dot {{ fill: var(--ink); opacity: .7; }}
.l-ar {{ font-size: {FS_AR}px; font-weight: 700; }}
.l-en {{ font-size: {FS_EN}px; fill: var(--muted); }}
.l-n {{ font-size: {FS_N}px; font-weight: 600; }}
.l-n.empty {{ font-weight: 400; fill: var(--muted); }}
.title {{ font-size: 32px; font-weight: 700; }}
.sub {{ font-size: 17px; fill: var(--muted); }}
.panel {{ fill: var(--sheet); fill-opacity: .92; stroke: var(--rule); stroke-width: 1; }}
.lg-h {{ font-size: 16px; font-weight: 600; }}
.lg {{ font-size: 15px; fill: var(--muted); }}
.lg-ring {{ fill: none; stroke: var(--muted); stroke-width: 1; }}
.void {{ opacity: .35; }}
.dock-ar {{ font-size: 26px; font-weight: 700; }}
.dock-en {{ font-size: 16px; fill: var(--muted); }}
.dock-note {{ font-size: 14px; fill: var(--muted); }}
.di-t {{ font-size: 17px; font-weight: 600; }}
.di-n {{ font-size: 15px; fill: var(--muted); }}
.rule {{ stroke: var(--rule); stroke-width: 1; }}
.footer {{ font-size: 15px; fill: var(--muted); }}
"""


def _text_w(s: str, px: float) -> float:
    """Rough rendered width of Latin text at `px` font size."""
    return sum((0.32 if ch in "il.,:;' " else 0.62 if ch.isupper() or ch.isdigit() else 0.54) for ch in s) * px


def _href(code: str, type_: str | None = None) -> str:
    return f"{SITE_URL}#country={code}" + (f"&type={type_}" if type_ else "")


def _bubble_title(where: str, t: str, cell: dict) -> str:
    title = f"{where} · {TYPE_LABELS.get(t, t)} · {plural(cell['n'], 'entry', 'entries')}"
    if cell["downloads"]:
        title += f" · {fmt(cell['downloads'])} downloads"
    top = sorted((e for e in cell["entries"] if _downloads(e)), key=lambda e: (-_downloads(e), e["name"].lower(), e["id"]))[:3]
    if top:
        title += " · most downloaded: " + ", ".join(f"{e['name']} ({fmt(_downloads(e))})" for e in top)
    return title


def _legend_steps(top: int) -> list[str]:
    lows: dict[int, int] = {}
    for n in range(1, top + 1):
        lows.setdefault(choropleth_step(n, top), n)
    labels = []
    for i in range(5):
        lo = lows.get(i)
        hi = next((lows[j] for j in range(i + 1, 5) if j in lows), None)
        if lo is None:
            labels.append("")
        elif hi is None:
            labels.append(str(lo) if lo == top else f"{lo}–{top}")
        else:
            labels.append(str(lo) if hi - 1 == lo else f"{lo}–{hi - 1}")
    return labels


def render_geo_svg(merged: list[dict], generated_at: str) -> str:
    features, meta = _geo_data()
    project = projection()
    countries, others = meta["countries"], meta["arab_league_other"]
    arab_ids = {m["id"]: (c, True) for c, m in countries.items()}
    arab_ids.update({m["id"]: (c, False) for c, m in others.items()})
    arab_ids.setdefault("732", ("EH", False))  # Western Sahara: hatched, unlabeled

    entries = sorted(merged, key=lambda e: e["id"])
    by, intl = aggregate(entries)
    counts = {c: sum(t["n"] for t in by.get(c, {}).values()) for c in countries}
    top = max(counts.values(), default=0)
    dmax = cell_max(entries, False)
    imax = cell_max(entries, True)

    # --- geometry layers
    land = _path([p for f in features for p in f["polygons"]], project)
    defs = [
        f'<clipPath id="frame"><rect x="0" y="0" width="{WIDTH}" height="{MAP_H}"/></clipPath>',
        '<pattern id="hatch" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)">'
        '<rect class="hatch-bg" width="6" height="6"/><line class="hatch-line" x1="0" y1="0" x2="0" y2="6"/></pattern>',
        f'<path id="land" d="{land}"/>',
    ]
    fills, borders = [], []
    for f in sorted(features, key=lambda f: f["id"] or ""):
        if f["id"] not in arab_ids:
            continue
        d = _path(f["polygons"], project)
        if not d:
            continue
        code, listed = arab_ids[f["id"]]
        cls = "unlisted"
        if listed:
            cls = f"s{choropleth_step(counts[code], top)}" if counts[code] else "s-none"
        defs.append(f'<path id="c{f["id"]}" d="{d}"/>')
        fills.append(f'<use href="#c{f["id"]}" class="{cls}" data-code="{code}"/>')
        borders.append(f'<use href="#c{f["id"]}"/>')
    points = []
    for code, m in sorted(list(countries.items()) + list(others.items())):
        if not m.get("point"):
            continue
        x, y = project(*m["lonlat"])
        if not (0 <= x <= WIDTH and 0 <= y <= MAP_H):
            continue
        listed = code in countries
        cls = (f"s{choropleth_step(counts[code], top)}" if counts[code] else "s-none") if listed else "unlisted"
        points.append(f'<circle class="pt {cls}" cx="{_n(x)}" cy="{_n(y)}" r="3"/>')
    ghosts = []
    for code, m in sorted(others.items()):
        if m.get("nolabel"):
            continue
        x, y = project(*m["lonlat"])
        ghosts.append(f'<text class="ghost" x="{_n(x)}" y="{_n(y)}" text-anchor="middle" lang="ar">{_attr(m["ar"])}</text>')

    geo_layer = [
        f'<g clip-path="url(#frame)">',
        f'<rect class="sea" x="0" y="0" width="{WIDTH}" height="{MAP_H}"/>',
        f'<path class="graticule" d="{_graticule(project)}"/>',
        *(f'<use href="#land" class="wl wl-{i}"/>' for i in range(4)),
        '<use href="#land" class="land"/>',
        '<use href="#land" class="borders-foreign"/>',
        *fills,
        '<g class="borders-arab">', *borders, "</g>",
        *points,
        *ghosts,
        "</g>",
    ]

    # --- marks: leader lines, bubble rings, labels (quietest first, busiest drawn on top)
    marks = []
    for code in sorted(countries, key=lambda c: (counts[c], c)):
        m = countries[code]
        ring = bubble_layout(by.get(code, {}), dmax)
        ext = ring_extent(ring)
        px, py = project(*m["lonlat"])
        ax, ay = project(*m["anchor"]) if m.get("anchor") else (px, py)
        g = [f'<g class="mark" data-code="{code}">']
        if m.get("anchor"):
            g.append(f'<line class="leader" x1="{_n(px)}" y1="{_n(py)}" x2="{_n(ax)}" y2="{_n(ay)}"/>')
            g.append(f'<circle class="leader-dot" cx="{_n(px)}" cy="{_n(py)}" r="2.4"/>')
        for it in ring:
            cell = by[code][it["type"]]
            g.append(f'<a href="{_attr(_href(code, it["type"]))}" target="_blank" rel="noopener">'
                     f'<title>{_attr(_bubble_title(m["en"], it["type"], cell))}</title>'
                     f'<circle class="bubble" cx="{_n(ax + it["x"])}" cy="{_n(ay + it["y"])}" r="{_n(it["r"])}" '
                     f'fill="{COLORS.get(it["type"], "#6B7280")}"/></a>')
        side = m.get("side", "below")
        off = max(ext, 4) + 5
        if side == "right":
            tx, ty, anchor = off, -FS_AR * 0.15, "start"
        elif side == "left":
            tx, ty, anchor = -off, -FS_AR * 0.15, "end"
        else:
            tx, ty, anchor = 0, off + FS_AR * 0.85, "middle"
        x = ax + tx
        n = counts[code]
        lab = [f'<a href="{_attr(_href(code))}" target="_blank" rel="noopener">',
               f'<title>{_attr(m["en"] + ", " + plural(n, "entry", "entries"))}</title>',
               f'<text class="halo l-ar" x="{_n(x)}" y="{_n(ay + ty)}" text-anchor="{anchor}" lang="ar">{_attr(m["ar"])}</text>',
               f'<text class="halo l-en" x="{_n(x)}" y="{_n(ay + ty + FS_EN + 4)}" text-anchor="{anchor}">{_attr(m["en"])}</text>',
               f'<text class="halo l-n{"" if n else " empty"}" x="{_n(x)}" y="{_n(ay + ty + 2 * FS_EN + 7)}" '
               f'text-anchor="{anchor}">{_attr(plural(n, "entry", "entries") if n else "no entries yet")}</text>',
               "</a>"]
        g += lab
        g.append("</g>")
        marks.extend(g)

    # --- legend (bottom left of the map)
    lg_w, lg_x = 384, 14
    refs = sorted({v for v in (1000, 10 ** _jsround(math.log10(max(dmax, 10)) - 1), dmax) if 0 < v <= dmax})
    size_h = 2 * R_MAX + 26 if refs else 0
    lg_h = 26 + 46 + 30 + size_h + 14
    lg_y = MAP_H - 14 - lg_h
    L = [f'<g class="legend" transform="translate({lg_x},{_n(lg_y)})">',
         f'<rect class="panel" x="0" y="0" width="{lg_w}" height="{_n(lg_h)}" rx="3"/>']
    y = 24
    L.append(f'<text class="lg-h" x="14" y="{y}">Entries per country</text>')
    steps = _legend_steps(top)
    sw = (lg_w - 28 - 4 * 3) / 5
    for i, label in enumerate(steps):
        sx = 14 + i * (sw + 3)
        void = "" if label else " void"
        L.append(f'<rect class="s{i}{void}" x="{_n(sx)}" y="{y + 8}" width="{_n(sw)}" height="11"/>')
        if label:
            L.append(f'<text class="lg" x="{_n(sx)}" y="{y + 36}">{label}</text>')
    y += 46 + 20
    L.append(f'<rect class="unlisted" x="14" y="{y - 11}" width="28" height="12"/>')
    L.append(f'<text class="lg" x="50" y="{y}">Arab League, nothing listed yet</text>')
    y += 30
    L.append(f'<text class="lg-h" x="14" y="{y}">Bubble area: Hugging Face downloads per type</text>')
    if refs:
        base = y + 8 + 2 * R_MAX
        bx = 16
        for v in refs:
            r = bubble_radius(v, dmax)
            cx = bx + max(r, 18)
            L.append(f'<circle class="lg-ring" cx="{_n(cx)}" cy="{_n(base - r)}" r="{_n(r)}"/>')
            L.append(f'<text class="lg" x="{_n(cx)}" y="{_n(base + 17)}" text-anchor="middle">{fmt(v)}</text>')
            bx = cx + max(r, 18) + 16
    L.append("</g>")

    # --- International dock (below the map)
    dock_y = HEAD_H + MAP_H
    itypes = [t for t in TYPE_ORDER if t in intl] + sorted(t for t in intl if t not in TYPE_ORDER)
    n_intl = sum(intl[t]["n"] for t in itypes)
    item_h = 2 * R_MAX + 20
    D = [f'<a href="{_attr(_href("INTL"))}" target="_blank" rel="noopener">'
         f'<title>Built outside the region, or by global teams. Not placed on the map; bubbles use their own scale.</title>'
         f'<text class="dock-ar" x="24" y="{dock_y + 44}" lang="ar">دولي</text>'
         f'<text class="dock-en" x="24" y="{dock_y + 72}">International · {n_intl}</text></a>',
         f'<text class="dock-note" x="24" y="{dock_y + 92}">Own bubble scale, dashed</text>']
    x, row = 220.0, 0
    for t in itypes:
        cell = intl[t]
        cap = plural(cell["n"], "entry", "entries")
        dl = f"{fmt(cell['downloads'])} downloads" if cell["downloads"] else ""
        w = 2 * R_MAX + 14 + max(_text_w(TYPE_LABELS.get(t, t), 17), _text_w(cap, 15), _text_w(dl, 15)) + 26
        if x + w > WIDTH - 20:
            x, row = 220.0, row + 1
        cy = dock_y + 14 + row * item_h + R_MAX + 4
        cx = x + R_MAX + 2
        r = bubble_radius(cell["downloads"], imax)
        tx = x + 2 * R_MAX + 14
        lines = [(TYPE_LABELS.get(t, t), "di-t"), (cap, "di-n")] + ([(dl, "di-n")] if dl else [])
        ty0 = cy - (len(lines) - 1) * 9 + 6
        D.append(f'<a href="{_attr(_href("INTL", t))}" target="_blank" rel="noopener">'
                 f'<title>{_attr(_bubble_title("International", t, cell))}</title>'
                 f'<circle class="over" cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r + 3)}"/>'
                 f'<circle class="bubble" cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r)}" fill="{COLORS.get(t, "#6B7280")}"/>'
                 + "".join(f'<text class="{cls}" x="{_n(tx)}" y="{_n(ty0 + i * 18)}">{_attr(s)}</text>'
                           for i, (s, cls) in enumerate(lines)) + "</a>")
        x += w
    if not itypes:
        D.append(f'<text class="dock-note" x="200" y="{dock_y + 50}">No international entries yet.</text>')
    dock_h = 28 + (row + 1) * item_h
    height = math.ceil(HEAD_H + MAP_H + dock_h + 34)

    count = len(merged)
    head = [
        f'<text class="title" x="24" y="42">Arabic AI Atlas</text>',
        f'<text class="sub" x="24" y="66">{_attr(f"Where Arabic AI is built · {count} entries · {generated_at}")}</text>',
    ]
    types_present = [t for t in TYPE_ORDER if t in intl or any(t in by.get(c, {}) for c in countries)]
    kx = WIDTH - 24
    key = []
    for t in reversed(types_present):
        label = TYPE_LABELS[t]
        kx -= _text_w(label, 15)
        key.append(f'<text class="lg" x="{_n(kx)}" y="{66}">{label}</text>')
        kx -= 16
        key.append(f'<circle cx="{_n(kx + 6)}" cy="61" r="6.5" fill="{COLORS[t]}"/>')
        kx -= 16
    head += reversed(key)
    head.append(f'<text class="lg-h" x="{WIDTH - 24}" y="38" text-anchor="end">'
                f'One bubble per entry type · click a country or bubble to open it on the live map</text>')
    footer = (f'<text class="footer" x="{WIDTH - 24}" y="{height - 14}" text-anchor="end">'
              f"{_attr(f'Generated {generated_at} from {count} entries · github.com/h9-tec/arabic-ai-atlas')}</text>")

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="Arabic AI Atlas: map of Arabic AI entries by country">',
        "<title>Arabic AI Atlas</title>",
        f"<style>{_STYLE}</style>",
        "<defs>", *defs, "</defs>",
        f'<rect class="bg" x="0" y="0" width="{WIDTH}" height="{height}"/>',
        *head,
        f'<g transform="translate(0,{HEAD_H})">',
        *geo_layer,
        *marks,
        *L,
        f'<rect class="frame" x="0.5" y="0.5" width="{WIDTH - 1}" height="{MAP_H - 1}"/>',
        "</g>",
        *D,
        f'<line class="rule" x1="24" y1="{_n(dock_y + dock_h)}" x2="{WIDTH - 24}" y2="{_n(dock_y + dock_h)}"/>',
        footer,
        "</svg>",
    ]) + "\n"
