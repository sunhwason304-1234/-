"""CHAMPION park golf head v2 - refined engraving for a Volvik-style head.

Head: D profile seen from the face (flat top, round sole), plan view with a straight face
edge and a rounded back. Gold top cap (engraved) over a wood body, carbon face with gold pins.

Panels (mm, y-down):
  top  : 72 x 92 plan shape, back apex at y=0, face edge at y=92 (reads from the face side).
         Shaft rises from the centre of a laurel wreath, guilloche sunburst behind it.
  face : 72 x 52 D shape, carbon plate with 10 gold pins.
"""
import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from shaft import bezier, d_of, leaf, ribbon, spiral, star
from head_art import crown, trophy, laurel_branch, outline

OUT = Path(__file__).parent / "head_v2"
OUT.mkdir(exist_ok=True)
HW, HD, ARC = 72.0, 92.0, 42.0          # width, depth, depth of the rounded back
FH, FS = 52.0, 16.0                     # face height, straight-side height of the D (from the top)
HOSEL = (36.0, 22.0)                    # shaft centre on the top plate
SERIF_KR = ("/root/.fonts/NotoSerifCJK-Bold.ttc", 1)
ITALIC = ("/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf", 0)


def plan(inset=0.0, n=90):
    """Top-view outline: rounded back (y=0 apex) + straight sides + straight face edge."""
    rx, ry = HW / 2 - inset, ARC - inset
    pts = [(HW / 2 - rx * math.cos(math.pi * i / n), ARC - ry * math.sin(math.pi * i / n)) for i in range(n + 1)]
    pts += [(HW - inset, HD - inset), (inset, HD - inset)]
    return Polygon(pts)


def dface(inset=0.0, n=80):
    """Face outline: flat top, straight sides to FS, half-ellipse sole."""
    w = HW / 2 - inset
    pts = [(HW / 2 - w, inset), (HW / 2 + w, inset)]
    for i in range(n + 1):
        a = math.pi * i / n
        pts.append((HW / 2 + w * math.cos(a), FS + (FH - FS - inset) * math.sin(a)))
    return Polygon(pts)


def fleur(cx, y0, h):
    """Fleur-de-lis ornament, top at y0, height h."""
    parts = [leaf((cx, y0 + .6 * h), -math.pi / 2, .6 * h, .3 * h)]
    for s in (-1, 1):
        p = bezier((cx + s * .05 * h, y0 + .58 * h), (cx + s * .5 * h, y0 + .52 * h),
                   (cx + s * .52 * h, y0 + .1 * h), (cx + s * .27 * h, y0 + .2 * h), 40)
        parts.append(ribbon(p, .14 * h, .045 * h))
        t = bezier((cx, y0 + .7 * h), (cx + s * .1 * h, y0 + .8 * h), (cx + s * .24 * h, y0 + .86 * h),
                   (cx + s * .3 * h, y0 + .76 * h), 30)
        parts.append(ribbon(t, .07 * h, .03 * h))
    parts.append(box(cx - .25 * h, y0 + .6 * h, cx + .25 * h, y0 + .68 * h))
    parts.append(leaf((cx, y0 + .68 * h), math.pi / 2, .3 * h, .12 * h))
    return unary_union(parts)


_f = {}


def text(fontspec, s, cap, cx, baseline, track=0.0):
    path, idx = fontspec
    f = _f.setdefault(fontspec, TTFont(path, fontNumber=idx))
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    capu = getattr(f["OS/2"], "sCapHeight", 0) or f["head"].unitsPerEm * .7
    k = cap / capu
    pen, x = SVGPathPen(gs), 0.0
    for ch in s:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, x, 0)))
        x += hmtx[g][0] * k + track
    w = x - track
    return f'<path transform="translate({cx - w / 2:.3f},{baseline:.3f})" d="{pen.getCommands()}"/>', w


def panel_top():
    cx = HW / 2
    P = plan()
    inner = plan(4.6)
    g = [outline(plan(2.4), .45), outline(plan(3.7), .16)]
    hx, hy = HOSEL
    # hosel medallion: double ring + laurel wreath
    g += [Point(hx, hy).buffer(9.9).difference(Point(hx, hy).buffer(9.55)),
          Point(hx, hy).buffer(10.9).difference(Point(hx, hy).buffer(10.75))]
    g.append(laurel_branch(hx, hy, 14.2, 90 + 26, 270 - 34, -1, 3.5, 9))
    g.append(laurel_branch(hx, hy, 14.2, 90 - 26, -90 + 34, 1, 3.5, 9))
    g.append(Point(hx, hy + 14.2).buffer(.9))
    # guilloche sunburst behind the wreath (fine radial lines)
    rays = []
    for i in range(0, 360, 3):
        a = math.radians(i)
        rays.append(LineString([(hx + 18.6 * math.cos(a), hy + 18.6 * math.sin(a)),
                                (hx + 60 * math.cos(a), hy + 60 * math.sin(a))]).buffer(.07, cap_style="flat"))
    g.append(unary_union(rays).intersection(inner).intersection(box(0, 0, HW, 37.5)))
    g.append(box(12, 38.6, HW - 12, 38.78))
    # crown (fine outline style)
    cr, _ = crown(cx, 46.2, 14, 7.2)
    g.append(cr)
    # rule with diamond
    g += [box(cx - 20, 65.6, cx - 3, 65.78), box(cx + 3, 65.6, cx + 20, 65.78),
          Polygon([(cx, 64.3), (cx + 1.3, 65.69), (cx, 67.1), (cx - 1.3, 65.69)]),
          Point(cx - 21.2, 65.69).buffer(.45), Point(cx + 21.2, 65.69).buffer(.45)]
    # trophy flanked by stars
    tr, _ = trophy(cx, 76.5, 9.5)
    g.append(tr)
    for s in (-1, 1):
        g += [star((cx + s * 8.5, 82), 1.25), star((cx + s * 13, 82), .95)]
    # fleur-de-lis at the face-side corners
    g += [fleur(10.5, 79, 8.5), fleur(HW - 10.5, 79, 8.5)]
    geo = unary_union(g).intersection(P)
    t1, _ = text(SERIF_KR, "CHAMPION", 6.0, cx, 60.6, 1.55)
    t2, _ = text(ITALIC, "Premium Park Golf", 3.1, cx, 72.4, .35)
    return geo, t1 + t2, P


def panel_face():
    D = dface()
    carbon = dface(1.2)
    ring = outline(dface(3.2), .25)
    # 10 gold pins, symmetric: 3 along the top, 2 on the straight sides, 5 around the sole
    w, ry = HW / 2 - 4.8, FH - FS - 4.8
    pins = [Point(x, 4.8) for x in (18, 36, 54)] + [Point(4.8, 15), Point(HW - 4.8, 15)]
    pins += [Point(HW / 2 + w * math.cos(math.radians(a)), FS + ry * math.sin(math.radians(a)))
             for a in (22, 56, 90, 124, 158)]
    heads = unary_union([Point(p).buffer(1.35, quad_segs=12) for p in pins])
    return D, carbon, ring, heads, [(p.x, p.y) for p in pins]


CUT = 'fill="none" stroke="#FF00FF" stroke-width=".2" stroke-dasharray="1 .6"'


def svg(w, h, body, pad=2):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w + 2 * pad}mm" height="{h + 2 * pad}mm" '
            f'viewBox="{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}">{body}</svg>')


if __name__ == "__main__":
    import cairosvg, pymupdf
    top, tx, P = panel_top()
    D, carbon, ring, heads, pins = panel_face()
    top_svg = svg(HW, HD, f'<path d="{d_of(top)}"/>{tx}<path d="{d_of(P)}" {CUT}/>')
    face_svg = svg(HW, FH, f'<path d="{d_of(carbon)}" fill="#1c1c1c"/><path d="{d_of(ring)}" fill="#C9A13B"/>'
                            f'<path d="{d_of(heads)}" fill="#C9A13B"/><path d="{d_of(D)}" {CUT}/>')
    (OUT / "head2_top_engraving.svg").write_text(top_svg)
    (OUT / "head2_face_plate.svg").write_text(face_svg)
    # combined artboard -> .ai (PDF-compatible)
    lab = lambda s, x, y: text(("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 0), s, 3.0, x, y, .4)[0]
    sheet = svg(190, 125, f'<rect x="-2" y="-2" width="194" height="129" fill="#fff"/>'
                f'<g transform="translate(10,18)"><path d="{d_of(top)}"/>{tx}<path d="{d_of(P)}" {CUT}/></g>'
                f'<g transform="translate(105,18)"><path d="{d_of(carbon)}" fill="#1c1c1c"/><path d="{d_of(ring)}" fill="#C9A13B"/>'
                f'<path d="{d_of(heads)}" fill="#C9A13B"/><path d="{d_of(D)}" {CUT}/></g>'
                f'<g fill="#666">{lab("TOP 72 x 92", 46, 12)}{lab("FACE 72 x 52", 141, 12)}</g>', 0)
    (OUT / "head2_engraving_sheet.svg").write_text(sheet)
    pdf = OUT / "tmp.pdf"
    cairosvg.svg2pdf(bytestring=sheet.encode(), write_to=str(pdf))
    d = pymupdf.open(pdf); d.set_metadata({"title": "CHAMPION park golf head v2 engraving"})
    d.save(OUT / "head2_engraving.ai", garbage=3, deflate=True); pdf.unlink()
    # clean raster masks for the 3D mockup
    M = "/tmp/claude-0/mock"
    cairosvg.svg2png(bytestring=svg(HW, FH, f'<rect x="-1" y="-1" width="{HW + 2}" height="{FH + 2}" fill="#fff"/>'
                                    f'<path d="{d_of(ring)}"/>', 0).encode(),
                     write_to=f"{M}/h2_face.png", output_width=1440, output_height=int(1440 * FH / HW))
    cairosvg.svg2png(bytestring=svg(HW, HD, f'<rect x="-1" y="-1" width="{HW + 2}" height="{HD + 2}" fill="#fff"/>'
                                    f'<path d="{d_of(top)}"/>{tx}', 0).encode(),
                     write_to=f"{M}/h2_top.png", output_width=1440, output_height=int(1440 * HD / HW))
    print("pins", [(round(x, 2), round(y, 2)) for x, y in pins])
