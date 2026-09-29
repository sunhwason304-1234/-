"""CHAMPION park golf head v3 - top plate layout (front / flat view).

Rounded-triangle ("shield / pick") top plate, following the classic gold-head layout:
  upper band : crowned shield with a C monogram, acanthus scrolls left & right
  divider    : curved line parallel to the top edge
  centre     : CHAMPION (serif), subtitle, three grade stars
  edge       : double contour + small circle marks
All in mm, y-down. Writes engraving line art (SVG + .ai) and a gold-rendered preview.
"""
import math
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from shaft import bezier, d_of, leaf, ribbon, spiral, star
from head_art import crown, outline
from head2_art import text, SERIF_KR

OUT = Path(__file__).parent / "head_v3"
OUT.mkdir(exist_ok=True)
W, H = 84.0, 80.0
CX = W / 2


def plate():
    """Rounded triangle: gently arched top edge, sides sweeping to a rounded point."""
    top = bezier((3, 12), (22, 1.5), (62, 1.5), (81, 12), 60)
    right = bezier((81, 12), (84, 34), (64, 64), (CX + 4, 78.5), 60)
    left = [(W - x, y) for x, y in reversed(right)]
    g = Polygon(top + right[1:] + left[1:])
    return g.buffer(-4, join_style="round").buffer(4, join_style="round")


def inset(g, d):
    return g.buffer(-d, join_style="round")


def scroll(mirror=False):
    """Acanthus scroll for the upper band (left side; mirrored for the right)."""
    parts = []
    main = bezier((31.5, 18.2), (28.5, 9.2), (19, 8.4), (13.2, 13.6), 50)
    c = (16.4, 15.0)
    main += spiral(c, math.dist(main[-1], c), math.atan2(main[-1][1] - c[1], main[-1][0] - c[0]), 1.1, cw=True, n=50)[1:]
    parts.append(ribbon(main, 1.05, .22))
    low = bezier((31.2, 20.6), (27.5, 23.4), (21.5, 23.2), (20.2, 20.4), 40)
    c2 = (22.6, 20.1)
    low += spiral(c2, math.dist(low[-1], c2), math.atan2(low[-1][1] - c2[1], low[-1][0] - c2[0]), .9, cw=False, n=40)[1:]
    parts.append(ribbon(low, .75, .18))
    for t, da, L, w in [(.14, -1.25, 4.2, 1.6), (.3, -1.35, 3.6, 1.35), (.47, -1.2, 2.8, 1.1), (.3, 1.25, 2.6, 1.0)]:
        i = int(t * 50)
        (x0, y0), (x1, y1) = main[i], main[i + 1]
        parts.append(leaf(main[i], math.atan2(y1 - y0, x1 - x0) + da, L, w))
    parts.append(leaf((13.4, 17.6), math.radians(125), 4.2, 1.5))     # pointed drop leaf
    parts.append(Point(26.2, 15.6).buffer(.55))
    g = unary_union(parts)
    return affinity.scale(g, xfact=-1, origin=(CX, 0)) if mirror else g


def shield(cx, top, w, h):
    """Heater shield with a double outline."""
    pts = [(cx - w / 2, top), (cx + w / 2, top)]
    pts += bezier((cx + w / 2, top), (cx + w / 2, top + h * .55), (cx + w * .25, top + h * .85), (cx, top + h), 30)[1:]
    pts += bezier((cx, top + h), (cx - w * .25, top + h * .85), (cx - w / 2, top + h * .55), (cx - w / 2, top), 30)[1:]
    s = Polygon(pts)
    return unary_union([outline(s, .7), outline(s.buffer(-1.5, join_style="mitre"), .25)]), s


def panel():
    P = plate()
    g = [outline(inset(P, 1.6), .55), outline(inset(P, 2.8), .2)]
    # curved divider under the upper band (parallel to the arched top edge)
    div = LineString(bezier((6.5, 27.2), (24, 21.8), (60, 21.8), (W - 6.5, 27.2), 60)).buffer(.28)
    g.append(div.intersection(inset(P, 2.8)))
    # crowned shield with C monogram
    sh, shp = shield(CX, 8.9, 12.4, 14.4)
    g.append(sh)
    cr, _ = crown(CX, 11.9, 5.4, 2.5)
    g.append(cr)
    g += [scroll(False), scroll(True)]
    # three grade stars
    g += [star((CX + dx, 55.5), 1.9) for dx in (-6, 0, 6)]
    # small circle marks around the edge (as on the reference)
    marks = []
    ring_path = inset(P, 6.4).exterior
    for y in (31, 59, 69):               # symmetric pairs on the inner contour
        hit = ring_path.intersection(LineString([(-5, y), (W + 5, y)]))
        for p in getattr(hit, "geoms", [hit]):
            marks.append(Point(p).buffer(1.3).difference(Point(p).buffer(1.0)))
    g += marks
    geo = unary_union(g).intersection(P)
    mono, _ = text(SERIF_KR, "C", 4.5, CX, 19.9)
    t1, w1 = text(SERIF_KR, "CHAMPION", 6.4, CX, 42.5, 1.1)
    t2, _ = text(("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 0), "PREMIUM GOLD", 2.7, CX, 49.5, .75)
    return geo, mono + t1 + t2, P


CUT = 'fill="none" stroke="#FF00FF" stroke-width=".2" stroke-dasharray="1 .6"'


def svg(w, h, body, pad=2):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w + 2 * pad}mm" height="{h + 2 * pad}mm" '
            f'viewBox="{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}">{body}</svg>')


GOLD = ('<defs><linearGradient id="g" x1="0" y1="0" x2=".35" y2="1">'
        '<stop offset="0" stop-color="#f3e2b0"/><stop offset=".35" stop-color="#d9bd7c"/>'
        '<stop offset=".6" stop-color="#c6a562"/><stop offset="1" stop-color="#e8d3a0"/></linearGradient>'
        '<filter id="eng" x="-5%" y="-5%" width="110%" height="110%">'
        '<feOffset in="SourceAlpha" dx=".22" dy=".26" result="o"/><feFlood flood-color="#fff6d8" flood-opacity=".85"/>'
        '<feComposite in2="o" operator="in" result="hl"/>'
        '<feMerge><feMergeNode in="hl"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')

if __name__ == "__main__":
    import cairosvg, pymupdf
    geo, tx, P = panel()
    line = svg(W, H, f'<path d="{d_of(geo)}"/>{tx}<path d="{d_of(P)}" {CUT}/>')
    (OUT / "head3_top_layout.svg").write_text(line)
    pdf = OUT / "tmp.pdf"
    cairosvg.svg2pdf(bytestring=line.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf); d.set_metadata({"title": "CHAMPION park golf head v3 top layout"})
    d.save(OUT / "head3_top_layout.ai", garbage=3, deflate=True); pdf.unlink()
    # gold preview: plate in brushed-gold gradient, engraving recessed (dark) with a light lower edge
    gold = svg(W, H, GOLD + f'<path d="{d_of(P)}" fill="url(#g)"/>'
               f'<g fill="#6b4d1a" filter="url(#eng)"><path d="{d_of(geo)}"/>{tx}</g>', 3)
    (OUT / "head3_top_gold.svg").write_text(gold)
    cairosvg.svg2png(bytestring=gold.encode(), write_to=str(OUT / "head3_top_gold.png"), output_width=1800)
    cairosvg.svg2png(bytestring=line.encode(), write_to=str(OUT / "head3_top_layout.png"), output_width=1800,
                     background_color="white")
    print("ok")
