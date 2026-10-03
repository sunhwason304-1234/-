"""파크나라 CHAMPION 샤프트 랩 – 스플릿 버전 (40 x 380 mm).

트라이벌 문양을 세로 중심선에서 반으로 잘라
왼쪽 절반은 위쪽(불꽃이 위로), 오른쪽 절반은 아래쪽(불꽃이 헤드 쪽으로) 배치한다.
두 조각의 잘린 면을 금선으로 이어 CHAMPION을 감싸는 하나의 흐름으로 만든다.

재생성: FONT_DIR=<fontsource 패키지 폴더> python3 shaft-design/build_champion_split.py
"""
import math, os
from flame import flame
from build_champion import (HERE, W, H, CX, CINZEL, MONT, MONT_I, DEFS, WORD, KOR, TAG,
                            text_path, mark, truss, svg)

SX, SY = .40, .44            # 문양 배율 (반쪽 폭 50 → 20mm, 높이 160 → 70mm)
EDGE = 7.0                   # 잘린 면(금선)이 중심에서 떨어진 거리
TOP_Y, BOT_Y = 40, 330       # 위 조각 시작 / 아래 조각 끝
TOP_TIP = TOP_Y + 160 * SY   # 위 조각 뾰족한 끝
BOT_TIP = BOT_Y - 160 * SY   # 아래 조각 뾰족한 끝

CLIP = '''<clipPath id="halfL"><rect x="-10" y="-10" width="60" height="180"/></clipPath>
<clipPath id="halfR"><rect x="50" y="-10" width="60" height="180"/></clipPath>'''

def piece(tf, clip):
    """그림자 → 오렌지 외곽선 → 메탈 골드 본체."""
    return f'''<g transform="translate(.5 .7) {tf}" opacity=".7"><g clip-path="url(#{clip})">{flame("#000")}</g></g>
<g transform="{tf}"><g clip-path="url(#{clip})" stroke="#FF6A13" stroke-width="2.2" stroke-linejoin="round">{flame("#FF6A13")}</g></g>
<g transform="{tf}"><g clip-path="url(#{clip})">{flame("url(#goldY)")}</g></g>'''

def star(x, y, r):
    pts = " ".join(f"{x + (r if i % 2 == 0 else r*.42)*math.sin(i*math.pi/5):.3f},"
                   f"{y - (r if i % 2 == 0 else r*.42)*math.cos(i*math.pi/5):.3f}" for i in range(10))
    return f'<polygon points="{pts}" fill="url(#goldY)"/>'

def build():
    o = [f'<rect width="{W}" height="{H}" fill="url(#carbon)"/>',
         f'<rect width="{W}" height=".6" fill="url(#goldX)"/>',
         f'<rect y="{H-.6}" width="{W}" height=".6" fill="url(#goldX)"/>']

    # 상단 엠블럼 + 트러스
    o.append(f'<circle cx="{CX}" cy="15.5" r="11" fill="#000" stroke="url(#goldX)" stroke-width=".35"/>')
    o.append(f'<circle cx="{CX}" cy="15.5" r="10.1" fill="none" stroke="url(#goldX)" stroke-width=".15" stroke-dasharray=".5 .5"/>')
    o.append(f'<g transform="translate({CX - 56*.085:.3f} 6.6) scale(.085)">{mark("#F5F1E8", "url(#goldY)")}</g>')
    o.append(truss(30))

    # 글로우
    o.append(f'<ellipse cx="{CX - 3}" cy="{TOP_Y + 160*SY*.55:.2f}" rx="15" ry="36" fill="url(#glow)"/>')
    o.append(f'<ellipse cx="{CX + 3}" cy="{BOT_Y - 160*SY*.55:.2f}" rx="15" ry="36" fill="url(#glow)"/>')

    # 위 조각: 왼쪽 절반, 불꽃 위로. 잘린 면(x=50)을 CX+EDGE에 맞춤
    top_tf = f"translate({CX + EDGE - 50*SX:.3f} {TOP_Y}) scale({SX} {SY})"
    # 아래 조각: 오른쪽 절반을 상하 반전, 불꽃이 헤드 쪽으로. 잘린 면을 CX-EDGE에 맞춤
    bot_tf = f"translate({CX - EDGE - 50*SX:.3f} {BOT_Y}) scale({SX} {-SY})"
    o.append(piece(top_tf, "halfL"))
    o.append(piece(bot_tf, "halfR"))

    # 잘린 면을 잇는 금선: 위 조각의 단면 → CHAMPION 오른쪽 레일 → 아래 조각 끝
    o.append(f'<rect x="{CX + EDGE - .2:.2f}" y="{TOP_Y + 6}" width=".45" height="{BOT_TIP - TOP_Y - 6:.2f}" fill="url(#goldY)"/>')
    o.append(f'<rect x="{CX - EDGE - .25:.2f}" y="{TOP_TIP:.2f}" width=".45" height="{BOT_Y - 6 - TOP_TIP:.2f}" fill="url(#goldY)"/>')
    # 레일 끝 장식(다이아몬드)
    for x, y in ((CX + EDGE, BOT_TIP), (CX - EDGE, TOP_TIP)):
        o.append(f'<path d="M{x:.2f} {y-1.4:.2f} l1 1.4 l-1 1.4 l-1 -1.4z" fill="url(#goldY)"/>')

    # CHAMPION (두 조각 사이 중앙)
    size = 14.2
    p, w = text_path(CINZEL, "CHAMPION", size, 0, 0, track=1.0, anchor="middle")
    cap = size * .7
    cy = (TOP_TIP + BOT_TIP) / 2 + 3
    tf = f'translate({CX - cap/2:.3f} {cy:.2f}) rotate(90)'
    o.append(f'<g transform="translate(.45 .6)"><path transform="{tf}" d="{p}" fill="#000" opacity=".75"/></g>')
    o.append(f'<path transform="{tf}" d="{p}" fill="none" stroke="#FF6A13" stroke-width=".7" stroke-linejoin="round"/>')
    o.append(f'<path transform="{tf}" d="{p}" fill="url(#goldText)"/>')
    top = cy - w/2
    o += [star(CX, top - 4.2, 1.4), star(CX - 3.3, top - 3.4, .9), star(CX + 3.3, top - 3.4, .9)]

    # 보조 문구 (레일 바깥)
    s1, _ = text_path(MONT, "PARK GOLF  PROFESSIONAL SERIES", 1.8, 0, 0, track=.4, anchor="middle")
    o.append(f'<path transform="translate({CX + EDGE + 1.2:.3f} {cy:.2f}) rotate(90)" d="{s1}" fill="#E3CD98"/>')
    s2, _ = text_path(MONT_I, "PARKNARA", 1.9, 0, 0, track=.6, anchor="middle")
    o.append(f'<path transform="translate({CX - EDGE - 3.2:.3f} {cy:.2f}) rotate(90)" d="{s2}" fill="#FF8A1F"/>')

    # 오렌지 사선 포인트 (가장자리)
    o.append(f'<path d="M4.6 150 L7.6 144 V146.4 L5.8 150.2 V236 L4.6 238 Z" fill="url(#fire)"/>')
    o.append(f'<path d="M35.4 232 L32.4 238 V235.6 L34.2 231.8 V146 L35.4 144 Z" fill="url(#fireR)"/>')
    o += [f'<rect x="31.2" y="{60 + i*1.6:.2f}" width="3.4" height=".7" fill="url(#goldX)"/>' for i in range(8)]
    o += [f'<rect x="5.4" y="{306 + i*1.6:.2f}" width="3.4" height=".7" fill="url(#goldX)"/>' for i in range(8)]

    o.append(truss(334))

    # 하단 40mm: 파크나라 로고
    sc = 33 / 840
    o.append(f'<rect x="{CX - 6.2:.2f}" y="341.5" width="12.4" height="37" rx=".8" fill="#000" stroke="url(#goldX)" stroke-width=".25"/>')
    o.append(f'''<g transform="translate({CX + 180*sc/2:.3f} {360 - 840*sc/2:.3f}) rotate(90) scale({sc:.5f}) translate(-90 -54)">
  <g transform="translate(90 45) scale(.95)">{mark("#F5F1E8", "url(#goldY)")}</g>
  <path d="{WORD}" fill="#F5F1E8"/>
  <path d="{KOR}" fill="#E3CD98"/>
  <rect x="371.6" y="215.0" width="299.1" height="1.2" fill="#B8995A"/>
  <path d="{TAG}" fill="#E3CD98"/>
</g>''')
    return o

if __name__ == "__main__":
    s = svg(build()).replace("</defs>", CLIP + "\n</defs>", 1)
    open(os.path.join(HERE, "parknara-champion-split-40x380.svg"), "w").write(s)
    print("ok")
