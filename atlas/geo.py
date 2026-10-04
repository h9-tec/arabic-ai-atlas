"""Tiny TopoJSON decoder and map projections (stdlib only, pure functions).

`decode(topo, name)` turns a world-atlas TopoJSON object into features with absolute lon/lat
rings; `fit(bbox, width, height, padding)` returns a projection fitted to a lon/lat box, the
same way d3's `projection.fitExtent` does for a densified box outline.
"""
import math
from typing import Callable

Ring = list[tuple[float, float]]
Polygon = list[Ring]  # outer ring first, then holes
Projector = Callable[[float, float], tuple[float, float]]


def decode_arcs(topo: dict) -> list[Ring]:
    """Absolute lon/lat arcs: undo delta encoding, then apply the quantization transform."""
    t = topo.get("transform")
    sx, sy = t["scale"] if t else (1.0, 1.0)
    tx, ty = t["translate"] if t else (0.0, 0.0)
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for p in arc:
            if t:
                x, y = x + p[0], y + p[1]
            else:
                x, y = p[0], p[1]
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    return arcs


def _ring(indices: list[int], arcs: list[Ring]) -> Ring:
    out: Ring = []
    for i in indices:
        pts = arcs[i] if i >= 0 else arcs[~i][::-1]
        out.extend(pts if not out else pts[1:])  # consecutive arcs share an endpoint
    return out


def decode(topo: dict, name: str = "countries") -> list[dict]:
    """Features of one object: {"id", "name", "polygons": [[outer, *holes], ...]}."""
    arcs = decode_arcs(topo)
    feats = []
    for g in topo["objects"][name]["geometries"]:
        if g["type"] == "Polygon":
            polys = [[_ring(r, arcs) for r in g["arcs"]]]
        elif g["type"] == "MultiPolygon":
            polys = [[_ring(r, arcs) for r in p] for p in g["arcs"]]
        else:
            polys = []
        feats.append({"id": g.get("id"), "name": (g.get("properties") or {}).get("name"), "polygons": polys})
    return feats


# ---------- raw projections (radians in, unitless plane out, y up) ----------

def mercator_raw() -> Callable[[float, float], tuple[float, float]]:
    def raw(lam: float, phi: float) -> tuple[float, float]:
        phi = max(-1.5, min(1.5, phi))
        return lam, math.log(math.tan(math.pi / 4 + phi / 2))
    return raw


def conic_conformal_raw(p0: float, p1: float) -> Callable[[float, float], tuple[float, float]]:
    """Lambert conformal conic with standard parallels p0, p1 (degrees), as d3.geoConicConformal."""
    y0, y1 = math.radians(p0), math.radians(p1)

    def tany(y: float) -> float:
        return math.tan((math.pi / 2 + y) / 2)

    cy0 = math.cos(y0)
    n = math.sin(y0) if y0 == y1 else math.log(cy0 / math.cos(y1)) / math.log(tany(y1) / tany(y0))
    f = cy0 * tany(y0) ** n / n
    eps = 1e-6

    def raw(lam: float, phi: float) -> tuple[float, float]:
        if f > 0:
            phi = max(phi, -math.pi / 2 + eps)
        else:
            phi = min(phi, math.pi / 2 - eps)
        r = f / tany(phi) ** n
        return r * math.sin(n * lam), f - r * math.cos(n * lam)
    return raw


def _rotated(raw, rotate: float):
    def plane(lon: float, lat: float) -> tuple[float, float]:
        lam = (lon + rotate + 180.0) % 360.0 - 180.0
        x, y = raw(math.radians(lam), math.radians(lat))
        return x, -y  # screen y grows downward
    return plane


def bbox_outline(bbox: tuple[float, float, float, float], step: float = 1.0) -> list[tuple[float, float]]:
    """The box (west, south, east, north) densified every `step` degrees, as map.js samples it."""
    w, s, e, n = bbox
    pts = []
    x = w
    while x <= e + 1e-9:
        pts += [(x, s), (x, n)]
        x += step
    y = s
    while y <= n + 1e-9:
        pts += [(w, y), (e, y)]
        y += step
    return pts


def fit(bbox: tuple[float, float, float, float], width: float, height: float, padding: float = 0.0,
        kind: str = "mercator", parallels: tuple[float, float] = (18.0, 34.0), rotate: float = 0.0) -> Projector:
    """Fit a projection so the lon/lat box fills [pad, width - pad] x [pad, height - pad], centred.

    `padding` below 1 is a fraction of each side's length, otherwise pixels. `kind` is
    "mercator" or "conic" (Lambert conformal conic with `parallels` and a `rotate` of the
    central meridian, matching d3.geoConicConformal().parallels(p).rotate([rotate, 0]))."""
    raw = mercator_raw() if kind == "mercator" else conic_conformal_raw(*parallels)
    plane = _rotated(raw, rotate)
    pts = [plane(lon, lat) for lon, lat in bbox_outline(bbox)]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    px = padding * width if padding < 1 else padding
    py = padding * height if padding < 1 else padding
    w, h = width - 2 * px, height - 2 * py
    k = min(w / (x1 - x0), h / (y1 - y0))
    ox = px + (w - k * (x1 - x0)) / 2 - k * x0
    oy = py + (h - k * (y1 - y0)) / 2 - k * y0

    def project(lon: float, lat: float) -> tuple[float, float]:
        x, y = plane(lon, lat)
        return ox + k * x, oy + k * y
    return project


def plane_aspect(bbox, kind: str = "mercator", parallels=(18.0, 34.0), rotate: float = 0.0) -> float:
    """Height / width of the projected box (to size a canvas that fits it without letterboxing)."""
    raw = mercator_raw() if kind == "mercator" else conic_conformal_raw(*parallels)
    plane = _rotated(raw, rotate)
    pts = [plane(lon, lat) for lon, lat in bbox_outline(bbox)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (max(ys) - min(ys)) / (max(xs) - min(xs))


# ---------- planar helpers ----------

def point_in_ring(x: float, y: float, ring: Ring) -> bool:
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def clip_ring(ring: Ring, x0: float, y0: float, x1: float, y1: float) -> Ring:
    """Sutherland-Hodgman clip of a closed ring against an axis-aligned rectangle."""
    def clip(pts, inside, cross):
        out = []
        if not pts:
            return out
        prev = pts[-1]
        for cur in pts:
            if inside(cur):
                if not inside(prev):
                    out.append(cross(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cross(prev, cur))
            prev = cur
        return out

    def at_x(xc):
        return lambda a, b: (xc, a[1] + (b[1] - a[1]) * (xc - a[0]) / (b[0] - a[0]))

    def at_y(yc):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (yc - a[1]) / (b[1] - a[1]), yc)

    pts = list(ring)
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    pts = clip(pts, lambda p: p[0] >= x0, at_x(x0))
    pts = clip(pts, lambda p: p[0] <= x1, at_x(x1))
    pts = clip(pts, lambda p: p[1] >= y0, at_y(y0))
    pts = clip(pts, lambda p: p[1] <= y1, at_y(y1))
    return pts
