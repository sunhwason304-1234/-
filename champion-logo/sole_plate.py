"""CHAMPION sole copper plate (동판 하부) - built to the client's hand drawing.

Drawing (flat plate, mm, y-down):  top edge 95 wide, fold line 40 down at 75 wide,
bottom edge 40 further down at 30 wide (total 80). Sides are convex curves.
The plate folds at the 75 line: the upper 40 mm lies on the sole, the lower 40 mm
bends up the back of the head ("모서리 부분 각접").

Design (from the client's memo sheet):
  upper (sole)  : the "A" ornament frame - scrolls, flowers and feather wings - with the doves
                  removed and the crown + ParkNara mark in the centre; fine sunburst behind it.
  lower (back)  : Honma-style tribal flame borders left & right, lettering in the middle:
                  CHAMPION / MADE IN KOREA / five stars / small PREMIUM.
"""
import math
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from shaft import bezier, d_of, leaf, ribbon, spiral, star
from head_art import outline
from head2_art import text, SERIF_KR
from head4_art import blade
from parknara import crown_mark, pn_symbol

OUT = Path(__file__).parent / "sole_plate"
OUT.mkdir(exist_ok=True)
W, H, FOLD = 95.0, 80.0, 40.0
CX = W / 2
SANS = ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 0)
EMB = (CX, 21.4)            # centre of the ornament frame on the sole section


def side_left():
    upper = bezier((0, 0), (-.6, 15), (2.5, 32), (10, FOLD), 50)
    lower = bezier((10, FOLD), (9.4, 60), (15.5, 79.6), (32.5, 80), 50)
    return upper + lower[1:]


def plate():
    left = side_left()                                   # (0,0) -> (32.5,80)
    right = [(W - x, y) for x, y in left]                # (95,0) -> (62.5,80)
    bottom = [(62.5, 80), (32.5, 80)]
    g = Polygon(right + bottom[1:-1] + list(reversed(left))).buffer(-1.6, join_style='round').buffer(1.6, join_style='round')
    return g.buffer(0)


def inset(g, d):
    return g.buffer(-d, join_style="round")


def flower(c, r):
    """Five-petal flower (outlined petals, solid centre ring)."""
    petals = []
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        p = affinity.scale(Point(0, 0).buffer(r * .52, quad_segs=16), 1.0, .78)
        p = affinity.translate(p, r * .55, 0)
        p = affinity.rotate(p, a, origin=(0, 0), use_radians=True)
        petals.append(affinity.translate(p, *c))
    body = unary_union(petals)
    return unary_union([outline(body, r * .12), Point(c).buffer(r * .3).difference(Point(c).buffer(r * .14))])


def scroll(p0, c1, c2, p3, curl_c, turns, cw, w0, w1):
    path = bezier(p0, c1, c2, p3, 40)
    path += spiral(curl_c, math.dist(path[-1], curl_c),
                   math.atan2(path[-1][1] - curl_c[1], path[-1][0] - curl_c[0]), turns, cw=cw, n=40)[1:]
    return path, ribbon(path, w0, w1)


def feather(base, d, L, w):
    """Long curved feather leaf: base point, unit direction d, length L, width w (with vein)."""
    nx, ny = -d[1], d[0]
    tip = (base[0] + d[0] * L + nx * L * .18, base[1] + d[1] * L + ny * L * .18)   # slight sweep
    mid = [(base[0] + d[0] * L * t + nx * L * .18 * t * t, base[1] + d[1] * L * t + ny * L * .18 * t * t)
           for t in [i / 40 for i in range(41)]]
    left, right = [], []
    for i, (x, y) in enumerate(mid):
        t = i / 40
        ww = w * (math.sin(math.pi * min(1, t * 1.08)) ** .7) * (1 - .35 * t) / 2
        left.append((x + nx * ww, y + ny * ww)); right.append((x - nx * ww, y - ny * ww))
    g = Polygon(left + right[::-1]).buffer(0)
    vein = LineString(mid[4:30]).buffer(.13)
    return g.difference(vein)


def plume(root, tip, bend, w):
    """Curved feather plume from root to tip, bowed sideways by `bend` (mm), with a vein."""
    mx, my = (root[0] + tip[0]) / 2, (root[1] + tip[1]) / 2
    dx, dy = tip[0] - root[0], tip[1] - root[1]
    L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    c1 = (root[0] + dx * .3 + nx * bend, root[1] + dy * .3 + ny * bend)
    c2 = (root[0] + dx * .72 + nx * bend * 1.2, root[1] + dy * .72 + ny * bend * 1.2)
    return blade(root, c1, c2, tip, w)


def feathers(cx, cy, *_):
    """Feather wing hugging the outside of the frame (left side), plumes sweeping up and out."""
    parts = []
    specs = [   # root, tip, bend, width
        ((cx - 15.2, cy + 9.6), (cx - 19.6, cy - 12.4), -2.2, 2.6),
        ((cx - 16.0, cy + 10.4), (cx - 23.6, cy - 8.6), -2.4, 2.6),
        ((cx - 16.8, cy + 11.0), (cx - 27.0, cy - 3.8), -2.4, 2.5),
        ((cx - 17.4, cy + 11.4), (cx - 29.4, cy + 1.8), -2.2, 2.3),
        ((cx - 17.8, cy + 11.8), (cx - 30.2, cy + 7.4), -1.8, 2.0),
    ]
    for root, tip, bend, w in specs:
        parts.append(plume(root, tip, bend, w))
    return unary_union(parts)


def frame_half():
    """Left half of the ornament frame (doves removed)."""
    cx, cy = EMB
    parts = []
    # top scroll: from the top centre outward, curling down, with a flower
    _, g = scroll((cx - 4.4, 5.4), (cx - 9.5, 4.4), (cx - 14.5, 6.0), (cx - 14.8, 10.2), (cx - 12.8, 10.4), 1.05, False, .8, .22)
    parts.append(g)
    parts.append(flower((cx - 9.0, 8.4), 2.0))
    for t_pt, ang in [((cx - 7.0, 4.9), -2.75), ((cx - 11.8, 5.1), -2.4)]:
        parts.append(leaf(t_pt, ang, 2.6, 1.0))
    # bottom scroll: from the bottom centre outward, curling up, with a flower
    _, g = scroll((cx - 4.0, 34.8), (cx - 9.5, 35.8), (cx - 14.6, 33.8), (cx - 14.8, 29.6), (cx - 12.8, 29.8), 1.05, True, .8, .22)
    parts.append(g)
    parts.append(flower((cx - 9.0, 31.8), 2.0))
    for t_pt, ang in [((cx - 6.8, 35.4), 2.8), ((cx - 11.8, 35.2), 2.35)]:
        parts.append(leaf(t_pt, ang, 2.6, 1.0))
    # feather wing sweeping up the outside
    parts.append(feathers(cx, cy))
    return unary_union(parts)


def tribal_half():
    """Honma-style tribal flame border for the back section (left side): bold S-tongues rising."""
    parts = [
        blade((27.5, 74.5), (15.5, 71.5), (21.5, 57.0), (15.2, 46.2), 4.6),     # long outer tongue
        blade((28.2, 72.2), (20.5, 68.6), (25.0, 60.2), (20.8, 52.6), 3.4),
        blade((28.6, 69.4), (24.0, 66.4), (27.2, 62.4), (24.6, 58.4), 2.3),     # short inner tongue
    ]
    return unary_union(parts)


def divider(y, half):
    """Bar ornament from the reference: double line, centre diamond, starburst ends."""
    parts = [box(CX - half, y - .55, CX - 2.2, y - .3), box(CX + 2.2, y - .55, CX + half, y - .3),
             box(CX - half + 1.2, y + .3, CX - 2.2, y + .5), box(CX + 2.2, y + .3, CX + half - 1.2, y + .5),
             Polygon([(CX, y - 1.6), (CX + 1.4, y), (CX, y + 1.6), (CX - 1.4, y)])]
    for s in (-1, 1):
        parts.append(star((CX + s * (half + 1.6), y), 1.6, .3))
    return unary_union(parts)


def panel():
    P = plate()
    body = inset(P, 2.4)
    g = [outline(inset(P, 1.3), .45), outline(body, .16)]
    cx, cy = EMB
    # frame + mirrored half
    fh = frame_half()
    g += [fh, affinity.scale(fh, xfact=-1, origin=(CX, 0))]
    # centre: modified crown over the ParkNara hole-green mark
    cr, chh = crown_mark(cx, 7.4, 13.6)
    g.append(cr)
    g.append(pn_symbol(cx, 27.9, 6.6))
    # fine sunburst behind the frame, stopping short of the fold
    rays = [LineString([(cx + 24 * math.cos(math.radians(a)), cy + 22 * math.sin(math.radians(a))),
                        (cx + 70 * math.cos(math.radians(a)), cy + 70 * math.sin(math.radians(a)))]).buffer(.07)
            for a in range(0, 360, 4)]
    g.append(unary_union(rays).intersection(body.buffer(-.9)).intersection(box(0, 0, W, FOLD - 3.2)))
    # back section
    g.append(divider(43.6, 16))
    th = tribal_half()
    g.append(unary_union([th, affinity.scale(th, xfact=-1, origin=(CX, 0))]).intersection(inset(P, 3.2)))
    g += [star((CX + dx, 64.2), 1.25) for dx in (-6.8, -3.4, 0, 3.4, 6.8)]
    g += [box(CX - 13.5, 69.9, CX - 8.4, 70.1), box(CX + 8.4, 69.9, CX + 13.5, 70.1)]
    geo = unary_union(g).intersection(inset(P, .3))
    t1, _ = text(SERIF_KR, "CHAMPION", 5.2, CX, 54.2, .9)
    t2, _ = text(SANS, "MADE IN KOREA", 1.9, CX, 59.4, .9)
    t3, _ = text(SANS, "PREMIUM", 1.6, CX, 70.8, 1.1)
    return geo, t1 + t2 + t3, P


CUT = 'fill="none" stroke="#FF00FF" stroke-width=".22" stroke-dasharray="1 .6"'
FOLD_LINE = f'<path d="M4 {FOLD}H{W - 4}" stroke="#00A0E0" stroke-width=".25" stroke-dasharray="2.2 1"/>'
GOLD = ('<defs><linearGradient id="g" x1="0" y1="0" x2=".35" y2="1">'
        '<stop offset="0" stop-color="#f3e2b0"/><stop offset=".35" stop-color="#d9bd7c"/>'
        '<stop offset=".6" stop-color="#c6a562"/><stop offset="1" stop-color="#e8d3a0"/></linearGradient>'
        '<linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#e9d39a"/><stop offset="1" stop-color="#b8924a"/></linearGradient>'
        '<filter id="eng" x="-5%" y="-5%" width="110%" height="110%">'
        '<feOffset in="SourceAlpha" dx=".2" dy=".24" result="o"/><feFlood flood-color="#fff6d8" flood-opacity=".85"/>'
        '<feComposite in2="o" operator="in" result="hl"/>'
        '<feMerge><feMergeNode in="hl"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')


def svg(body, pad=3):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W + 2 * pad}mm" height="{H + 2 * pad}mm" '
            f'viewBox="{-pad} {-pad} {W + 2 * pad} {H + 2 * pad}">{body}</svg>')


if __name__ == "__main__":
    import cairosvg, pymupdf
    geo, tx, P = panel()
    line = svg(f'<path d="{d_of(geo)}"/>{tx}<path d="{d_of(P)}" {CUT}/>{FOLD_LINE}')
    (OUT / "sole_plate_layout.svg").write_text(line)
    pdf = OUT / "tmp.pdf"
    cairosvg.svg2pdf(bytestring=line.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf); d.set_metadata({"title": "CHAMPION sole plate 95-75-30 x 80"})
    d.save(OUT / "sole_plate_layout.ai", garbage=3, deflate=True); pdf.unlink()
    lower = P.intersection(box(-1, FOLD, W + 1, H + 2))
    gold = svg(GOLD + f'<path d="{d_of(P)}" fill="url(#g)"/><path d="{d_of(lower)}" fill="url(#g2)" opacity=".55"/>'
               f'<g fill="#6b4d1a" filter="url(#eng)"><path d="{d_of(geo)}"/>{tx}</g>')
    (OUT / "sole_plate_gold.svg").write_text(gold)
    cairosvg.svg2png(bytestring=gold.encode(), write_to=str(OUT / "sole_plate_gold.png"), output_width=2000)
    cairosvg.svg2png(bytestring=line.encode(), write_to=str(OUT / "sole_plate_layout.png"), output_width=2000,
                     background_color="white")
    print("ok")
