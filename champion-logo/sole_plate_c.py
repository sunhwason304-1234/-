"""CHAMPION sole copper plate - version C, following the client memo literally.

  sole (upper 40 mm) : reference "A" wreath with the doves removed - ribbed feather wings on the
                       outer sides, scrolls + flowers top and bottom - crown and PARK NARA in the centre.
  back (lower 40 mm) : Honma-style vertical tribal flames as left/right borders (second reference),
                       lettering in the middle: CHAMPION / MADE IN KOREA / five stars / small PREMIUM.
"""
import math
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import transform, unary_union

from shaft import bezier, d_of, leaf, ribbon, spiral, star
from head_art import outline
from head2_art import text, SERIF_KR
from head4_art import blade
from parknara import crown_mark
from sole_plate import plate, inset, flower, scroll, divider, W, H, FOLD, CX, SANS, CUT, FOLD_LINE, GOLD, svg

OUT = Path(__file__).parent / "sole_plate_c"
OUT.mkdir(exist_ok=True)
C = (CX, 20.0)          # wreath centre
RX, RY = 17.5, 16.8     # wreath ellipse


def on_ellipse(deg, dr=0.0):
    a = math.radians(deg)
    return (C[0] + (RX + dr) * math.cos(a), C[1] + (RY + dr) * math.sin(a))


def ribbed_wing():
    """Left ribbed wing: stacked curved blades rising along the outside of the wreath (A reference)."""
    parts = []
    n = 7
    for k in range(n):
        t = k / (n - 1)
        deg = 142 + 76 * t                      # 142 (lower-left) -> 218 (upper-left), y-down
        root = on_ellipse(deg, -1.2)
        a = math.radians(deg)
        out = (math.cos(a), math.sin(a) * RY / RX)
        up = (0.0, -1.0)
        L = 6.2 + 3.4 * math.sin(math.pi * t)
        d = (out[0] * .78 + up[0] * .62, out[1] * .78 + up[1] * .62)
        m = math.hypot(*d); d = (d[0] / m, d[1] / m)
        tip = (root[0] + d[0] * L, root[1] + d[1] * L)
        nx, ny = -d[1], d[0]
        c1 = (root[0] + d[0] * L * .35 - nx * 1.0, root[1] + d[1] * L * .35 - ny * 1.0)
        c2 = (root[0] + d[0] * L * .75 - nx * 1.6, root[1] + d[1] * L * .75 - ny * 1.6)
        parts.append(blade(root, c1, c2, tip, 2.3 - .4 * abs(t - .5)))
    return unary_union(parts)


def wreath_half():
    cx, cy = C
    parts = [ribbed_wing()]
    # top: scroll sweeping from the top centre outward and down into a curl, flower above it
    _, g = scroll((cx - 3.2, 4.8), (cx - 8.5, 3.6), (cx - 14.2, 5.2), (cx - 14.6, 9.6), (cx - 12.4, 9.5), 1.1, False, 1.0, .24)
    parts.append(g)
    parts.append(flower((cx - 8.2, 7.0), 1.9))
    for p, ang in [((cx - 6.0, 3.6), -2.8), ((cx - 11.0, 3.8), -2.45), ((cx - 14.2, 6.6), 3.3)]:
        parts.append(leaf(p, ang, 2.5, .95))
    # bottom: mirror-image scroll curling up, flower below it
    _, g = scroll((cx - 3.2, 35.8), (cx - 8.5, 37.4), (cx - 14.2, 35.4), (cx - 14.6, 30.6), (cx - 12.4, 30.5), 1.1, True, 1.0, .24)
    parts.append(g)
    parts.append(flower((cx - 8.2, 33.0), 1.9))
    for p, ang in [((cx - 6.0, 36.4), 2.8), ((cx - 11.0, 36.2), 2.45), ((cx - 14.2, 33.4), -3.3)]:
        parts.append(leaf(p, ang, 2.5, .95))
    return unary_union(parts)


def tribal():
    """Vertical tribal flame (second reference): slim lens with sharp top and a long tail,
    an oval eye and a crescent hook cut out. Flat side on the LEFT (outer). Local y 0..30."""
    outer_edge = bezier((1.4, 0), (0.2, 9), (0.0, 19), (3.4, 30), 50)
    inner_edge = bezier((3.4, 30), (4.2, 25.5), (6.4, 17), (1.4, 0), 50)
    body = Polygon(outer_edge + inner_edge[1:]).buffer(0)
    eye = affinity.rotate(affinity.scale(Point(2.6, 9.0).buffer(.85, quad_segs=24), 1.0, 4.0), -10, origin=(2.6, 9.0))
    ring = Point(2.9, 17.4).buffer(2.0, quad_segs=32).difference(Point(3.5, 17.0).buffer(1.35, quad_segs=32))
    hook = ring.intersection(box(0, 15.2, 8, 21))
    body = body.difference(eye).difference(hook)
    flick = blade((3.9, 21.5), (5.0, 23.8), (5.4, 26.2), (5.3, 28.8), .9)
    return unary_union([body, flick])


def panel():
    P = plate()
    body = inset(P, 2.4)
    g = [outline(inset(P, 1.3), .45), outline(body, .16)]
    wh = wreath_half()
    wreath = unary_union([wh, affinity.scale(wh, xfact=-1, origin=(CX, 0))])
    g.append(wreath)
    # centre: crown + PARK NARA
    cr, ch = crown_mark(CX, 9.0, 14.0)
    g.append(cr)
    g.append(box(CX - 7.0, 24.6, CX - 1.6, 24.8)); g.append(box(CX + 1.6, 24.6, CX + 7.0, 24.8))
    g.append(Polygon([(CX, 23.7), (CX + .9, 24.7), (CX, 25.7), (CX - .9, 24.7)]))
    # fine sunburst behind the wreath (outside it only)
    rays = [LineString([(C[0] + 21 * math.cos(math.radians(a)), C[1] + 21 * math.sin(math.radians(a))),
                        (C[0] + 70 * math.cos(math.radians(a)), C[1] + 70 * math.sin(math.radians(a)))]).buffer(.07)
            for a in range(0, 360, 4)]
    g.append(unary_union(rays).intersection(body.buffer(-.9)).intersection(box(0, 0, W, FOLD - 3.0)).difference(wreath.buffer(1.0)))
    # back: bar ornament under the fold, tribal borders, lettering
    g.append(divider(44.0, 14))
    t = tribal()
    # bend the flame so its outer edge follows the curved plate border
    border = inset(P, 3.0).exterior
    def bx(y):
        hit = border.intersection(LineString([(0, y), (CX, y)]))
        return min(p.x for p in getattr(hit, "geoms", [hit]))
    base = affinity.translate(affinity.scale(t, 1.2, .86, origin=(0, 0)), 0.9, 45.6)
    left = transform(lambda x, y, z=None: (x + bx(y), y), base)
    right = affinity.scale(left, xfact=-1, origin=(CX, 0))
    g.append(unary_union([left, right]))
    g += [star((CX + dx, 63.8), 1.25) for dx in (-6.8, -3.4, 0, 3.4, 6.8)]
    g += [box(CX - 13.2, 69.7, CX - 8.2, 69.9), box(CX + 8.2, 69.7, CX + 13.2, 69.9)]
    geo = unary_union(g).intersection(inset(P, .3))
    t0, _ = text(SANS, "PARK NARA", 1.7, CX, 29.0, .7)
    t1, _ = text(SERIF_KR, "CHAMPION", 5.2, CX, 54.4, .9)
    t2, _ = text(SANS, "MADE IN KOREA", 1.9, CX, 59.2, .9)
    t3, _ = text(SANS, "PREMIUM", 1.5, CX, 70.5, 1.1)
    return geo, t0 + t1 + t2 + t3, P


if __name__ == "__main__":
    import cairosvg, pymupdf
    geo, tx, P = panel()
    line = svg(f'<path d="{d_of(geo)}"/>{tx}<path d="{d_of(P)}" {CUT}/>{FOLD_LINE}')
    (OUT / "sole_plate_c_layout.svg").write_text(line)
    pdf = OUT / "tmp.pdf"
    cairosvg.svg2pdf(bytestring=line.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf); d.set_metadata({"title": "CHAMPION sole plate C 95-75-30 x 80"})
    d.save(OUT / "sole_plate_c_layout.ai", garbage=3, deflate=True); pdf.unlink()
    lower = P.intersection(box(-1, FOLD, W + 1, H + 2))
    gsvg = svg(GOLD + f'<path d="{d_of(P)}" fill="url(#g)"/><path d="{d_of(lower)}" fill="url(#g2)" opacity=".5"/>'
               f'<g fill="#6b4d1a" filter="url(#eng)"><path d="{d_of(geo)}"/>{tx}</g>')
    (OUT / "sole_plate_c_gold.svg").write_text(gsvg)
    cairosvg.svg2png(bytestring=gsvg.encode(), write_to=str(OUT / "sole_plate_c_gold.png"), output_width=2000)
    cairosvg.svg2png(bytestring=line.encode(), write_to=str(OUT / "sole_plate_c_layout.png"), output_width=2000,
                     background_color="white")
    print("ok")
