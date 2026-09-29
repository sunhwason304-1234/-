"""파크나라 로고 V2 (미니멀 럭셔리): 샤프트 + 공 = P 모노그램."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from build import font, text_path, OSW

SERIF = font("cormorant-garamond-latin-600-normal.woff")
KSERIF = font("nanum-myeongjo-korean-700-normal.woff")
MONT_L = font("montserrat-latin-500-normal.woff")

C = dict(ink="#15181B", champ="#B8995A", champ2="#E3CD98", cream="#F5F1E8", stone="#6E6A62")

DEFS = f'''<defs><linearGradient id="champ" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{C['champ2']}"/><stop offset=".6" stop-color="{C['champ']}"/><stop offset="1" stop-color="#8C7038"/>
</linearGradient></defs>'''

def mark(line, accent):
    """0..120 x 0..200. 가는 샤프트(세로획) + 헤드(발) + 공(P의 볼)."""
    return f'''<g>
  <rect x="20" y="10" width="7" height="44" rx="2" fill="{line}"/>
  <path d="M21.5 54 h4 l-0.8 128 h-2.4z" fill="{line}"/>
  <path d="M8 182 h40 a8 8 0 0 1 0 16 h-40 a6 6 0 0 1 -6 -6 v-4 a6 6 0 0 1 6 -6z" fill="{line}"/>
  <circle cx="68" cy="52" r="42" fill="{accent}"/>
  <path d="M36 52 a32 32 0 0 1 32 -32" fill="none" stroke="#FFFFFF" stroke-opacity=".35" stroke-width="2"/>
</g>'''

def svg(w, h, inner, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n{DEFS}\n{b}\n{inner}\n</svg>\n'

def words(x, y, main, sub, accent, anchor="start", scale=1.0):
    p, w = text_path(SERIF, "PARKNARA", 96*scale, x, y, track=22*scale, anchor=anchor)
    left = x - (w if anchor == "end" else w/2 if anchor == "middle" else 0)
    k, kw = text_path(KSERIF, "파크나라", 22*scale, left, y + 54*scale, track=6*scale)
    t, tw = text_path(MONT_L, "PARK GOLF SHAFT", 15*scale, left + w, y + 52*scale, track=6.5*scale, anchor="end")
    r1 = left + kw + 20*scale; r2 = left + w - tw - 20*scale
    return f'''<path d="{p}" fill="{main}"/>
<path d="{k}" fill="{sub}"/>
<rect x="{r1:.1f}" y="{y+45*scale:.1f}" width="{r2-r1:.1f}" height="{1*scale:.2f}" fill="{accent}"/>
<path d="{t}" fill="{sub}"/>''', w

def horizontal(dark=False):
    main = C['cream'] if dark else C['ink']; sub = C['champ2'] if dark else C['stone']
    wm, w = words(250, 170, main, sub, C['champ'])
    W = int(250 + w + 70)
    inner = f'<g transform="translate(90 45) scale(.95)">{mark(main, "url(#champ)")}</g>\n{wm}'
    return svg(W, 300, inner, C['ink'] if dark else None)

def stacked(dark=False):
    main = C['cream'] if dark else C['ink']; sub = C['champ2'] if dark else C['stone']
    wm, w = words(400, 440, main, sub, C['champ'], anchor="middle", scale=1.0)
    inner = f'<g transform="translate(327 60) scale(1.3)">{mark(main, "url(#champ)")}</g>\n{wm}'
    return svg(800, 560, inner, C['ink'] if dark else None)

def symbol():
    inner = f'''<rect width="512" height="512" fill="{C['ink']}"/>
<rect x="28" y="28" width="456" height="456" fill="none" stroke="{C['champ']}" stroke-width="1.5" opacity=".6"/>
<g transform="translate(166 90) scale(1.6)">{mark(C['cream'], "url(#champ)")}</g>'''
    return svg(512, 512, inner)

if __name__ == "__main__":
    out = os.path.dirname(os.path.abspath(__file__))
    files = {
        "parknara-v2-logo.svg": horizontal(),
        "parknara-v2-logo-dark.svg": horizontal(True),
        "parknara-v2-stacked.svg": stacked(),
        "parknara-v2-stacked-dark.svg": stacked(True),
        "parknara-v2-symbol.svg": symbol(),
    }
    for n, s in files.items():
        open(os.path.join(out, n), "w").write(s)
    print("\n".join(files))
