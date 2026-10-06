"""Six-petal flower outline (recreated from ref/flower6_ref.png): petals flare towards the tip,
which is notched; drawn as a clean outline (engraving) plus a filled variant."""
import math
from pathlib import Path

from shapely import affinity
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from shaft import bezier, d_of

OUT = Path(__file__).parent / "flower6"
R = 50.0                      # petal tip radius


def petal():
    """One petal pointing up (y-down coords): narrow waist near the centre, straight flaring sides,
    shallow V notch across the tip - symmetric."""
    right = bezier((4.2, -8.5), (6.0, -24.0), (9.0, -36.0), (14.5, -46.0), 30)       # sides flare out towards the tip
    right += [(0.0, -41.8)]                                                          # straight, shallow V notch
    left = [(-x, y) for x, y in reversed(right)]
    return Polygon(right + left[1:]).buffer(-1.8, join_style="round").buffer(1.8, join_style="round")


def flower(stroke=None):
    p = petal()
    petals = [affinity.rotate(p, k * 60 + 10, origin=(0, 0)) for k in range(6)]
    if stroke is None:
        return unary_union(petals + [Point(0, 0).buffer(4.5)])
    rings = [q.difference(q.buffer(-stroke, join_style="round")) for q in petals]
    dot = Point(0, 0).buffer(2.4)
    return unary_union(rings + [dot])


def svg(body, size=120, bg=None, defs=""):
    b = f'<rect x="-60" y="-60" width="120" height="120" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size*8}" height="{size*8}" viewBox="-60 -60 120 120">'
            f'<defs>{defs}</defs>{b}{body}</svg>')


if __name__ == "__main__":
    import cairosvg, pymupdf
    OUT.mkdir(exist_ok=True)
    line = flower(stroke=3.2)
    fill = flower()
    files = {
        "flower6_line.svg": svg(f'<path d="{d_of(line)}" fill="#111" fill-rule="evenodd"/>'),
        "flower6_fill.svg": svg(f'<path d="{d_of(fill)}" fill="#111"/>'),
        "flower6_gold.svg": svg(f'<path d="{d_of(line)}" fill="url(#g)" fill-rule="evenodd"/>', bg="#0e0e0e",
                                defs='<linearGradient id="g" x1="0" y1="0" x2=".4" y2="1"><stop offset="0" stop-color="#f6e3a8"/>'
                                     '<stop offset=".5" stop-color="#d4ae5a"/><stop offset="1" stop-color="#ecd29a"/></linearGradient>'),
        # glowing ice-blue version like the source picture
        "flower6_glow.svg": svg(f'<path d="{d_of(fill)}" fill="#eaf8ff" filter="url(#glow)"/>'
                                f'<path d="{d_of(line)}" fill="#4aa6d8" fill-rule="evenodd"/>'
                                f'<circle r="2.6" fill="#fff"/>', bg="url(#bgg)",
                                defs='<radialGradient id="bgg"><stop offset="0" stop-color="#d9f2ff"/><stop offset=".45" stop-color="#5fb0e6"/>'
                                     '<stop offset="1" stop-color="#123c74"/></radialGradient>'
                                     '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3.5" result="b"/>'
                                     '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'),
    }
    for n, s in files.items():
        (OUT / n).write_text(s)
        cairosvg.svg2png(bytestring=s.encode(), write_to=str(OUT / n.replace(".svg", ".png")),
                         background_color=None if "gold" in n or "glow" in n else "white")
    cairosvg.svg2pdf(bytestring=files["flower6_line.svg"].encode(), write_to=str(OUT / "t.pdf"))
    d = pymupdf.open(OUT / "t.pdf"); d.save(OUT / "flower6_line.ai"); (OUT / "t.pdf").unlink()
    print("ok")
