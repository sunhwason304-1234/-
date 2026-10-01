"""Trace the client's tribal reference (ref/tribal_ref.png) into a clean, symmetric vector shape.
Returns the full emblem in mm-free units (height 1.0, centred on x=0)."""
import numpy as np
from PIL import Image, ImageFilter
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity
from skimage import measure


def trace(path="ref/tribal_ref.png", up=4):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(int)
    dark = (a.max(axis=2) < 110)                       # black ink only (the blue arrow is excluded)
    m = Image.fromarray((dark * 255).astype("uint8")).resize((im.width * up, im.height * up), Image.LANCZOS)
    m = m.filter(ImageFilter.GaussianBlur(up * .9))
    arr = np.asarray(m) / 255.0
    cs = measure.find_contours(arr, .5)
    polys = []
    for c in cs:
        if len(c) < 30:
            continue
        p = Polygon([(x, y) for y, x in c]).buffer(0)
        if p.area > 400:
            polys.append(p)
    # even-odd: nested contours become holes
    polys.sort(key=lambda p: -p.area)
    shape = None
    for p in polys:
        shape = p if shape is None else shape.symmetric_difference(p)
    return shape


def emblem():
    g = trace()
    minx, miny, maxx, maxy = g.bounds
    cx = (minx + maxx) / 2
    left = g.intersection(Polygon([(minx - 5, miny - 5), (cx, miny - 5), (cx, maxy + 5), (minx - 5, maxy + 5)]))
    sym = unary_union([left, affinity.scale(left, xfact=-1, origin=(cx, 0))])   # make it perfectly symmetric
    sym = sym.buffer(1.5).buffer(-1.5).simplify(.6)
    h = maxy - miny
    sym = affinity.translate(sym, -cx, -miny)
    return affinity.scale(sym, 1 / h, 1 / h, origin=(0, 0))


if __name__ == "__main__":
    import cairosvg
    from shaft import d_of
    e = emblem()
    print(e.bounds, e.geom_type)
    s = affinity.scale(e, 300, 300, origin=(0, 0))
    s = affinity.translate(s, 160, 10)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="320" height="320"><rect width="320" height="320" fill="#fff"/><path d="{d_of(s)}" fill="#000" fill-rule="evenodd"/></svg>'
    cairosvg.svg2png(bytestring=svg.encode(), write_to="/tmp/claude-0/-home-user--/635d9c1f-591e-5801-95b1-2aec957d93fb/scratchpad/trib.png")
