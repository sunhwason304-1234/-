"""CHAMPION sole copper plate - version E: client's head revision sheet applied to version D.

Client notes (head revision xlsx):
  * Head B has a narrow, pointed lower end with screw heads fixing the plate, so the lower
    pattern must be narrower; design the lower part as if the 30 mm bottom were only 10 mm,
    so one plate suits several head models.
  * Upper: widen the feather/laurel ornament (by up to 10 mm), put CHAMPION under the crown
    at 50 % of its previous size; the replaced six-petal flower 20 % smaller.
  * Lower: five stars, then PARK NARA (the maker), then MADE IN KOREA with condensed letters;
    the side patterns at least 15 mm in from the outer wall.
The cut outline stays 95 / 75 / 30 x 40 + 40; a "B-head guide" (bottom 10 mm, 15 mm in from the
walls) is drawn on the layout as a non-printing reference.
"""
import math
from pathlib import Path

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import transform, unary_union

from shaft import bezier, d_of, star
from head_art import outline
from head2_art import text, SERIF_KR
from parknara import crown_mark
from trace_tribal import trace
from ornament_trace import without_dove
from flower6 import flower as flower6
from sole_plate import plate, inset, W, H, FOLD, CX, SANS, CUT, FOLD_LINE, GOLD, svg

OUT = Path(__file__).parent / "sole_plate_e"
OUT.mkdir(exist_ok=True)
CROWN_TOP = 6.6
WIDEN = 4.0          # each wing moves out 4 mm -> ornament 8 mm wider (memo: within 10 mm)


def wing_left():
    """Client ornament (dove removed), six-petal flower 20 % smaller than in version D."""
    orn = without_dove()
    parts = list(getattr(orn, "geoms", [orn]))
    flowers = [p for p in parts if math.dist((p.centroid.x, p.centroid.y), (163, 303)) < 25]
    keep = unary_union([p for p in parts if not any(p is f for f in flowers)])
    fb = unary_union(flowers).bounds
    fc = ((fb[0] + fb[2]) / 2 + 4, (fb[1] + fb[3]) / 2 + 5)
    fr = max(fb[2] - fb[0], fb[3] - fb[1]) / 2 * 1.18 * .8
    f6 = affinity.scale(flower6(stroke=9.5), fr / 47, fr / 47, origin=(0, 0))
    g = unary_union([keep, affinity.translate(f6, *fc)])
    x0, y0, x1, y1 = g.bounds
    k = 31.0 / (y1 - y0)
    g = affinity.scale(g, k, k, origin=(x0, y0))
    return affinity.translate(g, CX - 6.8 - WIDEN - (x1 - x0) * k - x0, CROWN_TOP - y0)


def guide_left():
    """Left side of the B-head design area: 15 mm in from the wall at the fold,
    closing to a 10 mm wide bottom (x 42.5) at the lower edge."""
    return bezier((25.0, FOLD + .5), (24.6, 56.0), (31.5, 71.5), (42.5, 77.6), 80)


def guide_shape():
    left = guide_left()
    right = [(W - x, y) for x, y in reversed(left)]
    return Polygon(left + right)


def tribal_on(path, width):
    """Long tribal (client reference) bent along `path` (top -> bottom), flat side on the path."""
    t = trace("ref/tribal_long_ref.png")
    x0, y0, x1, y1 = t.bounds
    t = affinity.translate(affinity.scale(t, -1, 1, origin=(x1, 0)), -x1, -y0)
    L = path.length
    t = affinity.scale(t, width / (x1 - x0), L / (y1 - y0), origin=(0, 0))

    def warp(x, y, z=None):
        ox, oy, nx, ny = [], [], [], []
        for s in np.atleast_1d(y):
            p = path.interpolate(float(s)); q = path.interpolate(float(s) + .3)
            tx, ty = q.x - p.x, q.y - p.y
            n = math.hypot(tx, ty) or 1
            mx, my = ty / n, -tx / n
            if mx * (CX - p.x) + my * (60 - p.y) < 0:
                mx, my = -mx, -my
            ox.append(p.x); oy.append(p.y); nx.append(mx); ny.append(my)
        ox, oy, nx, ny = map(np.array, (ox, oy, nx, ny))
        return ox + nx * np.asarray(x), oy + ny * np.asarray(x)

    return transform(warp, t.segmentize(.4)).buffer(0)


def condensed(svg_text, cx, k):
    return f'<g transform="translate({cx:.3f},0) scale({k},1) translate({-cx:.3f},0)">{svg_text}</g>'


def panel():
    P = plate()
    body = inset(P, 2.4)
    g = [outline(inset(P, 1.3), .45), outline(body, .16)]
    wl = wing_left()
    g += [wl, affinity.scale(wl, xfact=-1, origin=(CX, 0))]
    cr, ch = crown_mark(CX, CROWN_TOP, 17.6)
    g.append(cr)
    # small divider under CHAMPION
    g += [box(CX - 6.4, 28.9, CX - 1.4, 29.08), box(CX + 1.4, 28.9, CX + 6.4, 29.08),
          Polygon([(CX, 28.2), (CX + .75, 29.0), (CX, 29.8), (CX - .75, 29.0)])]
    # lower: tribal along the B-head guide (15 mm in, bottom 10 mm)
    path = LineString(guide_left()[2:-6])
    tl = tribal_on(path, 4.6)
    g += [tl, affinity.scale(tl, xfact=-1, origin=(CX, 0))]
    g += [star((CX + dx, 52.0), 1.15) for dx in (-6.0, -3.0, 0, 3.0, 6.0)]
    geo = unary_union(g).intersection(inset(P, .3))
    t_ch, _ = text(SERIF_KR, "CHAMPION", 2.6, CX, 26.7, .5)                 # 50 % of the previous 5.2 mm
    t_pn, _ = text(SANS, "PARK NARA", 2.3, CX, 58.2, .55)
    t_mk, _ = text(SANS, "MADE IN KOREA", 1.7, CX, 62.2, .35)
    return geo, t_ch + t_pn + condensed(t_mk, CX, .78), P


GUIDE = 'fill="none" stroke="#00A0E0" stroke-width=".18" stroke-dasharray=".6 .6" opacity=".8"'


if __name__ == "__main__":
    import cairosvg, pymupdf
    from PIL import Image
    geo, tx, P = panel()
    geo = geo.simplify(.03)
    gs = guide_shape()
    line = svg(f'<path d="{d_of(geo)}" fill-rule="evenodd"/>{tx}<path d="{d_of(P)}" {CUT}/>{FOLD_LINE}')
    line_guide = line.replace('</svg>', f'<path d="{d_of(gs)}" {GUIDE}/></svg>')
    (OUT / "sole_plate_e_layout.svg").write_text(line)
    (OUT / "sole_plate_e_layout_guide.svg").write_text(line_guide)
    cairosvg.svg2pdf(bytestring=line.encode(), write_to=str(OUT / "CHAMPION_동판하부_E_도면.pdf"))
    d = pymupdf.open(OUT / "CHAMPION_동판하부_E_도면.pdf"); d.set_metadata({"title": "CHAMPION sole plate E"})
    d.save(OUT / "sole_plate_e_layout.ai", garbage=4, deflate=True, clean=True)
    lower = P.intersection(box(-1, FOLD, W + 1, H + 2))
    gsvg = svg(GOLD + f'<path d="{d_of(P)}" fill="url(#g)"/><path d="{d_of(lower)}" fill="url(#g2)" opacity=".5"/>'
               f'<g fill="#6b4d1a" filter="url(#eng)" fill-rule="evenodd"><path d="{d_of(geo)}"/>{tx}</g>')
    (OUT / "sole_plate_e_gold.svg").write_text(gsvg)
    cairosvg.svg2png(bytestring=gsvg.encode(), write_to=str(OUT / "sole_plate_e_gold.png"), output_width=2000)
    cairosvg.svg2png(bytestring=line_guide.encode(), write_to=str(OUT / "sole_plate_e_layout.png"), output_width=2000,
                     background_color="white")
    print("ok")
