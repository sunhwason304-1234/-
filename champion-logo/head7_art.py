"""CHAMPION park golf head v7 - bell/arch plate with all-over arabesque engraving and an enamel badge.

Layout (front / flat view, 84 x 80 mm):
  plate   : bell shape - flat face-side edge at the bottom, sides rising into a round dome
  pattern : all-over arabesque scrolls, eight-petal rosettes, fine concentric arcs in the dome
  badge   : black-enamel pentagon badge in the centre - CHAMPION / crown / C monogram / stars in gold
"""
import math
import random
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

from shaft import bezier, d_of, leaf, ribbon, spiral, star
from head_art import crown, outline
from head2_art import text, SERIF_KR
from head3_art import svg, CUT, GOLD

OUT = Path(__file__).parent / "head_v7"
OUT.mkdir(exist_ok=True)
W, H = 84.0, 80.0
CX = W / 2
SANS = ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 0)
BADGE_C = (CX, 45.5)


def plate():
    left = bezier((4, 77), (2.5, 44), (13, 3.5), (CX, 2.5), 80)
    right = [(W - x, y) for x, y in reversed(left)]
    g = Polygon(left + right[1:] + [(W - 4, 77)])
    return g.buffer(-3, join_style="round").buffer(3, join_style="round")


def inset(g, d):
    return g.buffer(-d, join_style="round")


def badge_shape():
    cx, cy = BADGE_C
    pts = [(cx - 11.5, cy - 12), (cx + 11.5, cy - 12), (cx + 13, cy + 1.5), (cx, cy + 13.5), (cx - 13, cy + 1.5)]
    return Polygon(pts).buffer(-1.6, join_style="round").buffer(1.6, join_style="round")


def rosette(c, r):
    """Eight-petal rosette: outlined petals, ring and a small cross in the centre."""
    parts = []
    for k in range(8):
        a = k * math.pi / 4
        p = leaf((c[0] + math.cos(a) * r * .18, c[1] + math.sin(a) * r * .18), a, r * .82, r * .52)
        parts.append(outline(p, .32))
    parts.append(Point(c).buffer(r * .24).difference(Point(c).buffer(r * .24 - .3)))
    parts += [box(c[0] - r * .11, c[1] - .14, c[0] + r * .11, c[1] + .14),
              box(c[0] - .14, c[1] - r * .11, c[0] + .14, c[1] + r * .11)]
    return unary_union(parts)


def scroll_unit():
    """Acanthus scroll (~11 mm): C-curve ending in a big spiral, leaf fronds, small counter-curl."""
    main = bezier((-5.0, 3.2), (-5.2, -2.8), (1.2, -5.2), (3.6, -1.2), 40)
    c = (1.9, -.9)
    main += spiral(c, math.dist(main[-1], c), math.atan2(main[-1][1] - c[1], main[-1][0] - c[0]), 1.35, cw=False, n=40)[1:]
    parts = [ribbon(main, .75, .22)]
    counter = bezier((-4.6, 1.6), (-2.6, 1.4), (-1.4, 3.4), (-2.6, 4.4), 20)
    c2 = (-2.0, 3.6)
    counter += spiral(c2, math.dist(counter[-1], c2), math.atan2(counter[-1][1] - c2[1], counter[-1][0] - c2[0]), 1.0, cw=True, n=24)[1:]
    parts.append(ribbon(counter, .5, .16))
    for t, da, L, w in [(.12, -1.2, 3.2, 1.2), (.28, -1.3, 2.9, 1.1), (.44, -1.25, 2.4, .95), (.6, -1.2, 1.9, .8)]:
        i = int(t * 40)
        (x0, y0), (x1, y1) = main[i], main[i + 1]
        parts.append(leaf(main[i], math.atan2(y1 - y0, x1 - x0) + da, L, w))
    parts.append(Point(-3.4, -1.0).buffer(.35))
    return unary_union(parts)


def pattern(P, keep_out):
    rnd = random.Random(11)
    unit = scroll_unit()
    tiles = []
    step = 10.5
    for j, y in enumerate(frange(2, H + 4, step * .82)):
        for x in frange(-3 + (step / 2 if j % 2 else 0), W + 6, step):
            g = unit if rnd.random() < .5 else affinity.scale(unit, -1, 1, origin=(0, 0))
            g = affinity.rotate(g, rnd.uniform(0, 360), origin=(0, 0))
            g = affinity.scale(g, rnd.uniform(.92, 1.1), rnd.uniform(.92, 1.1), origin=(0, 0))
            tiles.append(affinity.translate(g, x + rnd.uniform(-1.2, 1.2), y + rnd.uniform(-1.2, 1.2)))
    allowed = inset(P, 2.6).difference(keep_out)
    geo = unary_union(tiles).intersection(allowed)
    polys = getattr(geo, "geoms", [geo])
    return unary_union([p for p in polys if p.area > .8])


def frange(a, b, s):
    while a < b:
        yield a
        a += s


def panel():
    P = plate()
    B = badge_shape()
    g = [outline(inset(P, 1.4), .5), outline(inset(P, 2.3), .16)]
    # fine concentric arcs filling the dome
    arcs = unary_union([Point(CX, 46).buffer(r, quad_segs=64).difference(Point(CX, 46).buffer(r - .2, quad_segs=64))
                        for r in [33.2 + i * .9 for i in range(9)]])
    dome_zone = Point(CX, 46).buffer(41.5, quad_segs=64).difference(Point(CX, 46).buffer(32.6, quad_segs=64)).intersection(box(0, 0, W, 26))
    dome_arcs = arcs.intersection(inset(P, 2.6)).intersection(dome_zone)
    g.append(dome_arcs)
    # rings around the badge
    ring = unary_union([Point(BADGE_C).buffer(r, quad_segs=64).difference(Point(BADGE_C).buffer(r - .22, quad_segs=64))
                        for r in (17.0, 18.0)])
    g.append(ring.intersection(inset(P, 2.6)))
    # rosettes
    ros_pts = [(12.5, 50), (W - 12.5, 50), (22.5, 67.5), (W - 22.5, 67.5), (CX, 70.5), (21, 27), (W - 21, 27)]
    ros = [rosette(c, 4.4 if i < 5 else 3.6) for i, c in enumerate(ros_pts)]
    g += ros
    keep = unary_union([B.buffer(2.0), Point(BADGE_C).buffer(18.8),
                        *[Point(c).buffer(5.3 if i < 5 else 4.5) for i, c in enumerate(ros_pts)],
                        dome_zone.buffer(.6)])
    g.append(pattern(P, keep))
    engraved = unary_union(g).intersection(P)

    # badge: black enamel with gold (knocked-out) contents
    cx, cy = BADGE_C
    cr, _ = crown(cx, cy - 5.4, 7.4, 3.2)
    inner_line = outline(B.buffer(-1.1, join_style="round"), .3)
    stars = unary_union([star((cx + dx, cy + 8.2), .95) for dx in (-3, 0, 3)])
    gold_parts = unary_union([cr, inner_line, stars])
    t_name, _ = text(SANS, "CHAMPION", 1.9, cx, cy - 8.2, .45)
    t_mono, _ = text(SERIF_KR, "C", 7.0, cx, cy + 5.2)
    return engraved, B, gold_parts, t_name + t_mono, P


if __name__ == "__main__":
    import cairosvg, pymupdf
    eng, B, gold_parts, tx, P = panel()
    # line art: black = engrave, badge = enamel fill (black) with knocked-out gold elements (white)
    line = svg(W, H, f'<path d="{d_of(eng)}"/><path d="{d_of(B)}" fill="#000"/>'
                     f'<g fill="#fff"><path d="{d_of(gold_parts)}"/>{tx}</g><path d="{d_of(P)}" {CUT}/>')
    (OUT / "head7_top_layout.svg").write_text(line)
    pdf = OUT / "tmp.pdf"
    cairosvg.svg2pdf(bytestring=line.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf); d.set_metadata({"title": "CHAMPION park golf head v7 top layout"})
    d.save(OUT / "head7_top_layout.ai", garbage=3, deflate=True); pdf.unlink()
    gold = svg(W, H, GOLD + f'<path d="{d_of(P)}" fill="url(#g)"/>'
               f'<g fill="#6b4d1a" filter="url(#eng)"><path d="{d_of(eng)}"/></g>'
               f'<path d="{d_of(B)}" fill="#141312"/>'
               f'<g fill="url(#g)"><path d="{d_of(gold_parts)}"/>{tx}</g>', 3)
    (OUT / "head7_top_gold.svg").write_text(gold)
    cairosvg.svg2png(bytestring=gold.encode(), write_to=str(OUT / "head7_top_gold.png"), output_width=1800)
    cairosvg.svg2png(bytestring=line.encode(), write_to=str(OUT / "head7_top_layout.png"), output_width=1800,
                     background_color="white")
    print("ok")
