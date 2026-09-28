"""CHAMPION park golf shaft artwork (33.6 x 388 mm, same size as the existing GOBBLE shaft file).

Premium black & gold concept based on high-end park golf shafts (Honma 5-star / Gold Classic style):
gold bands, carbon texture, grade stars, gold filigree, laurel wreath (champion symbol).
Everything is outlined vector (text converted to paths) so the SVG/PDF can go straight to print.

Grip side is the top of the canvas; text reads top-to-bottom like the existing file.
"""
import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

import build as wordmark

OUT = Path(__file__).parent
W, H = 33.6, 388.0
CX = W / 2
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


# ---------------------------------------------------------------- geometry helpers

def d_of(geom):
    polys = getattr(geom, "geoms", [geom])
    out = []
    for p in polys:
        if p.is_empty:
            continue
        for r in [p.exterior, *p.interiors]:
            out.append("M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in r.coords) + "Z")
    return " ".join(out)


def bezier(p0, p1, p2, p3, n=60):
    pts = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def spiral(center, r0, a0, turns, cw=True, n=80, shrink=0.78):
    """Inward spiral starting at angle a0 (rad), radius r0."""
    s = -1 if cw else 1
    pts = []
    for i in range(n + 1):
        t = i / n
        a = a0 + s * t * turns * 2 * math.pi
        r = r0 * (1 - shrink * t)
        pts.append((center[0] + r * math.cos(a), center[1] + r * math.sin(a)))
    return pts


def ribbon(pts, w0, w1):
    """Tapered stroke along a polyline (width w0 -> w1)."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        xa, ya = pts[max(i - 1, 0)]
        xb, yb = pts[min(i + 1, n - 1)]
        dx, dy = xb - xa, yb - ya
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        t = i / (n - 1)
        w = (w0 + (w1 - w0) * t) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    poly = Polygon(left + right[::-1]).buffer(0)
    return unary_union([poly, Point(pts[-1]).buffer(w1 * 0.9, quad_segs=8)])


def leaf(base, angle, length, width):
    """Almond leaf starting at base, pointing at angle (rad)."""
    pts = []
    for i in range(41):
        t = i / 40
        pts.append((t * length, math.sin(math.pi * t) ** 0.9 * width / 2))
    pts += [(x, -y) for x, y in reversed(pts[1:-1])]
    g = Polygon(pts)
    g = affinity.rotate(g, angle, origin=(0, 0), use_radians=True)
    return affinity.translate(g, *base)


def mirror(g):
    return unary_union([g, affinity.scale(g, xfact=-1, origin=(CX, 0))])


def star(c, r, k=0.42):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * k
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    return Polygon(pts)


# ---------------------------------------------------------------- text -> outlines

_fonts = {}


def text_d(font, s, cap_mm, track_mm=0.0):
    """Outline text. Baseline at y=0, cap top at y=-cap_mm (y-down). Returns (d, width_mm)."""
    f = _fonts.setdefault(font, TTFont(font))
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    cap = getattr(f["OS/2"], "sCapHeight", 0) or f["head"].unitsPerEm * 0.7
    k = cap_mm / cap
    pen = SVGPathPen(gs)
    x = 0.0
    for ch in s:
        gname = cmap.get(ord(ch))
        if gname is None:
            continue
        gs[gname].draw(TransformPen(pen, (k, 0, 0, -k, x, 0)))
        x += hmtx[gname][0] * k + track_mm
    return pen.getCommands(), x - track_mm


def vtext(font, s, cap_mm, y0, track_mm=0.0, cx=CX, fill="url(#gold)", center=True):
    """Text reading top-to-bottom, letter tops pointing right, centred on cx."""
    d, w = text_d(font, s, cap_mm, track_mm)
    ys = y0 - w / 2 if center else y0
    return (f'<g transform="translate({cx - cap_mm / 2:.3f},{ys:.3f}) rotate(90)">'
            f'<path d="{d}" fill="{fill}"/></g>'), w


# ---------------------------------------------------------------- motifs

def filigree(y_top, height, flip=False):
    """Symmetric gold scroll ornament, spanning y_top..y_top+height."""
    s = height / 50.0
    def P(x, y):  # local (x from centre, y 0..50) -> page
        yy = (50 - y) if flip else y
        return (CX + x * s * 0.62, y_top + yy * s)
    parts = []
    # main S-scroll: centre-bottom sweeping out to the edge and curling in
    main = [P(*p) for p in bezier((0.8, 49), (3, 36), (22, 40), (21, 24))]
    curl_c = P(15.5, 23)
    r0 = math.dist(main[-1], curl_c)
    a0 = math.atan2(main[-1][1] - curl_c[1], main[-1][0] - curl_c[0])
    main += spiral(curl_c, r0, a0, 1.15, cw=not flip)[1:]
    parts.append(ribbon(main, 1.35 * s, 0.26 * s))
    # upper scroll
    up = [P(*p) for p in bezier((0.8, 30), (1, 18), (14, 16), (12, 6))]
    c2 = P(8.6, 7.2)
    up += spiral(c2, math.dist(up[-1], c2), math.atan2(up[-1][1] - c2[1], up[-1][0] - c2[0]),
                 1.0, cw=flip)[1:]
    parts.append(ribbon(up, 1.0 * s, 0.2 * s))
    # lower outward curl
    lo = [P(*p) for p in bezier((0.8, 44), (6, 50), (16, 50), (19, 43))]
    c3 = P(16.2, 44.5)
    lo += spiral(c3, math.dist(lo[-1], c3), math.atan2(lo[-1][1] - c3[1], lo[-1][0] - c3[0]),
                 0.9, cw=flip)[1:]
    parts.append(ribbon(lo, 0.8 * s, 0.18 * s))
    # leaves on the upper scroll
    for t in (0.35, 0.6):
        i = int(t * 60)
        (x0, y0), (x1, y1) = up[i], up[i + 1]
        a = math.atan2(y1 - y0, x1 - x0)
        parts.append(leaf(up[i], a + (0.9 if not flip else -0.9), 6.0 * s, 2.2 * s))
    # leaves along the main scroll
    for t, ang, L in [(0.15, -0.2, 8.0), (0.3, 0.3, 7.0), (0.45, -0.9, 6.5), (0.6, 0.9, 5.5)]:
        i = int(t * 60)
        (x0, y0), (x1, y1) = main[i], main[i + 1]
        base_ang = math.atan2(y1 - y0, x1 - x0) + (ang if not flip else -ang)
        parts.append(leaf(main[i], base_ang - (math.pi / 2.6 if not flip else -math.pi / 2.6),
                          L * s, 2.8 * s))
    half = unary_union(parts)
    g = mirror(half)
    # centre jewel: vertical diamond + dots
    cy = y_top + (32 if not flip else 18) * s
    g = unary_union([g,
                     Polygon([(CX, cy - 7 * s), (CX + 1.8 * s, cy), (CX, cy + 7 * s), (CX - 1.8 * s, cy)]),
                     Point(CX, y_top + (2.5 if not flip else 47.5) * s).buffer(0.9 * s, quad_segs=12),
                     Point(CX, y_top + (47.5 if not flip else 2.5) * s).buffer(1.2 * s, quad_segs=12)])
    return g.intersection(box(0.9, -10, W - 0.9, H + 10))


def laurel(y0, y1, side):
    """Laurel branch running from y1 (bottom) up to y0, on side -1 (left) / +1 (right)."""
    xs = CX + side * 9.2
    stem_pts = [(xs + side * 2.2 * math.sin(math.pi * (1 - t)) ** 1.2 - side * 2.4 * (1 - t),
                 y1 - (y1 - y0) * t) for t in [i / 60 for i in range(61)]]
    parts = [ribbon(stem_pts, 0.75, 0.25)]
    n = 7
    for k in range(n):
        t = 0.1 + 0.85 * k / (n - 1)
        i = int(t * 60)
        (xa, ya), (xb, yb) = stem_pts[i], stem_pts[min(i + 1, 60)]
        ang = math.atan2(yb - ya, xb - xa)
        L = 5.2 * (1 - 0.35 * t)
        parts.append(leaf(stem_pts[i], ang + side * 0.75, L, L * 0.42))   # outer leaf
        parts.append(leaf(stem_pts[i], ang - side * 0.55, L * 0.85, L * 0.38))  # inner leaf
    parts.append(leaf(stem_pts[-1], -math.pi / 2 - side * 0.15, 4.2, 1.8))  # tip
    return unary_union(parts)


def crown(cy, w=12.0, h=7.5):
    x0, x1 = CX - w / 2, CX + w / 2
    body = Polygon([(x0, cy + h / 2), (x1, cy + h / 2), (x1 + 0.4, cy - h / 2 + 1.5),
                    (CX + w * 0.25, cy + 0.2), (CX, cy - h / 2), (CX - w * 0.25, cy + 0.2),
                    (x0 - 0.4, cy - h / 2 + 1.5)])
    base = box(x0, cy + h / 2 + 0.7, x1, cy + h / 2 + 1.9)
    balls = [Point(p).buffer(0.85, quad_segs=10) for p in
             [(x0 - 0.4, cy - h / 2 + 1.0), (CX, cy - h / 2 - 0.6), (x1 + 0.4, cy - h / 2 + 1.0)]]
    return unary_union([body, base, *balls])


# ---------------------------------------------------------------- composition

GOLD = ('<linearGradient id="gold" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#9C7420"/><stop offset=".3" stop-color="#E9C766"/>'
        '<stop offset=".5" stop-color="#FFF1BF"/><stop offset=".7" stop-color="#D4A93C"/>'
        '<stop offset="1" stop-color="#8A651B"/></linearGradient>'
        '<linearGradient id="goldv" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#F6E3A1"/><stop offset=".45" stop-color="#D4A93C"/>'
        '<stop offset=".55" stop-color="#A97C1F"/><stop offset="1" stop-color="#E9C766"/>'
        '</linearGradient>')


def carbon(bg, weave):
    return (f'<pattern id="carbon" width="1.6" height="1.6" patternUnits="userSpaceOnUse">'
            f'<rect width="1.6" height="1.6" fill="{bg}"/>'
            f'<rect width=".8" height=".8" fill="{weave}"/><rect x=".8" y=".8" width=".8" height=".8" fill="{weave}"/>'
            f'</pattern>')


THEMES = {
    "black_gold": dict(bg="#0B0B0C", weave="#17181A", gold="url(#gold)", ink="url(#gold)",
                       sub="#CFCFCF", logo="url(#goldv)", ball="#FFFFFF", peak="#FFFFFF"),
    "white_gold": dict(bg="#F7F5F0", weave="#EDEAE2", gold="url(#gold)", ink="#141414",
                       sub="#555555", logo="#141414", ball="url(#gold)", peak="url(#gold)"),
}


def artwork(theme, guides=True):
    T = THEMES[theme]
    el = []
    # base + carbon weave
    # (drawn as real squares, not an SVG pattern, so Illustrator / print shows no tile seams)
    el.append(f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>')
    cell = 0.8
    sq = "".join(f"M{c * cell:.1f},{r * cell:.1f}h{cell}v{cell}h-{cell}z"
                 for r in range(int(H / cell)) for c in range(int(W / cell) + 1) if (r + c) % 2 == 0)
    el.append(f'<path d="{sq}" fill="{T["weave"]}"/>')
    # edge pinstripes
    for x in (1.3, W - 1.3 - 0.25):
        el.append(f'<rect x="{x}" y="10" width=".25" height="{H - 20}" fill="{T["gold"]}"/>')
    # top & bottom gold bands (grip end / hosel end)
    def band(y, flip=False):
        a, b = (y, y + 7) if not flip else (y - 7, y)
        s = [f'<rect x="0" y="{a}" width="{W}" height="7" fill="url(#goldv)"/>']
        for off in (1.6, 2.3):
            yy = b + off if not flip else a - off - 0.3
            s.append(f'<rect x="0" y="{yy}" width="{W}" height=".3" fill="{T["gold"]}"/>')
        return "".join(s)
    el.append(band(0))
    el.append(band(H, flip=True))

    # crown + small wordmark under the grip band
    el.append(f'<path d="{d_of(crown(17))}" fill="{T["gold"]}"/>')
    t, _ = vtext(SERIF, "PREMIUM PARK GOLF", 1.35, 39.5, track_mm=0.4, fill=T["sub"])
    el.append(t)

    # upper filigree
    el.append(f'<path d="{d_of(filigree(54, 54))}" fill="{T["gold"]}"/>')

    # CHAMPION wordmark (vertical)
    main, acc, ww = wordmark.build()
    L = 150.0                       # logo length on the shaft (mm)
    k = L / ww
    y_logo = 116
    m_d, a_d = wordmark.to_path(main), wordmark.to_path(acc)
    # acc contains the A-peak triangle and the golf ball: split by size for separate colours
    peak = [g for g in acc.geoms if len(g.exterior.coords) <= 10]
    ball = [g for g in acc.geoms if len(g.exterior.coords) > 10]
    cap_mm = 100 * k
    el.append(f'<g transform="translate({CX + cap_mm / 2:.3f},{y_logo}) rotate(90) scale({k:.5f})" '
              f'fill-rule="evenodd"><path d="{m_d}" fill="{T["logo"]}"/>'
              f'<path d="{wordmark.to_path(unary_union(peak))}" fill="{T["peak"]}"/>'
              f'<path d="{wordmark.to_path(unary_union(ball))}" fill="{T["ball"]}"/></g>')

    # laurel wreath + 5 grade stars
    ys0, ys1 = 276, 322
    el.append(f'<path d="{d_of(unary_union([laurel(ys0, ys1, -1), laurel(ys0, ys1, 1)]))}" fill="{T["gold"]}"/>')
    stars = unary_union([star((CX, ys0 + 5 + i * 8.6), 3.0) for i in range(5)])
    el.append(f'<path d="{d_of(stars)}" fill="{T["gold"]}"/>')

    # model / spec lines
    t, _ = vtext(SANS, "CP-01", 3.4, 337, track_mm=0.6, cx=CX + 2.6, fill=T["gold"])
    el.append(t)
    t, _ = vtext(SANS, "10-AXIS CARBON  R", 1.5, 337, track_mm=0.3, cx=CX - 3.0, fill=T["sub"])
    el.append(t)

    # SHAFT weight badge
    bx, by, bw, bh = CX - 6, 353, 12, 14
    el.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx=".8" fill="none" '
              f'stroke="{T["gold"]}" stroke-width=".35"/>')
    el.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="4" rx=".8" fill="{T["gold"]}"/>')
    d, w = text_d(SANS, "SHAFT", 1.8, 0.3)
    badge_ink = "#141414" if theme == "white_gold" else T["bg"]
    el.append(f'<path transform="translate({CX - w / 2:.3f},{by + 2.9})" d="{d}" fill="{badge_ink}"/>')
    d, w = text_d(SANS, "56G", 3.6, 0.15)
    el.append(f'<path transform="translate({CX - w / 2:.3f},{by + 10.9})" d="{d}" fill="{T["ink"] if theme == "white_gold" else T["gold"]}"/>')

    guide = (f'<rect x="0" y="0" width="{W}" height="{H}" fill="none" stroke="#FF00FF" '
             f'stroke-width=".15" stroke-dasharray="1 .6"/>') if guides else ""
    defs = GOLD
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
            f'viewBox="0 0 {W} {H}"><defs>{defs}</defs>{"".join(el)}{guide}</svg>')


if __name__ == "__main__":
    for theme in THEMES:
        (OUT / f"shaft_{theme}.svg").write_text(artwork(theme, guides=False))
    print("ok")
