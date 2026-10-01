"""Trace the client's dove ornament (ref/ornament_ref.png) and return it with the dove removed."""
import numpy as np
from PIL import Image, ImageFilter
from skimage import measure
from shapely.geometry import Polygon
from shapely.ops import unary_union


def trace(path="ref/ornament_ref.png", up=4):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(int)
    gold = (a[:, :, 0] > 110) & (a[:, :, 0] - a[:, :, 2] > 35)
    m = Image.fromarray((gold * 255).astype("uint8")).resize((im.width * up, im.height * up), Image.LANCZOS)
    arr = np.asarray(m.filter(ImageFilter.GaussianBlur(up * .8))) / 255
    polys = []
    for c in measure.find_contours(arr, .5):
        if len(c) < 20:
            continue
        p = Polygon([(x / up, y / up) for y, x in c]).buffer(0)
        if p.area > 4:
            polys.append(p)
    polys.sort(key=lambda p: -p.area)
    shape = None
    for p in polys:
        shape = p if shape is None else shape.symmetric_difference(p)
    return shape


def without_dove():
    g = trace()
    parts = list(getattr(g, "geoms", [g]))
    # the dove sits in the upper-right of the picture
    # (plus its separate wing-tip piece): everything whose centre lies right of x=140 and above y=190
    keep = [p for p in parts if not (p.centroid.x > 140 and p.centroid.y < 190)]
    return unary_union(keep).buffer(.4).buffer(-.4).simplify(.25)


if __name__ == "__main__":
    import cairosvg
    from shapely import affinity
    from shaft import d_of
    g = without_dove()
    minx, miny, maxx, maxy = g.bounds
    pad = 12
    W, H = maxx - minx + pad * 2, maxy - miny + pad * 2
    gg = affinity.translate(g, pad - minx, pad - miny)
    defs = ('<defs><linearGradient id="g" x1="0" y1="0" x2=".4" y2="1"><stop offset="0" stop-color="#f6e3a8"/>'
            '<stop offset=".45" stop-color="#d4ae5a"/><stop offset=".65" stop-color="#b18a3a"/><stop offset="1" stop-color="#ecd29a"/></linearGradient></defs>')
    gold = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*4:.0f}" height="{H*4:.0f}" viewBox="0 0 {W:.1f} {H:.1f}">{defs}'
            f'<rect width="{W:.1f}" height="{H:.1f}" fill="#000"/><path d="{d_of(gg)}" fill="url(#g)" fill-rule="evenodd"/></svg>')
    line = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*4:.0f}" height="{H*4:.0f}" viewBox="0 0 {W:.1f} {H:.1f}">'
            f'<path d="{d_of(gg)}" fill="#000" fill-rule="evenodd"/></svg>')
    import pathlib; out = pathlib.Path("ornament"); out.mkdir(exist_ok=True)
    (out / "ornament_no_dove_gold.svg").write_text(gold)
    (out / "ornament_no_dove.svg").write_text(line)
    cairosvg.svg2png(bytestring=gold.encode(), write_to=str(out / "ornament_no_dove_gold.png"))
    cairosvg.svg2png(bytestring=line.encode(), write_to=str(out / "ornament_no_dove.png"), background_color="white")
    import pymupdf
    cairosvg.svg2pdf(bytestring=line.encode(), write_to=str(out / "t.pdf"))
    d = pymupdf.open(out / "t.pdf"); d.save(out / "ornament_no_dove.ai"); (out / "t.pdf").unlink()
    print("ok", W, H)
