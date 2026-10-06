"""CHAMPION sole copper plate - version D: client revision notes applied to version C.

  sole : crown a little larger; feather wings with their tips level with the crown top;
         ornament flower replaced by the six-petal flower; PARK NARA moved down.
  back : divider bar and PREMIUM removed; CHAMPION moved up, then five stars, then MADE IN KOREA;
         the long tribal (client reference) stretched along the curved border on both sides.
"""
import math
from pathlib import Path

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import transform, unary_union

from shaft import d_of, star
from head_art import outline
from head2_art import text, SERIF_KR
from parknara import crown_mark
from trace_tribal import trace
from ornament_trace import without_dove
from flower6 import flower as flower6
from sole_plate import plate, inset, W, H, FOLD, CX, SANS, CUT, FOLD_LINE, GOLD, svg

OUT = Path(__file__).parent / "sole_plate_d"
OUT.mkdir(exist_ok=True)
CROWN_TOP = 6.6


def wing_left():
    """Client ornament (dove removed) with its round flower swapped for the six-petal flower."""
    orn = without_dove()
    parts = list(getattr(orn, "geoms", [orn]))
    flowers = [p for p in parts if math.dist((p.centroid.x, p.centroid.y), (163, 303)) < 25]
    keep = unary_union([p for p in parts if not any(p is f for f in flowers)])
    fb = unary_union(flowers).bounds
    fc = ((fb[0] + fb[2]) / 2 + 6, (fb[1] + fb[3]) / 2 + 7)   # nudged off the lowest feather
    fr = max(fb[2] - fb[0], fb[3] - fb[1]) / 2 * 1.18
    f6 = affinity.scale(flower6(stroke=8.5), fr / 47, fr / 47, origin=(0, 0))
    g = unary_union([keep, affinity.translate(f6, *fc)])
    x0, y0, x1, y1 = g.bounds
    k = 31.0 / (y1 - y0)
    g = affinity.scale(g, k, k, origin=(x0, y0))
    return affinity.translate(g, CX - 6.8 - (x1 - x0) * k - x0, CROWN_TOP - y0)


def left_path(P, d):
    """Left inner border curve from just under the fold down towards the bottom, top -> bottom."""
    ring = LineString(inset(P, d).exterior.coords).segmentize(.5)
    pts = [p for p in ring.coords if p[0] < CX - 8.0 and p[1] > FOLD + 4.0]
    pts.sort(key=lambda p: ring.project(Point(p)))
    line = LineString(pts)
    if line.coords[0][1] > line.coords[-1][1]:
        line = LineString(list(line.coords)[::-1])
    return line


def tribal_along(P, d=4.8, width=6.4):
    """Long tribal (client reference) bent along the left border: flat side outwards."""
    t = trace("ref/tribal_long_ref.png")
    x0, y0, x1, y1 = t.bounds
    t = affinity.translate(affinity.scale(t, -1, 1, origin=(x1, 0)), -x1, -y0)   # mirror: flat side at x=0
    path = left_path(P, d)
    L = path.length * .99
    sx, sy = width / (x1 - x0), L / (y1 - y0)
    t = affinity.scale(t, sx, sy, origin=(0, 0))

    def warp(x, y, z=None):
        x = np.asarray(x); y = np.asarray(y)
        ox, oy, nx, ny = [], [], [], []
        for s in np.atleast_1d(y):
            p = path.interpolate(float(s)); q = path.interpolate(float(s) + .3)
            tx, ty = q.x - p.x, q.y - p.y
            n = math.hypot(tx, ty) or 1
            tx, ty = tx / n, ty / n
            mx, my = ty, -tx                                   # candidate normal
            if mx * (CX - p.x) + my * (60 - p.y) < 0:
                mx, my = -mx, -my                              # point it inwards
            ox.append(p.x); oy.append(p.y); nx.append(mx); ny.append(my)
        ox, oy, nx, ny = map(np.array, (ox, oy, nx, ny))
        return ox + nx * x, oy + ny * x

    t = t.segmentize(.4)
    return transform(warp, t).buffer(0)


def panel():
    P = plate()
    body = inset(P, 2.4)
    g = [outline(inset(P, 1.3), .45), outline(body, .16)]
    wl = wing_left()
    g += [wl, affinity.scale(wl, xfact=-1, origin=(CX, 0))]
    cr, ch = crown_mark(CX, CROWN_TOP, 17.6)
    g.append(cr)
    g += [box(CX - 6.4, 25.6, CX - 1.4, 25.8), box(CX + 1.4, 25.6, CX + 6.4, 25.8),
          Polygon([(CX, 24.8), (CX + .8, 25.7), (CX, 26.6), (CX - .8, 25.7)])]
    tl = tribal_along(P)
    g += [tl, affinity.scale(tl, xfact=-1, origin=(CX, 0))]
    g += [star((CX + dx, 56.6), 1.3) for dx in (-7.0, -3.5, 0, 3.5, 7.0)]
    geo = unary_union(g).intersection(inset(P, .3))
    t0, _ = text(SANS, "PARK NARA", 1.55, CX, 30.0, .55)
    t1, _ = text(SERIF_KR, "CHAMPION", 5.2, CX, 51.2, .9)
    t2, _ = text(SANS, "MADE IN KOREA", 1.9, CX, 63.4, .9)
    return geo, t0 + t1 + t2, P


if __name__ == "__main__":
    import cairosvg, pymupdf
    geo, tx, P = panel()
    line = svg(f'<path d="{d_of(geo)}" fill-rule="evenodd"/>{tx}<path d="{d_of(P)}" {CUT}/>{FOLD_LINE}')
    (OUT / "sole_plate_d_layout.svg").write_text(line)
    pdf = OUT / "tmp.pdf"
    cairosvg.svg2pdf(bytestring=line.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf); d.set_metadata({"title": "CHAMPION sole plate D 95-75-30 x 80"})
    d.save(OUT / "sole_plate_d_layout.ai", garbage=3, deflate=True); pdf.unlink()
    lower = P.intersection(box(-1, FOLD, W + 1, H + 2))
    gsvg = svg(GOLD + f'<path d="{d_of(P)}" fill="url(#g)"/><path d="{d_of(lower)}" fill="url(#g2)" opacity=".5"/>'
               f'<g fill="#6b4d1a" filter="url(#eng)" fill-rule="evenodd"><path d="{d_of(geo)}"/>{tx}</g>')
    (OUT / "sole_plate_d_gold.svg").write_text(gsvg)
    cairosvg.svg2png(bytestring=gsvg.encode(), write_to=str(OUT / "sole_plate_d_gold.png"), output_width=2000)
    cairosvg.svg2png(bytestring=line.encode(), write_to=str(OUT / "sole_plate_d_layout.png"), output_width=2000,
                     background_color="white")
    print("ok")
