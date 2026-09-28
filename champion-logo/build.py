"""CHAMPION wordmark generator.

Custom letterforms built from geometric primitives (shapely), then exported as
outlined SVG paths (no font dependency - safe for print / Illustrator).

Units: cap height = 100.
"""
import math
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

OUT = Path(__file__).parent
CAP = 100.0
S = 22.0          # main stroke weight
TRACK = 11.0      # letter spacing
SLANT = 12.0      # italic angle (degrees)


def rrect(x0, y0, x1, y1, r):
    """Rounded rectangle."""
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, quad_segs=24)


def ring(x0, y0, x1, y1, r):
    outer = rrect(x0, y0, x1, y1, r)
    ri = max(r - S, 2)
    inner = rrect(x0 + S, y0 + S, x1 - S, y1 - S, ri)
    return outer.difference(inner)


def stroke(p0, p1, w=S):
    return LineString([p0, p1]).buffer(w / 2, cap_style="flat", join_style="mitre")


def stem(x, w=S, y0=0, y1=CAP):
    return box(x, y0, x + w, y1)


# ---- letters: each returns (main_geometry, accent_geometry_or_None, advance) ----

def C():
    w = 78
    g = ring(0, 0, w, CAP, 30).difference(box(w * 0.58, S + 4, w + 1, CAP - S - 4))
    return g, None, w


def H():
    w = 76
    g = unary_union([stem(0), stem(w - S), box(0, 40, w, 40 + S * 0.9)])
    return g, None, w


def A():
    w = 88
    top = 16  # flat apex width
    outer = Polygon([(0, 0), (w, 0), (w / 2 + top / 2, CAP), (w / 2 - top / 2, CAP)])
    # counter: open to baseline (no crossbar) -> inverted V
    k = S * 1.18
    inner = Polygon([(k, -1), (w - k, -1), (w / 2, CAP - S * 1.55)])
    g = outer.difference(inner)
    # accent: "peak" triangle sitting in the counter (trophy / summit)
    acc = Polygon([(w / 2 - 11, 0), (w / 2 + 11, 0), (w / 2, 22)])
    return g, acc, w


def M():
    w = 100
    v = 34  # height of the middle vertex
    h = S * 0.6
    ld = Polygon([(0, CAP), (S * 1.2, CAP), (w / 2 + h, v), (w / 2 - h, v)])
    rd = affinity.scale(ld, xfact=-1, origin=(w / 2, 0))
    g = unary_union([stem(0), stem(w - S), ld, rd]).difference(box(-1, CAP, w + 1, CAP + 40))
    return g, None, w


def P():
    w = 76
    bowl = ring(0, CAP * 0.36, w, CAP, 26).difference(box(-1, CAP * 0.36 - 1, S / 2, CAP + 1))
    # square off the top-left and bottom-left corners of the bowl so it joins the stem
    g = unary_union([stem(0), bowl, box(0, CAP - S, 30, CAP), box(0, CAP * 0.36, 30, CAP * 0.36 + S)])
    return g, None, w


def I():
    return stem(0), None, S


def O():
    d = CAP
    c = Point(d / 2, d / 2)
    g = c.buffer(d / 2, quad_segs=48).difference(c.buffer(d / 2 - S, quad_segs=48))
    ball = c.buffer(13, quad_segs=32)  # golf ball in the counter
    return g, ball, d


def N():
    w = 80
    diag = Polygon([(0, CAP), (S * 1.05, CAP), (w, 0), (w - S * 1.05, 0)])
    g = unary_union([stem(0), stem(w - S), diag])
    return g, None, w


LETTERS = [C, H, A, M, P, I, O, N]


def build(slit=True):
    mains, accents, x = [], [], 0.0
    for fn in LETTERS:
        g, acc, adv = fn()
        mains.append(affinity.translate(g, x))
        if acc is not None:
            accents.append(affinity.translate(acc, x))
        x += adv + TRACK
    width = x - TRACK
    main = unary_union(mains)
    acc = unary_union(accents) if accents else None
    if slit:
        # speed line cut through the lower third
        band = box(-50, 26, width + 50, 30.5)
        main = main.difference(band)
    # italic shear
    shear = math.tan(math.radians(SLANT))
    main = affinity.skew(main, xs=SLANT, origin=(0, 0))
    if acc is not None:
        # triangles shear with the letters; the golf ball stays perfectly round
        parts = []
        for a in getattr(acc, "geoms", [acc]):
            if len(a.exterior.coords) > 10:
                c = a.centroid
                parts.append(affinity.translate(a, c.y * shear))
            else:
                parts.append(affinity.skew(a, xs=SLANT, origin=(0, 0)))
        acc = unary_union(parts)
    return main, acc, width + CAP * shear


def to_path(geom):
    """shapely (Multi)Polygon -> SVG path data, y flipped (SVG y-down)."""
    polys = getattr(geom, "geoms", [geom])
    parts = []
    for p in polys:
        for ringc in [p.exterior, *p.interiors]:
            pts = list(ringc.coords)
            parts.append("M" + " L".join(f"{px:.2f},{CAP - py:.2f}" for px, py in pts) + "Z")
    return " ".join(parts)


def svg(main, acc, width, fg, accent, bg=None, pad=18, extra_defs=""):
    W, H = width + pad * 2, CAP + pad * 2
    bg_el = f'<rect width="{W:.1f}" height="{H:.1f}" fill="{bg}"/>' if bg else ""
    acc_el = f'<path d="{to_path(acc)}" fill="{accent}"/>' if acc is not None else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" '
            f'width="{W * 4:.0f}" height="{H * 4:.0f}">'
            f'<defs>{extra_defs}</defs>{bg_el}'
            f'<g transform="translate({pad},{pad})" fill-rule="evenodd">'
            f'<path d="{to_path(main)}" fill="{fg}"/>{acc_el}</g></svg>')


GOLD_DEFS = ('<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#F6E3A1"/><stop offset=".45" stop-color="#D4A93C"/>'
             '<stop offset=".55" stop-color="#A97C1F"/><stop offset="1" stop-color="#E9C766"/>'
             '</linearGradient>')

if __name__ == "__main__":
    main, acc, width = build()
    variants = {
        "champion_black.svg": svg(main, acc, width, "#111111", "#111111"),
        "champion_black_gold.svg": svg(main, acc, width, "#111111", "#C9A13B"),
        "champion_gold_on_black.svg": svg(main, acc, width, "url(#gold)", "#FFFFFF",
                                          bg="#0E0E0E", extra_defs=GOLD_DEFS),
        "champion_white.svg": svg(main, acc, width, "#FFFFFF", "#FFFFFF", bg="#1B1B1B"),
    }
    for name, s in variants.items():
        (OUT / name).write_text(s)
    print("wrote", ", ".join(variants), f"width={width:.1f}")
