"""CHAMPION park golf head v5 - top plate layout with a laurel wreath (front / flat view).

Same rounded-triangle plate as v3/v4. Layout:
  top    : CHAMPION (serif), subtitle between two rules, five stars
  centre : crowned shield with C monogram inside a laurel wreath
  bottom : crossed stems tied with a ribbon bow near the tip
Laurel leaves carry an engraved centre vein, with small berries along the branch.
"""
import math
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from shaft import bezier, d_of, ribbon, star
from head_art import crown, outline
from head2_art import text, SERIF_KR
from head3_art import plate, inset, shield, svg, CUT, GOLD, W, H, CX

OUT = Path(__file__).parent / "head_v5"
OUT.mkdir(exist_ok=True)
SANS = ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 0)


def laurel_leaf(base, ang, L, Wd):
    """Pointed laurel leaf (asymmetric almond) with an engraved centre vein."""
    pts = []
    for i in range(41):
        t = i / 40
        pts.append((t * L, (math.sin(math.pi * t) ** .85) * (1 - .25 * t) * Wd / 2))
    pts += [(x, -y) for x, y in reversed(pts[1:-1])]
    g = Polygon(pts)
    vein = LineString([(L * .1, 0), (L * .8, 0)]).buffer(max(.1, Wd * .07))
    g = g.difference(vein)
    g = affinity.rotate(g, ang, origin=(0, 0), use_radians=True)
    return affinity.translate(g, *base)


def branch(side=-1):
    """Left branch (side=-1); the right one is its mirror."""
    p = bezier((CX - 1.5, 64.2), (CX - 19.5, 61.5), (CX - 24.5, 45), (CX - 16.5, 31.5), 80)
    parts = [ribbon(p, .95, .35)]
    n = 10
    for k in range(n):
        t = .1 + .84 * k / (n - 1)
        i = int(t * 80)
        (xa, ya), (xb, yb) = p[i], p[i + 1]
        a = math.atan2(yb - ya, xb - xa)
        L = 6.6 - 2.6 * t
        parts.append(laurel_leaf(p[i], a + .62, L, L * .42))           # outer leaf (left of travel)
        parts.append(laurel_leaf(p[i], a - .55, L * .88, L * .38))     # inner leaf
        if k % 3 == 1:                                                  # berries
            c = (p[i][0] + math.cos(a - 1.3) * 2.2, p[i][1] + math.sin(a - 1.3) * 2.2)
            parts.append(Point(c).buffer(.62, quad_segs=12))
    (xa, ya), (xb, yb) = p[-3], p[-1]
    parts.append(laurel_leaf(p[-1], math.atan2(yb - ya, xb - xa), 4.6, 1.8))  # tip leaf
    g = unary_union(parts)
    return g if side < 0 else affinity.scale(g, xfact=-1, origin=(CX, 0))


def bow(cx, cy):
    """Ribbon bow with two tails where the stems cross."""
    loops = []
    for s in (-1, 1):
        lp = Polygon([(cx, cy)] + [(cx + s * (3.4 * math.sin(math.pi * t)) + s * 1.2 * t, cy - 2.2 * math.sin(2 * math.pi * t) * .6 - .6 * math.sin(math.pi * t))
                                   for t in [i / 30 for i in range(31)]])
        loops.append(outline(lp.buffer(.35), .55))
        tail = bezier((cx + s * .6, cy + .6), (cx + s * 1.8, cy + 2.4), (cx + s * 2.2, cy + 3.6), (cx + s * 3.6, cy + 4.8), 20)
        loops.append(ribbon(tail, 1.1, .5))
    loops.append(Point(cx, cy).buffer(.9, quad_segs=12))
    return unary_union(loops)


def panel():
    P = plate()
    g = [outline(inset(P, 1.8), .5), outline(inset(P, 2.9), .16)]
    g += [star((CX + dx, 27.2), 1.35) for dx in (-7, -3.5, 0, 3.5, 7)]
    sh, _ = shield(CX, 39.0, 12.6, 14.8)
    g.append(sh)
    cr, _ = crown(CX, 35.4, 7.0, 3.3)
    g.append(cr)
    g += [branch(-1), branch(1)]
    g.append(bow(CX, 63.4))
    geo = unary_union(g).intersection(inset(P, .4))
    t1, _ = text(SERIF_KR, "CHAMPION", 5.4, CX, 16.4, 1.0)
    t2, w2 = text(SANS, "ROYAL GOLD", 2.4, CX, 22.2, .8)
    rules = unary_union([box(CX - w2 / 2 - 12, 21.0, CX - w2 / 2 - 2, 21.25),
                         box(CX + w2 / 2 + 2, 21.0, CX + w2 / 2 + 12, 21.25)])
    geo = unary_union([geo, rules])
    mono, _ = text(SERIF_KR, "C", 5.0, CX, 49.0)
    return geo, t1 + t2 + mono, P


if __name__ == "__main__":
    import cairosvg, pymupdf
    geo, tx, P = panel()
    line = svg(W, H, f'<path d="{d_of(geo)}"/>{tx}<path d="{d_of(P)}" {CUT}/>')
    (OUT / "head5_top_layout.svg").write_text(line)
    pdf = OUT / "tmp.pdf"
    cairosvg.svg2pdf(bytestring=line.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf); d.set_metadata({"title": "CHAMPION park golf head v5 top layout"})
    d.save(OUT / "head5_top_layout.ai", garbage=3, deflate=True); pdf.unlink()
    gold = svg(W, H, GOLD + f'<path d="{d_of(P)}" fill="url(#g)"/>'
               f'<g fill="#6b4d1a" filter="url(#eng)"><path d="{d_of(geo)}"/>{tx}</g>', 3)
    (OUT / "head5_top_gold.svg").write_text(gold)
    cairosvg.svg2png(bytestring=gold.encode(), write_to=str(OUT / "head5_top_gold.png"), output_width=1800)
    cairosvg.svg2png(bytestring=line.encode(), write_to=str(OUT / "head5_top_layout.png"), output_width=1800,
                     background_color="white")
    print("ok")
