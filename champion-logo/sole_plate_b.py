"""CHAMPION sole copper plate - version B (all-over damask + enamel badge), same outline as sole_plate.py.

  sole (upper 40 mm) : all-over arabesque damask, eight-petal rosettes, fine arcs,
                       black-enamel pentagon badge: modified crown + ParkNara mark + CHAMPION
  back (lower 40 mm) : damask kept as left/right borders, clear centre panel with the lettering
                       CHAMPION / MADE IN KOREA / five stars / small PREMIUM (client memo)
"""
import math
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from shaft import bezier, d_of, star
from head_art import outline
from head2_art import text, SERIF_KR
from head7_art import rosette, scroll_unit, frange
from parknara import crown_mark, pn_symbol
from sole_plate import plate, inset, divider, W, H, FOLD, CX, SANS, CUT, FOLD_LINE, GOLD, svg
import random

OUT = Path(__file__).parent / "sole_plate_b"
OUT.mkdir(exist_ok=True)
BC = (CX, 19.2)                         # badge centre


def badge():
    cx, cy = BC
    pts = [(cx - 10.5, cy - 11), (cx + 10.5, cy - 11), (cx + 12, cy + 1.6), (cx, cy + 12.2), (cx - 12, cy + 1.6)]
    return Polygon(pts).buffer(-1.5, join_style="round").buffer(1.5, join_style="round")


def damask(area, seed=5):
    rnd = random.Random(seed)
    unit = scroll_unit()
    tiles = []
    step = 10.0
    for j, y in enumerate(frange(-2, H + 6, step * .82)):
        for x in frange(-4 + (step / 2 if j % 2 else 0), W + 6, step):
            g = unit if rnd.random() < .5 else affinity.scale(unit, -1, 1, origin=(0, 0))
            g = affinity.rotate(g, rnd.uniform(0, 360), origin=(0, 0))
            g = affinity.scale(g, rnd.uniform(.9, 1.08), rnd.uniform(.9, 1.08), origin=(0, 0))
            tiles.append(affinity.translate(g, x + rnd.uniform(-1.2, 1.2), y + rnd.uniform(-1.2, 1.2)))
    geo = unary_union(tiles).intersection(area)
    return unary_union([p for p in getattr(geo, "geoms", [geo]) if p.area > .8])


def panel():
    P = plate()
    body = inset(P, 2.4)
    B = badge()
    g = [outline(inset(P, 1.3), .45), outline(body, .16)]
    sole = body.intersection(box(-1, -1, W + 1, FOLD - 1.4))
    back = body.intersection(box(-1, FOLD + 1.4, W + 1, H + 2))
    # fold band: double line right at the bend
    g += [box(0, FOLD - .9, W, FOLD - .7).intersection(body), box(0, FOLD + .7, W, FOLD + .9).intersection(body)]
    # sole: arcs around the badge + rosettes + damask
    cx, cy = BC
    arcs = unary_union([Point(cx, cy).buffer(r, quad_segs=64).difference(Point(cx, cy).buffer(r - .2, quad_segs=64))
                        for r in (16.4, 17.3, 18.2)])
    g.append(arcs.intersection(sole))
    halo = Point(cx, cy).buffer(18.8)
    lower_arcs = unary_union([Point(CX, 62).buffer(r, quad_segs=64).difference(Point(CX, 62).buffer(r - .2, quad_segs=64))
                              for r in [27 + i * .95 for i in range(6)]])
    arc_zone = sole.intersection(Point(CX, 62).buffer(32.4)).difference(Point(CX, 62).buffer(26.8)).difference(halo)
    g.append(lower_arcs.intersection(arc_zone))
    ros_pts = [(13, 9.5), (W - 13, 9.5), (23.5, 30.5), (W - 23.5, 30.5), (7.5, 22), (W - 7.5, 22)]
    ros_r = [4.0, 4.0, 3.6, 3.6, 3.2, 3.2]
    for c, r in zip(ros_pts, ros_r):
        g.append(rosette(c, r).intersection(sole))
    keep = unary_union([halo, arc_zone.buffer(.6)] + [Point(c).buffer(r + 1.0) for c, r in zip(ros_pts, ros_r)])
    g.append(damask(sole.buffer(-.6).difference(keep)))
    # back: damask borders left / right, clear centre panel with lettering
    panel_c = inset(P, 9.0).intersection(box(-1, FOLD + 3.4, W + 1, H)).buffer(-1.5, join_style="round").buffer(1.5, join_style="round")
    g.append(outline(panel_c, .3))
    g.append(outline(panel_c.buffer(-1.0, join_style="round"), .14))
    g.append(damask(back.buffer(-.6).difference(panel_c.buffer(1.2)), seed=9))
    g += [star((CX + dx, 62.6), 1.2) for dx in (-6.4, -3.2, 0, 3.2, 6.4)]
    g.append(divider(47.2, 10.5))
    g += [box(CX - 12.5, 66.6, CX - 7.6, 66.8), box(CX + 7.6, 66.6, CX + 12.5, 66.8)]
    engraved = unary_union(g).intersection(inset(P, .3)).difference(B.buffer(1.4))
    engraved = unary_union([engraved, outline(B.buffer(1.0), .3)])
    # badge contents (gold on black enamel)
    cr, ch = crown_mark(cx, cy - 9.9, 9.4)
    inner = outline(B.buffer(-1.0, join_style="round"), .28)
    rule = unary_union([box(cx - 4.8, cy + 3.75, cx + 4.8, cy + 3.9)])
    gold = unary_union([cr, inner, rule])
    t_kr, _ = text(SERIF_KR, "파크나라", 2.6, cx, cy + 2.7, .3)
    t_en, _ = text(SANS, "PARK NARA", .85, cx, cy + 5.5, .32)
    t_badge = t_kr + t_en
    t1, _ = text(SERIF_KR, "CHAMPION", 5.0, CX, 55.6, .8)
    t2, _ = text(SANS, "MADE IN KOREA", 1.8, CX, 59.4, .8)
    t3, _ = text(SANS, "PREMIUM", 1.5, CX, 67.4, 1.0)
    return engraved, B, gold, t_badge, t1 + t2 + t3, P


if __name__ == "__main__":
    import cairosvg, pymupdf
    eng, B, gold_parts, tb, tx, P = panel()
    line = svg(f'<path d="{d_of(eng)}"/>{tx}<path d="{d_of(B)}" fill="#000"/>'
               f'<g fill="#fff"><path d="{d_of(gold_parts)}"/>{tb}</g><path d="{d_of(P)}" {CUT}/>{FOLD_LINE}')
    (OUT / "sole_plate_b_layout.svg").write_text(line)
    pdf = OUT / "tmp.pdf"
    cairosvg.svg2pdf(bytestring=line.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf); d.set_metadata({"title": "CHAMPION sole plate B 95-75-30 x 80"})
    d.save(OUT / "sole_plate_b_layout.ai", garbage=3, deflate=True); pdf.unlink()
    lower = P.intersection(box(-1, FOLD, W + 1, H + 2))
    gsvg = svg(GOLD + f'<path d="{d_of(P)}" fill="url(#g)"/><path d="{d_of(lower)}" fill="url(#g2)" opacity=".5"/>'
               f'<g fill="#6b4d1a" filter="url(#eng)"><path d="{d_of(eng)}"/>{tx}</g>'
               f'<path d="{d_of(B)}" fill="#141312"/><g fill="url(#g)"><path d="{d_of(gold_parts)}"/>{tb}</g>')
    (OUT / "sole_plate_b_gold.svg").write_text(gsvg)
    cairosvg.svg2png(bytestring=gsvg.encode(), write_to=str(OUT / "sole_plate_b_gold.png"), output_width=2000)
    cairosvg.svg2png(bytestring=line.encode(), write_to=str(OUT / "sole_plate_b_layout.png"), output_width=2000,
                     background_color="white")
    print("ok")
