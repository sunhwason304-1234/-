"""CHAMPION sole copper plate - version C, following the client memo literally.

  sole (upper 40 mm) : reference "A" wreath with the doves removed - a classic laurel wreath
                       tied with a ribbon bow - crown and PARK NARA in the centre.
  back (lower 40 mm) : the client's tribal emblem split in half as left/right borders,
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
from head5_art import laurel_leaf
from parknara import crown_mark
from trace_tribal import emblem
from ornament_trace import without_dove
from sole_plate import plate, inset, flower, scroll, divider, W, H, FOLD, CX, SANS, CUT, FOLD_LINE, GOLD, svg

OUT = Path(__file__).parent / "sole_plate_c"
OUT.mkdir(exist_ok=True)
C = (CX, 19.4)          # wreath centre
RX, RY = 16.8, 15.6     # wreath ellipse


def on_ellipse(deg, dr=0.0):
    a = math.radians(deg)
    return (C[0] + (RX + dr) * math.cos(a), C[1] + (RY + dr) * math.sin(a))


def laurel_side():
    """Left laurel branch: from the bottom centre (bow) up the wreath ellipse to near the top centre."""
    pts = [on_ellipse(100 + (256 - 100) * i / 90, 0.0) for i in range(91)]
    parts = [ribbon(pts, .8, .3)]
    n = 12
    for k in range(n):
        t = .05 + .9 * k / (n - 1)
        i = int(t * 90)
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        a = math.atan2(yb - ya, xb - xa)
        L = 5.4 - 1.8 * t                                 # leaves get smaller towards the top
        parts.append(laurel_leaf(pts[i], a + .7, L, L * .42))            # outer leaf
        parts.append(laurel_leaf(pts[i], a - .62, L * .84, L * .38))     # inner leaf
        if k in (2, 5, 8):
            c = (pts[i][0] + math.cos(a - 1.3) * 1.9, pts[i][1] + math.sin(a - 1.3) * 1.9)
            parts.append(Point(c).buffer(.55, quad_segs=12))
    (xa, ya), (xb, yb) = pts[-3], pts[-1]
    parts.append(laurel_leaf(pts[-1], math.atan2(yb - ya, xb - xa), 3.4, 1.35))
    return unary_union(parts)


def bow(cx, cy):
    """Small ribbon bow tying the two branches at the bottom centre."""
    parts = [Point(cx, cy).buffer(.9, quad_segs=12)]
    for sgn in (-1, 1):
        loop = Polygon([(cx, cy)] + [(cx + sgn * 3.0 * math.sin(math.pi * t), cy - 1.05 * math.sin(2 * math.pi * t) - .3 * math.sin(math.pi * t))
                                     for t in [i / 30 for i in range(31)]]).buffer(.3)
        parts.append(outline(loop, .5))
        parts.append(ribbon(bezier((cx + sgn * .5, cy + .5), (cx + sgn * 1.5, cy + 2.0), (cx + sgn * 2.0, cy + 2.8), (cx + sgn * 3.2, cy + 3.6), 20), 1.0, .45))
    return unary_union(parts)


def wreath_half():
    return laurel_side()


def tribal_half(height):
    """Right half of the client's tribal emblem (traced), cut edge on the left, scaled to `height` mm."""
    half = emblem().intersection(box(0, -1, 1, 2))
    return affinity.scale(half, height, height, origin=(0, 0))


def panel():
    P = plate()
    body = inset(P, 2.4)
    g = [outline(inset(P, 1.3), .45), outline(body, .16)]
    # client's ornament (dove removed): feathers rising on the outside, scroll + flower towards the centre
    orn = without_dove()
    ox0, oy0, ox1, oy1 = orn.bounds
    k = 33.0 / (oy1 - oy0)
    left_orn = affinity.translate(affinity.scale(orn, k, k, origin=(ox0, oy0)), CX - 5.0 - (ox1 - ox0) * k - ox0, 4.0 - oy0)
    wreath = unary_union([left_orn, affinity.scale(left_orn, xfact=-1, origin=(CX, 0))])
    g.append(wreath)
    # centre: crown + PARK NARA
    cr, ch = crown_mark(CX, 7.6, 12.4)
    g.append(cr)
    g.append(box(CX - 6.0, 21.7, CX - 1.4, 21.9)); g.append(box(CX + 1.4, 21.7, CX + 6.0, 21.9))
    g.append(Polygon([(CX, 20.9), (CX + .8, 21.8), (CX, 22.7), (CX - .8, 21.8)]))
    # back: bar ornament under the fold, tribal half borders, lettering
    g.append(divider(44.0, 14))
    # bend the flame so its outer edge follows the curved plate border
    border = inset(P, 3.0).exterior
    def bx(y):
        hit = border.intersection(LineString([(0, y), (CX, y)]))
        return min(p.x for p in getattr(hit, "geoms", [hit]))
    base = affinity.translate(tribal_half(23.5), .8, 47.6)
    left = transform(lambda x, y, z=None: (x + bx(y), y), base)
    right = affinity.scale(left, xfact=-1, origin=(CX, 0))
    g.append(unary_union([left, right]))
    g += [star((CX + dx, 63.8), 1.25) for dx in (-6.8, -3.4, 0, 3.4, 6.8)]
    g += [box(CX - 13.2, 69.7, CX - 8.2, 69.9), box(CX + 8.2, 69.7, CX + 13.2, 69.9)]
    geo = unary_union(g).intersection(inset(P, .3))
    t0, _ = text(SANS, "PARK NARA", 1.5, CX, 25.4, .55)
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
