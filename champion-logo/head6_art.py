"""CHAMPION park golf head v6 - top plate layout: shield with flame flourishes on top, name below.

Same rounded-triangle plate as v3-v5. Layout (front / flat view):
  upper  : large shield with C monogram, flame flourishes sweeping out left & right with a scroll curl
  lower  : CHAMPION (serif), subtitle, four stars
"""
import math
from pathlib import Path

from shapely import affinity
from shapely.geometry import Point
from shapely.ops import unary_union

from shaft import bezier, d_of, ribbon, spiral, star
from head_art import outline
from head2_art import text, SERIF_KR
from head3_art import plate, inset, shield, svg, CUT, GOLD, W, H, CX
from head4_art import blade

OUT = Path(__file__).parent / "head_v6"
OUT.mkdir(exist_ok=True)
SANS = ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 0)


def flourish():
    """Left flourish (mirrored for the right): a sweeping scroll base with flame tongues rising up-out."""
    base = bezier((40.5, 30.6), (33.0, 33.4), (24.5, 33.0), (18.6, 29.6), 50)
    c = (19.8, 27.2)
    base += spiral(c, math.dist(base[-1], c), math.atan2(base[-1][1] - c[1], base[-1][0] - c[0]), 1.0, cw=False, n=40)[1:]
    parts = [ribbon(base, 1.5, .3)]
    parts += [
        blade((33.8, 31.6), (33.5, 24.5), (27.5, 20.5), (25.8, 11.6), 3.2),    # tallest tongue
        blade((29.6, 32.2), (29.0, 26.4), (23.5, 23.4), (20.6, 16.2), 2.7),
        blade((25.4, 32.2), (24.6, 28.2), (20.4, 26.4), (16.6, 22.4), 2.1),
        blade((36.6, 30.2), (37.2, 25.6), (35.0, 21.0), (34.4, 16.6), 1.6),    # small inner tongue
        blade((28.0, 33.6), (25.8, 36.0), (22.8, 37.0), (19.4, 36.8), 1.7),    # lower drop lick
    ]
    parts.append(Point(23.6, 30.2).buffer(.5))
    return unary_union(parts)


def panel():
    P = plate()
    g = [outline(inset(P, 1.8), .45)]
    sh, shp = shield(CX, 11.6, 14.6, 18.0)
    g.append(sh)
    fl = flourish()
    fl = unary_union([fl, affinity.scale(fl, xfact=-1, origin=(CX, 0))]).difference(shp.buffer(.9))
    g.append(fl)
    g += [star((CX + dx, 60.0), 1.25) for dx in (-5.25, -1.75, 1.75, 5.25)]
    geo = unary_union(g).intersection(inset(P, .4))
    mono, _ = text(SERIF_KR, "C", 7.4, CX, 25.4)
    t1, _ = text(SERIF_KR, "CHAMPION", 4.8, CX, 48.6, .8)
    t2, _ = text(SANS, "ROYAL GOLD", 2.3, CX, 54.6, .6)
    return geo, mono + t1 + t2, P


if __name__ == "__main__":
    import cairosvg, pymupdf
    geo, tx, P = panel()
    line = svg(W, H, f'<path d="{d_of(geo)}"/>{tx}<path d="{d_of(P)}" {CUT}/>')
    (OUT / "head6_top_layout.svg").write_text(line)
    pdf = OUT / "tmp.pdf"
    cairosvg.svg2pdf(bytestring=line.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf); d.set_metadata({"title": "CHAMPION park golf head v6 top layout"})
    d.save(OUT / "head6_top_layout.ai", garbage=3, deflate=True); pdf.unlink()
    gold = svg(W, H, GOLD + f'<path d="{d_of(P)}" fill="url(#g)"/>'
               f'<g fill="#6b4d1a" filter="url(#eng)"><path d="{d_of(geo)}"/>{tx}</g>', 3)
    (OUT / "head6_top_gold.svg").write_text(gold)
    cairosvg.svg2png(bytestring=gold.encode(), write_to=str(OUT / "head6_top_gold.png"), output_width=1800)
    cairosvg.svg2png(bytestring=line.encode(), write_to=str(OUT / "head6_top_layout.png"), output_width=1800,
                     background_color="white")
    print("ok")
