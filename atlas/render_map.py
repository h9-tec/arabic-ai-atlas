"""Render the Arabic AI landscape map (assets/map.svg) from merged entries.

Stdlib only and deterministic: no randomness, no clock, everything sorted.
"""
import math
from xml.sax.saxutils import escape

from atlas.render_readme import FLAGS, fmt_downloads

WIDTH = 1600
PAD = 40  # horizontal outer padding
PAD_Y = 24  # vertical outer padding (keeps the hero map under 1000px tall)
ROW_PAD = 6
GUTTER = 150
CELL_PAD = 6
NODE_H, GAP, RADIUS = 28, 5, 5
MIN_W, MAX_W = 72, 220
FONT_PX = 11.5
# lowercase advance at semibold (renders bold in Arial): 7.1px measured at 12.5px, scaled
CHAR_W = 7.1 * FONT_PX / 12.5
_NARROW = set("iljtfrI.,:;!|'()[] -/")
_WIDE = set("mwMW@%")
MAX_NODES = 6
REPO_URL = "https://github.com/h9-tec/arabic-ai-atlas"
FONT = '-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'

COLUMNS = [
    ("SA", FLAGS["SA"], "Saudi Arabia"),
    ("AE", FLAGS["AE"], "UAE"),
    ("EG", FLAGS["EG"], "Egypt"),
    ("QA", FLAGS["QA"], "Qatar"),
    ("MA", FLAGS["MA"], "Morocco"),
    ("OTHER", "🌐", "Other"),
    ("INTL", FLAGS["INTL"], "International"),
]
OTHER = {"JO", "TN", "LB", "KW", "OM", "BH", "DZ", "LY", "SD", "IQ", "SY", "YE", "PS", "MR", "SO", "DJ", "KM"}
BANDS = [
    ("LLMs", ("llm",)),
    ("Speech", ("asr", "tts")),
    ("Vision", ("ocr",)),
    ("Embeddings & Tools", ("embedding", "tool", "benchmark")),
    ("Datasets", ("dataset",)),
]
ANCHORS = {
    "llm": "#-large-language-models",
    "asr": "#%EF%B8%8F-speech-recognition",
    "tts": "#-text-to-speech",
    "ocr": "#-ocr",
    "embedding": "#-embeddings",
    "tool": "#-tools",
    "benchmark": "#-benchmarks",
    "dataset": "#-datasets",
}
COLORS = {
    "llm": "#4F46E5", "asr": "#0891B2", "tts": "#0E7490", "ocr": "#B45309",
    "embedding": "#7C3AED", "tool": "#475569", "benchmark": "#B91C1C",
    "dataset": "#047857", "more": "#6B7280",
}
LEGEND = [("llm", "LLM"), ("asr", "ASR"), ("tts", "TTS"), ("ocr", "OCR"),
          ("embedding", "Embedding"), ("tool", "Tool"), ("benchmark", "Benchmark"), ("dataset", "Dataset")]
LINK_ORDER = ("hf", "github", "paper", "website")

SLOTS = {code: 2 if code == "INTL" else 1 for code, _, _ in COLUMNS}  # INTL holds most entries
SLOT_W = (WIDTH - 2 * PAD - GUTTER) / sum(SLOTS.values())
COL_X = {}  # column -> (left x offset from grid start, width)
_x = 0.0
for _code, _, _ in COLUMNS:
    COL_X[_code] = (_x, SLOT_W * SLOTS[_code])
    _x += SLOT_W * SLOTS[_code]


def _attr(value) -> str:
    return escape(str(value), {'"': "&quot;"})


def _n(x: float) -> str:
    """Compact, deterministic number formatting for coordinates."""
    s = f"{x:.1f}"
    return s[:-2] if s.endswith(".0") else s


def _downloads(entry: dict) -> int | None:
    m = entry.get("metrics")
    return m.get("downloads") if m else None


def _column(entry: dict) -> str:
    c = entry.get("country", "INTL")
    if c in OTHER:
        return "OTHER"
    return c if c in {code for code, _, _ in COLUMNS} else "INTL"


def node_width(downloads: int | None, inner_w: float) -> float:
    score = math.log10((downloads or 0) + 1) + 1
    w = MIN_W + (min(score, 8) - 1) / 7 * (MAX_W - MIN_W)
    return min(max(w, MIN_W), MAX_W, inner_w)


def text_width(label: str) -> float:
    """Estimated rendered width: CHAR_W per lowercase char, scaled for caps/narrow/wide."""
    total = 0.0
    for ch in label:
        if ch in _WIDE:
            total += CHAR_W * 1.45
        elif ch in _NARROW:
            total += CHAR_W * 0.55
        elif ch.isupper() or ch.isdigit():
            total += CHAR_W * 1.2
        else:
            total += CHAR_W
    return total


def truncate(label: str, width: float) -> str:
    room = width - 16
    if text_width(label) <= room:
        return label
    cut = label
    while cut and text_width(cut.rstrip() + "…") > room:
        cut = cut[:-1]
    return (cut.rstrip() or label[:1]) + "…"


def _primary_link(entry: dict) -> str | None:
    links = entry.get("links") or {}
    return next((links[k] for k in LINK_ORDER if links.get(k)), None)


def _sort_key(entry: dict):
    return (-(_downloads(entry) or 0), entry["name"].lower(), entry["id"])


def _cell_nodes(entries: list[dict], types: tuple[str, ...], inner_w: float) -> list[dict]:
    """Node specs for one cell: top MAX_NODES, or one fewer plus a `+N more` node."""
    ranked = sorted(entries, key=_sort_key)
    shown, hidden = (ranked, []) if len(ranked) <= MAX_NODES else (ranked[: MAX_NODES - 1], ranked[MAX_NODES - 1:])
    nodes = []
    for e in shown:
        w = node_width(_downloads(e), inner_w)
        nodes.append({
            "cls": e["type"], "w": w, "label": truncate(e["name"], w), "href": _primary_link(e),
            "title": f"{e['name']} · {e.get('org') or '—'} · {fmt_downloads(_downloads(e))} downloads",
        })
    if hidden:
        counts = {t: sum(1 for e in hidden if e["type"] == t) for t in types}
        top = max(types, key=lambda t: (counts[t], -types.index(t)))
        nodes.append({
            "cls": "more", "w": MIN_W, "label": f"+{len(hidden)} more", "href": f"{REPO_URL}{ANCHORS[top]}",
            "title": f"{len(hidden)} more in the README",
        })
    return nodes


def _flow(nodes: list[dict], inner_w: float) -> tuple[list[tuple[dict, float, float]], float]:
    """Flow-wrap nodes into centred lines; return (node, x, y) offsets and height."""
    lines: list[list[dict]] = []
    for node in nodes:
        if lines:
            used = sum(n["w"] for n in lines[-1]) + GAP * len(lines[-1])
            if used + node["w"] <= inner_w:
                lines[-1].append(node)
                continue
        lines.append([node])
    placed = []
    for i, line in enumerate(lines):
        line_w = sum(n["w"] for n in line) + GAP * (len(line) - 1)
        x = (inner_w - line_w) / 2
        for node in line:
            placed.append((node, x, i * (NODE_H + GAP)))
            x += node["w"] + GAP
    height = len(lines) * NODE_H + max(len(lines) - 1, 0) * GAP
    return placed, height


def _node_svg(node: dict, x: float, y: float) -> str:
    rect = (f'<rect class="n {node["cls"]}" x="{_n(x)}" y="{_n(y)}" width="{_n(node["w"])}" '
            f'height="{NODE_H}" rx="{RADIUS}"/>')
    text = (f'<text class="nl" x="{_n(x + node["w"] / 2)}" y="{_n(y + NODE_H / 2 + 4)}" '
            f'text-anchor="middle">{_attr(node["label"])}</text>')
    title = f"<title>{_attr(node['title'])}</title>"
    if node["href"]:
        return f'<a href="{_attr(node["href"])}" target="_blank" rel="noopener">{title}{rect}{text}</a>'
    return f"<g>{title}{rect}{text}</g>"


_STYLE = f"""
svg {{ --bg: #FFFFFF; --text: #1F2328; --muted: #59636E; --grid: #D0D7DE; --band: #F6F8FA; }}
@media (prefers-color-scheme: dark) {{
  svg {{ --bg: #0D1117; --text: #E6EDF3; --muted: #9198A1; --grid: #30363D; --band: #161B22; }}
}}
text {{ font-family: {FONT}; fill: var(--text); }}
.bg {{ fill: var(--bg); }}
.band {{ fill: var(--band); }}
.grid {{ stroke: var(--grid); stroke-width: 1; fill: none; }}
.title {{ font-size: 28px; font-weight: 700; }}
.sub {{ font-size: 14px; fill: var(--muted); }}
.colhead {{ font-size: 15px; font-weight: 700; }}
.colsub {{ font-size: 12px; fill: var(--muted); }}
.bandlabel {{ font-size: 16px; font-weight: 700; }}
.bandsub {{ font-size: 12px; fill: var(--muted); }}
.legend {{ font-size: 12px; fill: var(--muted); }}
.footer {{ font-size: 12px; fill: var(--muted); }}
.nl {{ font-size: {FONT_PX}px; font-weight: 600; fill: #FFFFFF; pointer-events: none; }}
a:hover .n {{ opacity: 0.85; }}
""" + "".join(f".{k} {{ fill: {v}; }}\n" for k, v in COLORS.items())


def _wrap_label(label: str, max_chars: int = 13) -> list[str]:
    words, lines = label.split(), [""]
    for w in words:
        cand = f"{lines[-1]} {w}".strip()
        if len(cand) <= max_chars or not lines[-1]:
            lines[-1] = cand
        else:
            lines.append(w)
    return lines


def render_svg(merged: list[dict], generated_at: str) -> str:
    count = len(merged)  # header total includes papers
    # Papers are literature, not located artifacts: never drawn on the grid.
    merged = [e for e in merged if e.get("type") != "paper"]
    band_of = {t: label for label, types in BANDS for t in types}
    drawn = [e for e in merged if e.get("type") in band_of]
    grid: dict[tuple[str, str], list[dict]] = {}
    for e in drawn:
        grid.setdefault((band_of[e["type"]], _column(e)), []).append(e)

    body: list[str] = []
    shading: list[str] = []
    x0 = PAD + GUTTER

    # Title block and legend
    body.append(f'<text class="title" x="{PAD}" y="{PAD_Y + 26}">Arabic AI Atlas</text>')
    body.append(f'<text class="sub" x="{PAD}" y="{PAD_Y + 48}">'
                f"{_attr(f'The Arabic AI ecosystem · {count} entries · {generated_at}')}</text>")
    lx = WIDTH - PAD
    legend = []
    for cls, label in reversed(LEGEND):
        tw = len(label) * 7 + 4
        lx -= tw
        legend.append(f'<text class="legend" x="{lx}" y="{PAD_Y + 48}">{label}</text>')
        lx -= 16
        legend.append(f'<rect class="{cls}" x="{lx}" y="{PAD_Y + 38}" width="12" height="12" rx="3"/>')
        lx -= 14
    body.extend(reversed(legend))

    # Column headers
    head_y = PAD_Y + 64
    col_counts = {code: sum(1 for e in drawn if _column(e) == code) for code, _, _ in COLUMNS}
    for i, (code, flag, name) in enumerate(COLUMNS):
        left, cw = COL_X[code]
        cx = x0 + left + cw / 2
        body.append(f'<text class="colhead" x="{_n(cx)}" y="{head_y + 17}" text-anchor="middle">'
                    f"{flag} {code}</text>")
        n = col_counts[code]
        body.append(f'<text class="colsub" x="{_n(cx)}" y="{head_y + 34}" text-anchor="middle">'
                    f"{_attr(name)} · {n}</text>")
    grid_top = head_y + 44

    # Bands
    y = grid_top
    lines = [f'<line class="grid" x1="{PAD}" y1="{grid_top}" x2="{WIDTH - PAD}" y2="{grid_top}"/>']
    for b, (label, types) in enumerate(BANDS):
        cells = {}
        for code, _, _ in COLUMNS:
            inner = COL_X[code][1] - 2 * CELL_PAD
            cells[code] = _flow(_cell_nodes(grid.get((label, code), []), types, inner), inner)
        content_h = max([h for _, h in cells.values()] + [NODE_H])
        row_h = max(content_h + 2 * ROW_PAD, 24 + 18 * len(_wrap_label(label)) + 8)
        if b % 2 == 0:
            shading.append(f'<rect class="band" x="{PAD}" y="{_n(y)}" width="{WIDTH - 2 * PAD}" height="{_n(row_h)}"/>')
        band_n = sum(len(grid.get((label, code), [])) for code, _, _ in COLUMNS)
        label_lines = _wrap_label(label)
        for k, part in enumerate(label_lines):
            body.append(f'<text class="bandlabel" x="{PAD + 14}" y="{_n(y + 22 + k * 18)}">{_attr(part)}</text>')
        body.append(f'<text class="bandsub" x="{PAD + 14}" y="{_n(y + 20 + len(label_lines) * 18)}">'
                    f"{band_n} entries</text>")
        for i, (code, _, _) in enumerate(COLUMNS):
            placed, _h = cells[code]
            cx = x0 + COL_X[code][0] + CELL_PAD
            for node, nx, ny in placed:
                body.append(_node_svg(node, cx + nx, y + ROW_PAD + ny))
        y += row_h
        lines.append(f'<line class="grid" x1="{PAD}" y1="{_n(y)}" x2="{WIDTH - PAD}" y2="{_n(y)}"/>')
    for gx in [x0 + left for left, _ in COL_X.values()] + [WIDTH - PAD]:
        lines.append(f'<line class="grid" x1="{_n(gx)}" y1="{head_y}" x2="{_n(gx)}" y2="{_n(y)}"/>')

    height = math.ceil(y + 22 + 16)
    footer = (f'<text class="footer" x="{WIDTH - PAD}" y="{height - 16}" text-anchor="end">'
              f"{_attr(f'Generated {generated_at} from {count} entries · github.com/h9-tec/arabic-ai-atlas')}</text>")

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="Arabic AI Atlas map">',
        "<title>Arabic AI Atlas</title>",
        f"<style>{_STYLE}</style>",
        f'<rect class="bg" x="0" y="0" width="{WIDTH}" height="{height}"/>',
        *shading,
        *lines,
        *body,
        footer,
        "</svg>",
    ]) + "\n"
