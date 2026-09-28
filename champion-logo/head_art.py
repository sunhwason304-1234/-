"""CHAMPION park golf HEAD engraving artwork (crown, laurel, trophy).

Three panels, all in mm, y-down:
  top  : 72 x 88  top plate of the head (back edge = top of the artwork so it reads from the face side; hosel at back-heel)
  back : 72 x 52  D-shaped back face - trophy crest in a laurel wreath under a crown
  face : 72 x 52  D-shaped striking face - carbon plate, 4 gold screws, small wordmark

Writes engraving line-art SVGs (black = engraved) plus a single Illustrator-compatible
head_engraving.ai with the three panels and their cut lines.
"""
import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

import build as wordmark
from shaft import SERIF, SANS, bezier, d_of, leaf, ribbon, star, text_d

OUT = Path(__file__).parent
HW, HD, HH = 72.0, 88.0, 52.0     # head width (toe-heel), depth (face-back), height
D_FLAT = 18.0                     # straight side height of the D before the round bottom
HOSEL = (12.5, 12.5, 7.6)         # hosel centre on the top plate (x, y) and radius (back-heel corner)


# ------------------------------------------------------------------ shapes

def d_shape(inset=0.0, n=64):
    """D profile: flat top, short straight sides, elliptical bottom (72 x 52)."""
    w, h = HW / 2 - inset, HH - inset
    pts = [(HW / 2 - w, inset), (HW / 2 + w, inset), (HW / 2 + w, D_FLAT)]
    ry = h - D_FLAT
    for i in range(1, n):
        a = math.pi * i / n
        pts.append((HW / 2 + w * math.cos(a), D_FLAT + ry * math.sin(a)))
    pts.append((HW / 2 - w, D_FLAT))
    return Polygon(pts)


def rrect(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, quad_segs=16)


def outline(g, w):
    """Engraved contour line of width w just inside the shape."""
    return g.difference(g.buffer(-w, join_style="mitre"))


def crown(cx, cy, w, h):
    x0, x1 = cx - w / 2, cx + w / 2
    body = Polygon([(x0, cy + h / 2), (x1, cy + h / 2), (x1 + w * .03, cy - h / 2 + h * .2),
                    (cx + w * .25, cy + h * .02), (cx, cy - h / 2), (cx - w * .25, cy + h * .02),
                    (x0 - w * .03, cy - h / 2 + h * .2)])
    band = box(x0, cy + h / 2 + h * .1, x1, cy + h / 2 + h * .26)
    tips = [Point(p).buffer(w * .065, quad_segs=10) for p in
            [(x0 - w * .03, cy - h / 2 + h * .12), (cx, cy - h / 2 - h * .09), (x1 + w * .03, cy - h / 2 + h * .12)]]
    jewels = [Point(cx + dx * w, cy + h * .3).buffer(w * .045, quad_segs=10) for dx in (-.28, 0, .28)]
    g = unary_union([body, band, *tips])
    return unary_union([outline(body, w * .045), band, *tips, *jewels]), g


def trophy(cx, top, h):
    """Trophy cup: bowl + handles + stem + knob + two-step base, star cut into the bowl."""
    w = h * 0.64
    L = bezier((cx - w / 2, top), (cx - w / 2, top + h * .42), (cx - h * .1, top + h * .5), (cx - h * .045, top + h * .56), 40)
    R = [(2 * cx - x, y) for x, y in reversed(L)]
    bowl = Polygon(L + R)
    lip = box(cx - w / 2 - h * .03, top - h * .05, cx + w / 2 + h * .03, top + h * .015)
    handles = []
    for s in (-1, 1):
        c = (cx + s * w * .5, top + h * .17)
        ring = Point(c).buffer(h * .15, quad_segs=24).difference(Point(c).buffer(h * .1, quad_segs=24))
        handles.append(ring.intersection(box(c[0], c[1] - 1e3, c[0] + s * 1e3, c[1] + 1e3) if s > 0
                                         else box(c[0] - 1e3, c[1] - 1e3, c[0], c[1] + 1e3)))
    stem = box(cx - h * .03, top + h * .55, cx + h * .03, top + h * .74)
    knob = affinity.scale(Point(cx, top + h * .64).buffer(h * .055, quad_segs=16), 1.4, 1)
    base1 = Polygon([(cx - h * .14, top + h * .74), (cx + h * .14, top + h * .74),
                     (cx + h * .2, top + h * .84), (cx - h * .2, top + h * .84)])
    base2 = rrect(cx - h * .27, top + h * .85, cx + h * .27, top + h * .97, h * .015)
    solid = unary_union([bowl, lip, *handles, stem, knob, base1, base2])
    st = star((cx, top + h * .22), h * .12)
    return solid.difference(st.buffer(h * .012)), solid


def laurel_branch(cx, cy, r, a0, a1, side, leaf_len, n=9):
    """Laurel branch on a circular arc (angles in degrees, SVG y-down, 90 = bottom)."""
    sgn = 1 if a1 > a0 else -1
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
           for a in [a0 + (a1 - a0) * i / 60 for i in range(61)]]
    parts = [ribbon(pts, leaf_len * .16, leaf_len * .06)]
    for k in range(n):
        t = 0.08 + 0.86 * k / (n - 1)
        i = int(t * 60)
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        ang = math.atan2(yb - ya, xb - xa)
        L = leaf_len * (1 - 0.35 * t)
        parts.append(leaf(pts[i], ang - sgn * 0.62, L, L * .4))    # outer
        parts.append(leaf(pts[i], ang + sgn * 0.62, L * .9, L * .36))  # inner
    parts.append(leaf(pts[-1], math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0]), leaf_len * .8, leaf_len * .32))
    return unary_union(parts)


def wreath(cx, cy, r, leaf_len, gap_top=30, gap_bottom=18, n=9):
    left = laurel_branch(cx, cy, r, 90 + gap_bottom, 270 - gap_top, -1, leaf_len, n)
    right = laurel_branch(cx, cy, r, 90 - gap_bottom, -90 + gap_top, 1, leaf_len, n)
    # small ribbon bow where the branches meet
    bow = unary_union([
        Polygon([(cx, cy + r), (cx - leaf_len * .55, cy + r - leaf_len * .3), (cx - leaf_len * .55, cy + r + leaf_len * .3)]),
        Polygon([(cx, cy + r), (cx + leaf_len * .55, cy + r - leaf_len * .3), (cx + leaf_len * .55, cy + r + leaf_len * .3)]),
        Point(cx, cy + r).buffer(leaf_len * .14)])
    return unary_union([left, right, bow])


# ------------------------------------------------------------------ text helpers

_f = {}


def glyph(font, ch, cap):
    f = _f.setdefault(font, TTFont(font))
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    capu = getattr(f["OS/2"], "sCapHeight", 0) or f["head"].unitsPerEm * .7
    k = cap / capu
    g = cmap[ord(ch)]
    pen = SVGPathPen(gs)
    gs[g].draw(TransformPen(pen, (k, 0, 0, -k, 0, 0)))
    return pen.getCommands(), f["hmtx"][g][0] * k


def htext(font, s, cap, cx, baseline, track=0.0, fill="#000"):
    d, w = text_d(font, s, cap, track)
    return f'<path transform="translate({cx - w / 2:.3f},{baseline:.3f})" d="{d}" fill="{fill}"/>'


def arc_text(font, s, cap, cx, cy, r, track=0.0, fill="#000", bottom=True):
    """Text on a circle; bottom=True runs left->right along the lower arc (readable)."""
    gl = [glyph(font, ch, cap) if ch != " " else ("", cap * .35) for ch in s]
    total = sum(a for _, a in gl) + track * (len(gl) - 1)
    rr = r if not bottom else r + cap          # baseline radius
    ang = total / rr                            # radians spanned
    out, pos = [], 0.0
    for d, adv in gl:
        mid = pos + adv / 2
        if bottom:
            a = math.pi / 2 + ang / 2 - mid / rr     # from left to right along the bottom
            x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            rot = math.degrees(a) - 90
        else:
            a = -math.pi / 2 - ang / 2 + mid / rr
            x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            rot = math.degrees(a) + 90
        if d:
            out.append(f'<path transform="translate({x:.3f},{y:.3f}) rotate({rot:.2f}) translate({-adv / 2:.3f},{0 if not bottom else -cap:.3f}) '
                       f'translate(0,{cap:.3f})" d="{d}" fill="{fill}"/>')
        pos += adv + track
    return "".join(out)


def wordmark_el(cx, cy, length, fill="#000"):
    main, acc, ww = wordmark.build()
    k = length / ww
    geo = unary_union([main, acc])
    return (f'<g transform="translate({cx - length / 2:.3f},{cy - 50 * k:.3f}) scale({k:.5f})" fill-rule="evenodd">'
            f'<path d="{wordmark.to_path(geo)}" fill="{fill}"/></g>')


# ------------------------------------------------------------------ panels

def panel_top(ink="#000"):
    cx = HW / 2
    g = []
    plate = rrect(0, 0, HW, HD, 9)
    g.append(outline(rrect(2.4, 2.4, HW - 2.4, HD - 2.4, 7), 0.55))
    g.append(outline(rrect(3.8, 3.8, HW - 3.8, HD - 3.8, 5.8), 0.25))
    # corner diamonds
    for x, y in [(8, 8), (HW - 8, 8), (8, HD - 8), (HW - 8, HD - 8)]:
        g.append(Polygon([(x, y - 1.4), (x + 1, y), (x, y + 1.4), (x - 1, y)]))
    cr, _ = crown(cx, 14.5, 17, 9)
    g.append(cr)
    # divider under wordmark: line - diamond - line
    g += [box(cx - 24, 41.6, cx - 3, 41.9), box(cx + 3, 41.6, cx + 24, 41.9),
          Polygon([(cx, 40.2), (cx + 1.6, 41.75), (cx, 43.3), (cx - 1.6, 41.75)])]
    # crest: wreath + trophy (kept clear of the hosel at the heel)
    wx, wy = cx, 64.5
    g.append(wreath(wx, wy, 13.2, 4.4, gap_top=34, n=8))
    tr, _ = trophy(wx, 57.5, 16.5)
    g.append(tr)
    # hosel ring guide
    geo = unary_union(g).difference(Point(HOSEL[:2]).buffer(HOSEL[2] + 1.2))
    geo = geo.intersection(plate)
    extra = (wordmark_el(cx, 32.5, 56, ink) +
             htext(SERIF, "PREMIUM PARK GOLF", 2.4, cx, 49.5, 1.0, ink))
    return geo, extra, plate


def panel_back(ink="#000"):
    cx = HW / 2
    D = d_shape()
    g = [outline(d_shape(1.6), 0.5), outline(d_shape(2.9), 0.22)]
    wy = 23.0
    g.append(wreath(cx, wy, 11.2, 3.9, gap_top=46, gap_bottom=24, n=7))
    tr, _ = trophy(cx, 15.8, 13.2)
    g.append(tr)
    cr, _ = crown(cx, 8.0, 10, 5.5)
    g.append(cr)
    # stars either side of the crown
    for s in (-1, 1):
        for i, dx in enumerate((10, 15.5, 21)):
            g.append(star((cx + s * dx, 8.8 + i * 1.1), 1.35))
    geo = unary_union(g).intersection(D)
    extra = arc_text(SERIF, "CHAMPION", 2.9, cx, wy, 15.2, 1.1, ink, bottom=True)
    return geo, extra, D


def panel_face(ink="#000"):
    cx = HW / 2
    D = d_shape()
    carbon = d_shape(3.2)
    screws = [(9.5, 7.5), (HW - 9.5, 7.5), (15, 40), (HW - 15, 40)]
    g = [outline(d_shape(0.8), 0.45)]
    heads = [Point(p).buffer(2.1, quad_segs=16) for p in screws]
    return unary_union(g), carbon, heads, screws


# ------------------------------------------------------------------ outputs

def svg_doc(w, h, body, pad=0):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w + 2 * pad}mm" height="{h + 2 * pad}mm" '
            f'viewBox="{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}">{body}</svg>')


CUT = 'fill="none" stroke="#FF00FF" stroke-width=".2" stroke-dasharray="1 .6"'


def lineart():
    """Engraving line-art (black = engrave) for each panel, with magenta cut line."""
    top, top_x, plate = panel_top()
    back, back_x, D = panel_back()
    fl, carbon, heads, screws = panel_face()
    files = {
        "head_top_engraving.svg": svg_doc(HW, HD, f'<path d="{d_of(top)}"/>{top_x}<path d="{d_of(plate)}" {CUT}/>', 2),
        "head_back_engraving.svg": svg_doc(HW, HH, f'<path d="{d_of(back)}"/>{back_x}<path d="{d_of(D)}" {CUT}/>', 2),
        "head_face_plate.svg": svg_doc(HW, HH,
            f'<path d="{d_of(carbon)}" fill="#222"/><path d="{d_of(unary_union(heads))}" fill="#C9A13B"/>'
            f'{wordmark_el(HW / 2, 24, 30, "#C9A13B")}<path d="{d_of(fl)}"/><path d="{d_of(D)}" {CUT}/>', 2),
    }
    for n, s in files.items():
        (OUT / n).write_text(s)
    return files


def sheet_svg():
    """All three panels on one artboard with labels (for the .ai)."""
    top, top_x, plate = panel_top()
    back, back_x, D = panel_back()
    fl, carbon, heads, _ = panel_face()
    lab = lambda s, x, y: htext(SANS, s, 3.2, x, y, 0.4, "#555")
    W, H = 260, 130
    body = (f'<rect width="{W}" height="{H}" fill="#fff"/>'
            f'<g transform="translate(10,22)"><path d="{d_of(top)}"/>{top_x}<path d="{d_of(plate)}" {CUT}/></g>'
            f'<g transform="translate(96,22)"><path d="{d_of(back)}"/>{back_x}<path d="{d_of(D)}" {CUT}/></g>'
            f'<g transform="translate(180,22)"><path d="{d_of(carbon)}" fill="#222"/>'
            f'<path d="{d_of(unary_union(heads))}" fill="#C9A13B"/>{wordmark_el(HW / 2, 24, 30, "#C9A13B")}'
            f'<path d="{d_of(fl)}"/><path d="{d_of(D)}" {CUT}/></g>'
            + lab("TOP 72x88", 46, 15) + lab("BACK 72x52", 132, 15) + lab("FACE 72x52", 216, 15)
            + htext(SANS, "CHAMPION HEAD ENGRAVING  /  BLACK = ENGRAVE  /  MAGENTA = CUT LINE", 2.6, W / 2, 124, 0.3, "#999"))
    return svg_doc(W, H, body)


if __name__ == "__main__":
    import cairosvg, pymupdf
    lineart()
    s = sheet_svg()
    (OUT / "head_engraving_sheet.svg").write_text(s)
    pdf = OUT / "head_engraving_sheet.pdf"
    cairosvg.svg2pdf(bytestring=s.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf)
    d.set_metadata({"title": "CHAMPION park golf head engraving", "creator": "CHAMPION head generator"})
    d.save(OUT / "head_engraving.ai", garbage=3, deflate=True)
    pdf.unlink()
    print("ok")
