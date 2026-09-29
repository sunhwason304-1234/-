"""파크나라 로고 빌드 스크립트: 폰트를 아웃라인(path)으로 변환해 독립 실행 SVG 생성."""
import glob, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = os.environ.get("FONT_DIR", ".")
def font(pat): return TTFont(glob.glob(os.path.join(FONTS, "*/package/files/" + pat))[0])
MONT = font("montserrat-latin-900-italic.woff")
OSW = font("oswald-latin-600-normal.woff")
HAN = font("black-han-sans-korean-400-normal.woff")

def text_path(f, text, size, x, y, track=0, anchor="start"):
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    upm = f["head"].unitsPerEm; s = size / upm
    hmtx = f["hmtx"]
    names = [cmap[ord(c)] for c in text]
    width = sum(hmtx[n][0] * s for n in names) + track * (len(names) - 1)
    cx = x - (width if anchor == "end" else width / 2 if anchor == "middle" else 0)
    pen = SVGPathPen(gs); out = []
    for n in names:
        tp = TransformPen(pen, (s, 0, 0, -s, cx, y))
        gs[n].draw(tp); cx += hmtx[n][0] * s + track
    return pen.getCommands(), width

C = dict(green="#0E3B2C", green2="#1F6B4A", gold="#D4A83A", gold2="#F2D27A", ink="#0B1A14", white="#FFFFFF", cream="#F6F1E4")

def defs(dark=False):
    return f'''<defs>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{C['gold2']}"/><stop offset=".55" stop-color="{C['gold']}"/><stop offset="1" stop-color="#9C7420"/>
  </linearGradient>
  <linearGradient id="shaft" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{'#8FA79B' if dark else '#2A5A45'}"/><stop offset=".45" stop-color="{'#FFFFFF' if dark else '#6FA58A'}"/><stop offset="1" stop-color="{'#8FA79B' if dark else C['green']}"/>
  </linearGradient>
</defs>'''

def symbol(dark=False, mono=None):
    """P 모노그램: 세로획 = 샤프트(그립+헤드), 볼 = 스윙 궤적 + 공. 200x200 좌표계."""
    g = mono or ("url(#gold)")
    body = mono or (C['white'] if dark else C['green'])
    shaft = mono or "url(#shaft)"
    ball = mono or (C['white'] if dark else C['white'])
    ballstroke = mono or (C['gold'] if not dark else C['gold'])
    return f'''<g transform="skewX(-8) translate(18 0)">
  <!-- grip -->
  <path d="M63 16 h20 a5 5 0 0 1 5 5 v58 l-3 5 h-24 l-3 -5 v-58 a5 5 0 0 1 5 -5z" fill="{body}"/>
  <path d="M60 28 l26 -6 M60 40 l26 -6 M60 52 l26 -6 M60 64 l26 -6 M60 76 l26 -6" stroke="{C['green'] if dark and not mono else (C['white'] if not mono else 'none')}" stroke-width="2.2" opacity=".3"/>
  <!-- shaft (tapered) -->
  <path d="M65 84 h16 l-3 78 h-10z" fill="{shaft}"/>
  <!-- club head -->
  <path d="M50 158 h58 c10 0 16 4 18 10 l2 8 c1 6 -3 10 -10 10 h-66 c-6 0 -9 -4 -9 -10 v-6 c0 -8 3 -12 7 -12z" fill="{body}"/>
  <path d="M58 180 h56" stroke="{mono or C['gold']}" stroke-width="3" stroke-linecap="round"/>
  <!-- swing arc = P bowl -->
  <path d="M96 30 H122 A48 48 0 0 1 122 126 H96" fill="none" stroke="{g}" stroke-width="18" stroke-linecap="butt"/>
  <!-- ball -->
  <circle cx="122" cy="78" r="15" fill="{ball}" stroke="{ballstroke}" stroke-width="{0 if mono else 3}"/>
  {'' if mono else f'<g fill="{C["gold"]}" opacity=".45"><circle cx="116" cy="73" r="2"/><circle cx="125" cy="71" r="2"/><circle cx="120" cy="81" r="2"/><circle cx="129" cy="79" r="2"/><circle cx="124" cy="88" r="1.8"/></g>'}
</g>'''

def wordmark(x, y, dark=False, mono=None, scale=1.0):
    main = mono or (C['white'] if dark else C['green'])
    acc = mono or "url(#gold)"
    sub = mono or (C['gold2'] if dark else C['green2'])
    p1, w1 = text_path(MONT, "PARK", 118*scale, x, y, track=-2)
    p2, w2 = text_path(MONT, "NARA", 118*scale, x + w1 + 6*scale, y, track=-2)
    total = w1 + 6*scale + w2
    k, kw = text_path(HAN, "파크나라", 44*scale, x + 6*scale, y + 62*scale, track=6*scale)
    t, tw = text_path(OSW, "PARK GOLF SHAFT", 24*scale, x + total, y + 58*scale, track=7*scale, anchor="end")
    rule_x1 = x + 6*scale + kw + 18*scale; rule_x2 = x + total - tw - 18*scale
    return f'''<path d="{p1}" fill="{main}"/><path d="{p2}" fill="{acc}"/>
<path d="{k}" fill="{main}"/>
<rect x="{rule_x1:.1f}" y="{y+44*scale:.1f}" width="{max(rule_x2-rule_x1,0):.1f}" height="{3*scale:.1f}" fill="{acc}"/>
<path d="{t}" fill="{sub}"/>''', total

def svg(w, h, inner, bg=None, dark=False):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n{defs(dark)}\n{b}\n{inner}\n</svg>\n'

def horizontal(dark=False, mono=None, bg=None):
    wm, tw = wordmark(270, 178, dark, mono)
    W = int(270 + tw + 60)
    return svg(W, 300, f'<g transform="translate(40 50)">{symbol(dark, mono)}</g>\n{wm}', bg, dark)

def emblem(dark=False, bg=None):
    ring = C['gold']; fill = C['green']
    # 원형 엠블럼 + 원형 텍스트 대신 상/하 라벨
    top, tw = text_path(OSW, "PARKNARA", 30, 256, 92, track=10, anchor="middle")
    bot, bw = text_path(OSW, "PARK GOLF SHAFT", 24, 256, 400, track=6, anchor="middle")
    est, _ = text_path(OSW, "PREMIUM", 16, 256, 430, track=8, anchor="middle")
    inner = f'''<circle cx="256" cy="256" r="240" fill="{fill}"/>
<circle cx="256" cy="256" r="226" fill="none" stroke="url(#gold)" stroke-width="4"/>
<circle cx="256" cy="256" r="214" fill="none" stroke="url(#gold)" stroke-width="1.5" opacity=".6"/>
<path d="{top}" fill="url(#gold)"/>
<path d="M150 104 h34 M328 104 h34" stroke="url(#gold)" stroke-width="2"/>
<g transform="translate(154 122) scale(1.08)">{symbol(True)}</g>
<path d="{bot}" fill="{C['white']}"/>
<path d="{est}" fill="url(#gold)" opacity=".8"/>
<path d="M186 424 l6 -6 6 6 -6 6z M314 424 l6 -6 6 6 -6 6z" fill="url(#gold)"/>'''
    return svg(512, 512, inner, bg, True)

def icon():
    inner = f'''<rect width="512" height="512" rx="112" fill="{C['green']}"/>
<rect x="14" y="14" width="484" height="484" rx="100" fill="none" stroke="url(#gold)" stroke-width="4" opacity=".7"/>
<g transform="translate(62 50) scale(2)">{symbol(True)}</g>'''
    return svg(512, 512, inner, None, True)

if __name__ == "__main__":
    out = os.path.dirname(os.path.abspath(__file__))
    files = {
        "parknara-logo.svg": horizontal(),
        "parknara-logo-dark.svg": horizontal(dark=True, bg=C['green']),
        "parknara-logo-black.svg": horizontal(mono=C['ink']),
        "parknara-logo-white.svg": horizontal(mono=C['white'], bg=C['ink']),
        "parknara-emblem.svg": emblem(),
        "parknara-icon.svg": icon(),
    }
    for n, s in files.items():
        open(os.path.join(out, n), "w").write(s)
    print("\n".join(files))
