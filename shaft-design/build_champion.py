"""파크나라 CHAMPION 파크골프채 샤프트 랩 디자인 (40 x 380 mm).

좌표 단위 = mm. 폭 40mm는 샤프트 둘레를 감싸는 방향이므로
핵심 요소(트라이벌, CHAMPION, 로고)는 가운데 20mm 안에 배치한다.

재생성: FONT_DIR=<fontsource 패키지 폴더> python3 shaft-design/build_champion.py
(필요 폰트: @fontsource/cinzel, @fontsource/montserrat, pip install fonttools)
"""
import glob, os, re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from flame import flame

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.environ.get("FONT_DIR", ".")
def font(pat): return TTFont(glob.glob(os.path.join(FONTS, "*/package/files/" + pat))[0])
CINZEL = font("cinzel-latin-900-normal.woff")
MONT = font("montserrat-latin-800-normal.woff")
MONT_I = font("montserrat-latin-900-italic.woff")

def text_path(f, text, size, x, y, track=0, anchor="start"):
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    s = size / f["head"].unitsPerEm; hmtx = f["hmtx"]
    names = [cmap[ord(c)] for c in text]
    width = sum(hmtx[n][0] * s for n in names) + track * (len(names) - 1)
    cx = x - (width if anchor == "end" else width / 2 if anchor == "middle" else 0)
    pen = SVGPathPen(gs)
    for n in names:
        gs[n].draw(TransformPen(pen, (s, 0, 0, -s, cx, y))); cx += hmtx[n][0] * s + track
    return pen.getCommands(), width

W, H = 40, 380
CX = W / 2

# 파크나라 V2 가로형 로고(아웃라인 처리된 원본)를 그대로 가져온다.
_logo = open(os.path.join(HERE, "..", "logo", "v2", "parknara-v2-logo-dark.svg")).read()
_paths = re.findall(r'<path d="([^"]{200,})" fill="([^"]+)"/>', _logo)
WORD, KOR, TAG = (p[0] for p in _paths)

def mark(line, accent):
    """V2 P 모노그램 (0..120 x 0..200): 샤프트 + 헤드 + 공."""
    return f'''<g>
  <rect x="20" y="10" width="7" height="44" rx="2" fill="{line}"/>
  <path d="M21.5 54 h4 l-0.8 128 h-2.4z" fill="{line}"/>
  <path d="M8 182 h40 a8 8 0 0 1 0 16 h-40 a6 6 0 0 1 -6 -6 v-4 a6 6 0 0 1 6 -6z" fill="{line}"/>
  <circle cx="68" cy="52" r="42" fill="{accent}"/>
  <path d="M36 52 a32 32 0 0 1 32 -32" fill="none" stroke="#FFFFFF" stroke-opacity=".45" stroke-width="2"/>
</g>'''

DEFS = f'''<defs>
  <!-- 금속 골드: 가로 방향으로 하이라이트를 줘서 원통에 감았을 때 광택이 산다 -->
  <linearGradient id="goldX" gradientUnits="userSpaceOnUse" x1="8" y1="0" x2="32" y2="0">
    <stop offset="0" stop-color="#7A4E10"/><stop offset=".22" stop-color="#C99332"/>
    <stop offset=".42" stop-color="#FFF3C4"/><stop offset=".55" stop-color="#F2CF6B"/>
    <stop offset=".78" stop-color="#B07A22"/><stop offset="1" stop-color="#6E440C"/>
  </linearGradient>
  <!-- 회전된 글자용: 글자 기준 세로(y) = 샤프트 가로 방향 -->
  <linearGradient id="goldText" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0" stop-color="#7A4E10"/><stop offset=".2" stop-color="#C99332"/>
    <stop offset=".45" stop-color="#FFF3C4"/><stop offset=".58" stop-color="#F2CF6B"/>
    <stop offset=".82" stop-color="#B07A22"/><stop offset="1" stop-color="#6E440C"/>
  </linearGradient>
  <linearGradient id="goldY" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFF6D2"/><stop offset=".35" stop-color="#F4CF68"/>
    <stop offset=".7" stop-color="#C98E2C"/><stop offset="1" stop-color="#8A5814"/>
  </linearGradient>
  <linearGradient id="fire" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0" stop-color="#FFD25A"/><stop offset=".45" stop-color="#FF8A1F"/><stop offset="1" stop-color="#D9360B"/>
  </linearGradient>
  <linearGradient id="fireR" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFD25A"/><stop offset=".5" stop-color="#FF8A1F"/><stop offset="1" stop-color="#D9360B"/>
  </linearGradient>
  <radialGradient id="glow" cx=".5" cy=".55" r=".5">
    <stop offset="0" stop-color="#FF7A1A" stop-opacity=".55"/><stop offset=".6" stop-color="#C2410C" stop-opacity=".15"/>
    <stop offset="1" stop-color="#C2410C" stop-opacity="0"/>
  </radialGradient>
  <!-- 카본 직조 텍스처 -->
  <pattern id="carbon" width="2" height="2" patternUnits="userSpaceOnUse">
    <rect width="2" height="2" fill="#0C0C0E"/>
    <rect width="1" height="1" fill="#121316"/><rect x="1" y="1" width="1" height="1" fill="#121316"/>
    <rect width="1" height=".25" fill="#17181B"/><rect x="1" y="1" width=".25" height="1" fill="#17181B"/>
  </pattern>
  <linearGradient id="fadeV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000" stop-opacity=".0"/><stop offset=".5" stop-color="#000" stop-opacity=".55"/>
    <stop offset="1" stop-color="#000" stop-opacity=".0"/>
  </linearGradient>
</defs>'''

def truss(y, h=5):
    """레퍼런스의 트러스(지그재그) 밴드."""
    n = 8; step = W / n; pts = []
    for i in range(n + 1):
        pts.append(f"{i*step:.2f},{y + (h - .6 if i % 2 else .6):.2f}")
    zz = " ".join(pts)
    zz2 = " ".join(f"{i*step:.2f},{y + (.6 if i % 2 else h - .6):.2f}" for i in range(n + 1))
    return f'''<g>
  <rect x="0" y="{y}" width="{W}" height="{h}" fill="#000" opacity=".6"/>
  <rect x="0" y="{y}" width="{W}" height=".45" fill="url(#goldX)"/>
  <rect x="0" y="{y + h - .45}" width="{W}" height=".45" fill="url(#goldX)"/>
  <polyline points="{zz}" fill="none" stroke="url(#goldX)" stroke-width=".32"/>
  <polyline points="{zz2}" fill="none" stroke="url(#goldX)" stroke-width=".32" opacity=".55"/>
</g>'''

def speed_frames():
    """레퍼런스의 오렌지 스피드 프레임 (사선 끝처리)."""
    L = f'''<path d="M10.2 124 L5.2 134 V300 L9.5 309 V306 L6.6 300 V134.6 L11.6 124 Z" fill="url(#fire)"/>
  <path d="M8.2 140 h.7 v150 h-.7 z" fill="url(#goldY)" opacity=".9"/>'''
    R = f'''<path d="M29.8 150 L34.8 160 V318 L29.8 328 V325.4 L33.4 318 V160.6 L28.4 150 Z" fill="url(#fireR)"/>
  <path d="M31.1 166 h.7 v148 h-.7 z" fill="url(#goldY)" opacity=".9"/>'''
    ticks = "".join(f'<rect x="{29.6 + (i % 2) * .0:.2f}" y="{132 + i*1.6:.2f}" width="3.6" height=".7" fill="url(#goldX)"/>' for i in range(9))
    ticks2 = "".join(f'<rect x="6.8" y="{312 + i*1.6:.2f}" width="3.6" height=".7" fill="url(#goldX)"/>' for i in range(9))
    return L + R + ticks + ticks2

def build():
    out = [f'<rect width="{W}" height="{H}" fill="url(#carbon)"/>']
    # 상단 그라데이션 & 하단 마감 금선
    out.append(f'<rect width="{W}" height=".6" fill="url(#goldX)"/>')
    out.append(f'<rect y="{H-.6}" width="{W}" height=".6" fill="url(#goldX)"/>')

    # ── 상단 로고 존 (0~30): P 모노그램 + 엠블럼 링
    out.append(f'<circle cx="{CX}" cy="15.5" r="11" fill="#000" stroke="url(#goldX)" stroke-width=".35"/>')
    out.append(f'<circle cx="{CX}" cy="15.5" r="10.1" fill="none" stroke="url(#goldX)" stroke-width=".15" stroke-dasharray=".5 .5"/>')
    out.append(f'<g transform="translate({CX - 56*.085:.3f} 6.6) scale(.085)">{mark("#F5F1E8", "url(#goldY)")}</g>')
    out.append(truss(30))

    # ── 메인 존: 트라이벌 플레임 (두 번째 이미지 재해석, 벡터)
    fx, fy, sx, sy = CX - 50*.25, 41, .25, .44
    out.append(f'<ellipse cx="{CX}" cy="{fy + 160*sy*.55:.2f}" rx="17" ry="38" fill="url(#glow)"/>')
    # 그림자 → 오렌지 외곽선 → 골드 본체 순으로 쌓아 입체감
    out.append(f'<g transform="translate({fx+.5:.2f} {fy+.7:.2f}) scale({sx} {sy})" opacity=".7">{flame("#000")}</g>')
    out.append(f'<g transform="translate({fx:.2f} {fy:.2f}) scale({sx} {sy})" stroke="#FF6A13" stroke-width="2.2" stroke-linejoin="round">{flame("#FF6A13")}</g>')
    out.append(f'<g transform="translate({fx:.2f} {fy:.2f}) scale({sx} {sy})">{flame("url(#goldY)")}</g>')

    out.append(speed_frames())

    # CHAMPION (세로, 레퍼런스처럼 위→아래로 읽힘)
    size = 15.2
    p, w = text_path(CINZEL, "CHAMPION", size, 0, 0, track=1.2, anchor="middle")
    cy = 222
    cap = size * .7
    # 텍스트 기준선이 회전 후 x축이 되므로 cap 높이의 절반만큼 이동해 가운데 정렬
    tf = f'translate({CX - cap/2:.3f} {cy}) rotate(90)'
    out.append(f'<g transform="translate(.45 .6)"><path transform="{tf}" d="{p}" fill="#000" opacity=".75"/></g>')
    out.append(f'<path transform="{tf}" d="{p}" fill="none" stroke="#FF6A13" stroke-width=".7" stroke-linejoin="round"/>')
    out.append(f'<path transform="{tf}" d="{p}" fill="url(#goldText)"/>')
    # CHAMPION 양 옆 가는 금선
    top, bot = cy - w/2, cy + w/2
    out.append(f'<rect x="{CX - cap/2 - 1.6:.2f}" y="{top:.2f}" width=".22" height="{w:.2f}" fill="url(#goldY)" opacity=".85"/>')
    out.append(f'<rect x="{CX + cap/2 + 1.4:.2f}" y="{top:.2f}" width=".22" height="{w:.2f}" fill="url(#goldY)" opacity=".85"/>')
    # 별(챔피언 상징) 3개
    def star(x, y, r):
        import math
        pts = " ".join(f"{x + (r if i%2==0 else r*.42)*math.sin(i*math.pi/5):.3f},{y - (r if i%2==0 else r*.42)*math.cos(i*math.pi/5):.3f}" for i in range(10))
        return f'<polygon points="{pts}" fill="url(#goldY)"/>'
    out += [star(CX, top - 5.5, 1.5), star(CX - 3.6, top - 4.6, 1.0), star(CX + 3.6, top - 4.6, 1.0)]

    # 시리즈 문구 (세로, 작은 글씨)
    s1, sw = text_path(MONT, "PARK GOLF  PROFESSIONAL SERIES", 1.9, 0, 0, track=.42, anchor="middle")
    out.append(f'<path transform="translate({CX + cap/2 + 2.6:.3f} {cy}) rotate(90)" d="{s1}" fill="#E3CD98"/>')
    s2, _ = text_path(MONT_I, "PARKNARA", 1.9, 0, 0, track=.6, anchor="middle")
    out.append(f'<path transform="translate({CX - cap/2 - 4.1:.3f} {cy}) rotate(90)" d="{s2}" fill="#FF8A1F"/>')

    # 모델 넘버 배지
    n1, _ = text_path(MONT_I, "01", 3.2, 0, 0, anchor="middle")
    out.append(f'<path transform="translate({CX - 1.1:.3f} 312) rotate(90)" d="{n1}" fill="url(#goldText)"/>')
    out.append(f'<rect x="{CX - 3:.2f}" y="307.2" width="6" height="9.6" rx=".6" fill="none" stroke="url(#goldX)" stroke-width=".25"/>')

    out.append(truss(334))

    # ── 하단 40mm 존: 파크나라 로고 (가로형을 세로로 회전)
    # 원본 로고 내용 영역 ≈ x 90..930, y 54..234 (996x300 캔버스)
    sc = 33 / 840
    lx, ly = 90, 54
    logo = f'''<g transform="translate({CX + 180*sc/2:.3f} {360 - 840*sc/2:.3f}) rotate(90) scale({sc:.5f}) translate({-lx} {-ly})">
  <g transform="translate(90 45) scale(.95)">{mark("#F5F1E8", "url(#goldY)")}</g>
  <path d="{WORD}" fill="#F5F1E8"/>
  <path d="{KOR}" fill="#E3CD98"/>
  <rect x="371.6" y="215.0" width="299.1" height="1.2" fill="#B8995A"/>
  <path d="{TAG}" fill="#E3CD98"/>
</g>'''
    out.append(f'<rect x="{CX - 6.2:.2f}" y="341.5" width="12.4" height="37" rx=".8" fill="#000" stroke="url(#goldX)" stroke-width=".25"/>')
    out.append(logo)
    return out

def svg(inner, print_size=True):
    size = f'width="{W}mm" height="{H}mm"' if print_size else f'width="{W*10}" height="{H*10}"'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" {size}>\n{DEFS}\n' + "\n".join(inner) + "\n</svg>\n"

if __name__ == "__main__":
    body = build()
    open(os.path.join(HERE, "parknara-champion-shaft-40x380.svg"), "w").write(svg(body))
    print("ok")
