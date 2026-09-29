"""CHAMPION park golf head v4 - top plate layout with flame wings (front / flat view).

Same rounded-triangle plate as v3. Layout:
  top    : CHAMPION (serif), subtitle between two rules, five stars
  centre : crowned shield with C monogram, flame / phoenix wings rising left & right
  edge   : single contour + faint circle marks
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

OUT = Path(__file__).parent / "head_v4"
OUT.mkdir(exist_ok=True)
SANS = ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 0)


def blade(p0, c1, c2, tip, w0, curl=0.0):
    """Flame blade: tapered, pointed, with an engraved vein; optional outward flick at the tip."""
    pts = bezier(p0, c1, c2, tip, 60)
    if curl:
        (xa, ya), (xb, yb) = pts[-4], pts[-1]
        a = math.atan2(yb - ya, xb - xa) + curl
        pts += bezier(tip, (tip[0] + 1.6 * math.cos(a), tip[1] + 1.6 * math.sin(a)),
                      (tip[0] + 3.2 * math.cos(a + curl * .6), tip[1] + 3.2 * math.sin(a + curl * .6)),
                      (tip[0] + 4.2 * math.cos(a + curl * 1.2), tip[1] + 4.2 * math.sin(a + curl * 1.2)), 20)[1:]
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        xa, ya = pts[max(i - 1, 0)]; xb, yb = pts[min(i + 1, n - 1)]
        L = math.hypot(xb - xa, yb - ya) or 1
        nx, ny = -(yb - ya) / L, (xb - xa) / L
        t = i / (n - 1)
        w = w0 * (1 - t) ** .8 * (1 + .25 * math.sin(t * math.pi))      # swelling then tapering to a point
        left.append((x + nx * w / 2, y + ny * w / 2)); right.append((x - nx * w / 2, y - ny * w / 2))
    g = Polygon(left + right[::-1]).buffer(0)
    vein = LineString(pts[int(n * .2):int(n * .62)]).buffer(.14)
    return g.difference(vein) if g.area > 2 else g


def wing():
    """Left flame wing (mirrored for the right): S-curved tongues rising from staggered roots."""
    b = [
        blade((38.4, 60.2), (29.5, 60.5), (30.5, 44.0), (15.5, 33.5), 4.3),   # outer, tallest
        blade((36.8, 55.4), (29.5, 54.2), (31.5, 44.2), (22.0, 36.6), 3.4),
        blade((35.8, 50.6), (31.5, 49.2), (33.2, 43.2), (28.2, 38.4), 2.5),   # inner, short
        blade((38.8, 61.8), (33.4, 63.4), (27.5, 63.4), (23.0, 60.0), 2.7),   # tail tongue licking up
        blade((39.6, 63.2), (37.2, 67.4), (33.2, 69.6), (28.2, 68.8), 2.2),
    ]
    return unary_union(b)


def panel():
    P = plate()
    g = [outline(inset(P, 1.8), .5)]
    # rules either side of the subtitle, five stars
    g += [star((CX + dx, 27.2), 1.35) for dx in (-7, -3.5, 0, 3.5, 7)]
    # shield + crown + wings
    sh, shp = shield(CX, 37.6, 11.6, 13.6)
    g.append(sh)
    cr, _ = crown(CX, 34.2, 6.4, 3.0)
    g.append(cr)
    wl = wing()
    g += [wl, affinity.scale(wl, xfact=-1, origin=(CX, 0))]
    # faint circle marks (as on the reference)
    ring_path = inset(P, 5.6).exterior
    for y in (27,):
        hit = ring_path.intersection(LineString([(-5, y), (W + 5, y)]))
        for p in getattr(hit, "geoms", [hit]):
            g.append(Point(p).buffer(1.6).difference(Point(p).buffer(1.3)))
    geo = unary_union(g).intersection(inset(P, .4))
    t1, _ = text(SERIF_KR, "CHAMPION", 5.4, CX, 16.4, 1.0)
    t2, w2 = text(SANS, "ROYAL GOLD", 2.4, CX, 22.2, .8)
    # rules either side of the subtitle, sized from its width
    rules = unary_union([box(CX - w2 / 2 - 12, 21.0, CX - w2 / 2 - 2, 21.25),
                         box(CX + w2 / 2 + 2, 21.0, CX + w2 / 2 + 12, 21.25)])
    geo = unary_union([geo, rules])
    mono, _ = text(SERIF_KR, "C", 4.7, CX, 47.0)
    return geo, t1 + t2 + mono, P


if __name__ == "__main__":
    import cairosvg, pymupdf
    geo, tx, P = panel()
    line = svg(W, H, f'<path d="{d_of(geo)}"/>{tx}<path d="{d_of(P)}" {CUT}/>')
    (OUT / "head4_top_layout.svg").write_text(line)
    pdf = OUT / "tmp.pdf"
    cairosvg.svg2pdf(bytestring=line.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf); d.set_metadata({"title": "CHAMPION park golf head v4 top layout"})
    d.save(OUT / "head4_top_layout.ai", garbage=3, deflate=True); pdf.unlink()
    gold = svg(W, H, GOLD + f'<path d="{d_of(P)}" fill="url(#g)"/>'
               f'<g fill="#6b4d1a" filter="url(#eng)"><path d="{d_of(geo)}"/>{tx}</g>', 3)
    (OUT / "head4_top_gold.svg").write_text(gold)
    cairosvg.svg2png(bytestring=gold.encode(), write_to=str(OUT / "head4_top_gold.png"), output_width=1800)
    cairosvg.svg2png(bytestring=line.encode(), write_to=str(OUT / "head4_top_layout.png"), output_width=1800,
                     background_color="white")
    print("ok")
