"""ParkNara (파크나라) brand marks shared by the CHAMPION head / plate designs.

crown_mark : the reference crown (diamond centre, teardrop finials) slightly modified -
             a star finial on the centre point (champion), inner jewel in the diamond, dotted band.
pn_symbol  : hole-green symbol built from the maker's "IS" - the I is the flag pin standing
             in the hole, the S is the fairway winding up to the green, inside a ring.
Running this file writes the ParkNara logo sheet (SVG / AI / PNG) into parknara/.
"""
import math
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from shaft import bezier, d_of, ribbon, star
from head_art import outline
from head2_art import text, SERIF_KR

OUT = Path(__file__).parent / "parknara"
SANS = ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 0)
SERIF_KR_B = SERIF_KR


def teardrop(tip, base, r):
    """Teardrop pointing at `tip`, round end of radius r centred at `base`."""
    ang = math.atan2(tip[1] - base[1], tip[0] - base[0])
    L = math.dist(tip, base)
    pts = [(L, 0)]
    for i in range(1, 40):
        a = math.pi / 2 + math.pi * i / 40
        pts.append((r * math.cos(a) * 1.0, r * math.sin(a)))
    body = Polygon([(L, 0)] + [(r * math.cos(a), r * math.sin(a)) for a in
                               [math.pi * .45 + math.pi * 1.1 * i / 40 for i in range(41)]])
    body = unary_union([body, Point(0, 0).buffer(r)])
    body = affinity.rotate(body, ang, origin=(0, 0), use_radians=True)
    return affinity.translate(body, *base)


def crown_mark(cx, top, w):
    """Crown of width w whose top (star finial tip) is at y=top. Returns (geometry, height)."""
    s = w  # unit scale
    P = lambda x, y: (cx + (x - .5) * s, top + y * s)
    # body silhouette with concave shoulders
    left = bezier(P(.13, .70), P(.07, .56), P(.03, .42), P(.02, .30), 20)
    shoulder_l = bezier(P(.02, .30), P(.14, .40), P(.27, .44), P(.33, .48), 20)
    rise_l = bezier(P(.33, .48), P(.40, .38), P(.46, .26), P(.50, .14), 20)
    pts = left + shoulder_l[1:] + rise_l[1:]
    pts += [(2 * cx - x, y) for x, y in reversed(pts[:-1])]
    body = Polygon(pts).buffer(0)
    # side triangles (lower flanks) as in the reference
    tri_l = Polygon([P(.10, .66), P(.17, .52), P(.24, .66)])
    tri_r = affinity.scale(tri_l, xfact=-1, origin=(cx, 0))
    # diamond with an inner jewel
    dia = Polygon([P(.5, .33), P(.585, .50), P(.5, .67), P(.415, .50)])
    jewel = Polygon([P(.5, .415), P(.54, .50), P(.5, .585), P(.46, .50)])
    body = body.difference(dia.buffer(.018 * s)).union(jewel).difference(tri_l.buffer(-.004 * s)).union(outline(tri_l, .02 * s))
    body = body.difference(tri_r.buffer(-.004 * s)).union(outline(tri_r, .02 * s))
    # band: gentle arc with three dots
    band_top = bezier(P(.10, .74), P(.30, .79), P(.70, .79), P(.90, .74), 30)
    band_bot = bezier(P(.90, .84), P(.70, .89), P(.30, .89), P(.10, .84), 30)
    band = Polygon(band_top + band_bot)
    dots = unary_union([Point(P(x, .815 + (.02 if x == .5 else .012))).buffer(.018 * s) for x in (.3, .5, .7)])
    band = band.difference(dots)
    # finials: teardrops on the side tips, a star on the centre tip
    fin_l = teardrop(P(-.05, .13), P(.005, .245), .032 * s)
    fin_r = affinity.scale(fin_l, xfact=-1, origin=(cx, 0))
    st = star(P(.5, .06), .075 * s, .45)
    g = unary_union([body, band, fin_l, fin_r, st])
    return g, .89 * s


def pn_symbol(cx, cy, r):
    """ParkNara hole-green symbol: ring, S fairway, I flag pin in the hole."""
    ring = outline(Point(cx, cy).buffer(r, quad_segs=64), r * .085)
    inner = Point(cx, cy).buffer(r * .83, quad_segs=64)
    P = lambda x, y: (cx + x * r, cy + y * r)
    # S fairway: a clean, even-width "S" rising from the tee (bottom-left) into the green (top)
    seg1 = bezier(P(-.50, .56), P(.48, .74), P(.52, .10), P(.0, .08), 50)
    seg2 = bezier(P(.0, .08), P(-.52, .06), P(-.46, -.44), P(.10, -.40), 50)
    fair = ribbon(seg1 + seg2[1:], r * .19, r * .19)
    green = affinity.scale(Point(P(.22, -.40)).buffer(r * .2, quad_segs=32), 1.45, .6)
    hole = affinity.scale(Point(P(.30, -.40)).buffer(r * .055, quad_segs=16), 1.4, .7)
    pin = box(P(.285, -.80)[0], P(.285, -.80)[1], P(.33, -.41)[0], P(.33, -.41)[1])   # the "I"
    flag = Polygon([P(.33, -.80), P(.60, -.69), P(.33, -.58)])
    ball = Point(P(-.47, .56)).buffer(r * .075, quad_segs=16)
    course = unary_union([fair, green]).intersection(inner).difference(hole).difference(ball.buffer(r * .045))
    g = unary_union([ring, course, pin, flag, ball])
    return g


def lockups():
    """Logo sheet: stacked lockup, horizontal lockup, symbol only (mono + gold)."""
    OUT.mkdir(exist_ok=True)
    parts = []
    # stacked: crown / symbol / 파크나라 / PARK NARA
    cr, ch = crown_mark(50, 6, 26)
    sym = pn_symbol(50, 6 + ch + 16, 14.5)
    t_kr, _ = text(SERIF_KR_B, "파크나라", 7.2, 50, 6 + ch + 16 + 14.5 + 12.5, .8)
    t_en, _ = text(SANS, "PARK NARA", 3.2, 50, 6 + ch + 16 + 14.5 + 19.5, 1.6)
    stacked = (unary_union([cr, sym]), t_kr + t_en)
    # horizontal: symbol with small crown | 파크나라 over PARK NARA · PARK GOLF
    cr2, ch2 = crown_mark(140, 22, 15)
    sym2 = pn_symbol(140, 22 + ch2 + 11.5, 10)
    t2a, w2a = text(SERIF_KR_B, "파크나라", 9.5, 187, 51, 1.0)
    t2b, _ = text(SANS, "PARK NARA", 3.1, 187, 59, 2.4)
    rule = unary_union([box(158, 62.2, 216, 62.45)])
    t2c, _ = text(SANS, "PREMIUM PARK GOLF", 2.2, 187, 67, 1.2)
    horiz = (unary_union([cr2, sym2, rule]), t2a + t2b + t2c)
    return stacked, horiz


GOLD = ('<defs><linearGradient id="g" x1="0" y1="0" x2=".3" y2="1">'
        '<stop offset="0" stop-color="#f6e3a8"/><stop offset=".45" stop-color="#d4ae5a"/>'
        '<stop offset=".62" stop-color="#b18a3a"/><stop offset="1" stop-color="#ecd29a"/></linearGradient></defs>')


if __name__ == "__main__":
    import cairosvg, pymupdf
    (sg, st), (hg, ht) = lockups()
    W, H = 240, 100
    mono = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="#fff"/><g fill="#111"><path d="{d_of(sg)}"/>{st}'
            f'<path d="{d_of(hg)}"/>{ht}</g></svg>')
    gold = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">{GOLD}'
            f'<rect width="{W}" height="{H}" fill="#101010"/><g fill="url(#g)"><path d="{d_of(sg)}"/>{st}'
            f'<path d="{d_of(hg)}"/>{ht}</g></svg>')
    (OUT / "parknara_logo.svg").write_text(mono)
    (OUT / "parknara_logo_gold.svg").write_text(gold)
    cairosvg.svg2png(bytestring=mono.encode(), write_to=str(OUT / "parknara_logo.png"), output_width=2400)
    cairosvg.svg2png(bytestring=gold.encode(), write_to=str(OUT / "parknara_logo_gold.png"), output_width=2400)
    pdf = OUT / "tmp.pdf"
    cairosvg.svg2pdf(bytestring=mono.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf); d.set_metadata({"title": "ParkNara logo"}); d.save(OUT / "parknara_logo.ai", garbage=3, deflate=True)
    pdf.unlink()
    print("ok")
