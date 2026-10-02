"""파크나라 카본 샤프트 – 럭스 에디션 (40 x 380 mm).

레퍼런스(블랙 글로시 카본 + 실버 바로크 레이스 + 샴페인 골드 세리프 + 라임 포인트 + 크롬 페이드)의
절제된 컬러 조합을 파크나라 브랜드로 재구성.

재생성: FONT_DIR=<fontsource 패키지 폴더> python3 shaft-design/build_carbon_luxe.py
(추가 폰트: @fontsource/cinzel, @fontsource/montserrat)
"""
import os
from damask import cell
from build_champion import HERE, W, H, CX, font, text_path, mark, WORD, KOR, TAG

SERIF = font("cormorant-garamond-latin-600-normal.woff")
MONT = font("montserrat-latin-800-normal.woff")

LIME = "#C5DE3A"
CELL_W = 20                     # 다마스크 한 칸 = 20mm (둘레 40mm에 2칸 → 이음새 없이 맞물림)
CS = CELL_W / 100
LACE_END = 80                   # 레이스 영역 끝(가운데 뾰족한 부분)

def defs():
    return f'''<defs>
  <pattern id="carbon" width="1.6" height="1.6" patternUnits="userSpaceOnUse">
    <rect width="1.6" height="1.6" fill="#060607"/>
    <rect width=".8" height=".8" fill="#0B0B0D"/><rect x=".8" y=".8" width=".8" height=".8" fill="#0B0B0D"/>
    <rect width=".8" height=".18" fill="#111215"/><rect x=".8" y=".8" width=".18" height=".8" fill="#111215"/>
  </pattern>
  <linearGradient id="silver" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">
    <stop offset="0" stop-color="#9A9EA4"/><stop offset=".3" stop-color="#E6E8EB"/>
    <stop offset=".45" stop-color="#FFFFFF"/><stop offset=".6" stop-color="#D9DCE0"/>
    <stop offset=".85" stop-color="#A9ADB3"/><stop offset="1" stop-color="#8A8E94"/>
  </linearGradient>
  <linearGradient id="silverV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#B9BDC3"/>
  </linearGradient>
  <!-- 회전 글자용 샴페인 골드 (글자 기준 세로 = 샤프트 가로) -->
  <!-- 비비드 골드: 채도·명도를 올린 선명한 순금색 (골드 에디션의 CHAMPION 전용) -->
  <linearGradient id="goldVivid" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0" stop-color="#9A6A00"/><stop offset=".22" stop-color="#E3A81E"/>
    <stop offset=".42" stop-color="#FFD54A"/><stop offset=".52" stop-color="#FFF4C2"/>
    <stop offset=".64" stop-color="#FFCB2E"/><stop offset=".85" stop-color="#D09312"/><stop offset="1" stop-color="#8C5E00"/>
  </linearGradient>
  <linearGradient id="champ" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0" stop-color="#A88D55"/><stop offset=".45" stop-color="#F3E8C6"/>
    <stop offset=".65" stop-color="#DCC78F"/><stop offset="1" stop-color="#9C8048"/>
  </linearGradient>
  <linearGradient id="champX" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">
    <stop offset="0" stop-color="#8C7340"/><stop offset=".45" stop-color="#F3E8C6"/><stop offset="1" stop-color="#8C7340"/>
  </linearGradient>
  <linearGradient id="chromeFade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2E3135" stop-opacity="0"/><stop offset=".45" stop-color="#3B3E43" stop-opacity=".85"/>
    <stop offset=".8" stop-color="#8D9197"/><stop offset="1" stop-color="#C4C8CD"/>
  </linearGradient>
  <linearGradient id="chrome" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">
    <stop offset="0" stop-color="#9DA1A7"/><stop offset=".35" stop-color="#E4E6E9"/>
    <stop offset=".48" stop-color="#FFFFFF"/><stop offset=".62" stop-color="#CFD2D6"/><stop offset="1" stop-color="#9599A0"/>
  </linearGradient>
  <pattern id="brushed" width="{W}" height=".5" patternUnits="userSpaceOnUse">
    <rect width="{W}" height=".18" fill="#FFFFFF" opacity=".35"/><rect y=".3" width="{W}" height=".08" fill="#6E7278" opacity=".25"/>
  </pattern>
  <!-- 레이스 아래쪽: 가운데로 모이는 스캘럽 가장자리 -->
  <clipPath id="laceClip">
    <path d="{lace_edge()} V0 H0 Z"/>
  </clipPath>
  <!-- 실버 그라데이션을 다마스크 칸 좌표계로 옮긴 버전 (마스크 없이 벡터 유지 → AI/PDF에서 래스터화되지 않음) -->
  {cell_gradient("silverC0", 0, CS)}
  {cell_gradient("silverC1", CELL_W, CS)}
  {cell_gradient("silverOrn", CX - 50*.15, .15)}
</defs>'''

def lace_edge():
    """x=0 → 40 으로 이어지는 레이스 하단 곡선 (가운데가 가장 깊다)."""
    return ("M0 64 C3 68 6 66 8 70 C10 74 13 72 15 76 C17 79 19 78 20 " + str(LACE_END) +
            " C21 78 23 79 25 76 C27 72 30 74 32 70 C34 66 37 68 40 64")

def cell_gradient(gid, ox, sc):
    """바깥 좌표 0..W 의 실버 그라데이션을 translate(ox) scale(sc) 된 칸 좌표로 변환."""
    x1, x2 = (0 - ox) / sc, (W - ox) / sc
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1:.2f}" y1="0" x2="{x2:.2f}" y2="0">'
            '<stop offset="0" stop-color="#9A9EA4"/><stop offset=".3" stop-color="#E6E8EB"/>'
            '<stop offset=".45" stop-color="#FFFFFF"/><stop offset=".6" stop-color="#D9DCE0"/>'
            '<stop offset=".85" stop-color="#A9ADB3"/><stop offset="1" stop-color="#8A8E94"/></linearGradient>')

def lace_tiles():
    out = []
    for col in range(2):
        for row in range(-1, 4):
            y = 2 + row * 120 * CS + (60 * CS if col else 0)
            out.append(f'<g transform="translate({col*CELL_W} {y:.2f}) scale({CS})">{cell(f"url(#silverC{col})")}</g>')
    return "".join(out)

def rot_text(f, txt, size, cy, fill, track=0, x=CX, cap=.7):
    p, w = text_path(f, txt, size, 0, 0, track=track, anchor="middle")
    return f'<path transform="translate({x - size*cap/2:.3f} {cy:.2f}) rotate(90)" d="{p}" fill="{fill}"/>', w

def diamond(y, s=1.3):
    return (f'<path d="M{CX} {y-s:.2f} l{s*.75:.2f} {s} l{-s*.75:.2f} {s} l{-s*.75:.2f} {-s}z" '
            f'fill="none" stroke="url(#silver)" stroke-width=".28"/>'
            f'<path d="M{CX} {y-s*.45:.2f} l{s*.33:.2f} {s*.45:.2f} l{-s*.33:.2f} {s*.45:.2f} l{-s*.33:.2f} {-s*.45:.2f}z" fill="url(#silver)"/>')

def build(vivid=False):
    o = [f'<rect width="{W}" height="{H}" fill="url(#carbon)"/>']
    # 라임 포인트 밴드 + 실버 헤어라인
    # 실버 바로크 레이스
    o.append(f'<g clip-path="url(#laceClip)">{lace_tiles()}</g>')
    o.append(f'<path d="{lace_edge()}" fill="none" stroke="url(#silver)" stroke-width=".35"/>')
    o.append(f'<circle cx="{CX}" cy="{LACE_END + 2.2}" r=".55" fill="url(#silver)"/>')
    o.append(f'<rect width="{W}" height="1.6" fill="{LIME}"/>')
    o.append(f'<rect y="1.6" width="{W}" height=".3" fill="url(#silver)"/>')

    # CHAMPION – 메인 네임, 로고와 같은 세리프(Cormorant Garamond)로 크게
    _, w10 = text_path(SERIF, "CHAMPION", 10, 0, 0, track=2.3)
    size = 10 * 82 / w10                       # 길이 82mm에 맞춤
    if vivid:
        # 어두운 테두리를 살짝 깔아 금색 윤곽을 또렷하게
        t, _ = rot_text(SERIF, "CHAMPION", size, 137, "none", track=size * .23, cap=.63)
        o.append(t.replace('fill="none"', 'fill="none" stroke="#2A1A00" stroke-width=".45" stroke-linejoin="round"'))
    t, _ = rot_text(SERIF, "CHAMPION", size, 137, "url(#goldVivid)" if vivid else "url(#champ)", track=size * .23, cap=.63)
    o.append(t)
    # 이름 끝의 작은 표기 (레퍼런스의 '83' 자리)
    t, _ = rot_text(MONT, "PREMIUM", 1.5, 172.5, "#DCC78F", track=.35, x=CX + 5.6)
    o.append(t)

    # 실버 장식 한 송이
    o.append(f'<g transform="translate({CX - 50*.15:.2f} 185) scale(.15)">{cell("url(#silverOrn)")}</g>')

    # PARKNARA – 로고 원본 세리프 아웃라인, 작게
    w = 40
    k = w / 673
    o.append(f'<g transform="translate({CX} {240 - w/2:.2f}) rotate(90) scale({k:.4f}) translate(-253 -140)">'
             f'<path d="{WORD}" fill="url(#champ)"/></g>')
    _, wl = text_path(MONT, "MADE IN KOREA", 1.6, 0, 0, track=.3)
    m, _ = rot_text(MONT, "MADE IN KOREA", 1.6, 240 + w/2 + 3 + wl/2, "#DCC78F", track=.3)
    o.append(m)
    o.append(f'<rect x="{CX - .15:.2f}" y="{240 - w/2 - 5:.2f}" width=".3" height="2.6" fill="{LIME}"/>')

    # 다이아몬드 2개
    o += [diamond(288), diamond(294)]

    # 크롬 페이드 → 하단 40mm 실버 존
    o.append(f'<rect y="290" width="{W}" height="50" fill="url(#chromeFade)"/>')
    o.append(f'<rect y="340" width="{W}" height="40" fill="url(#chrome)"/>')
    o.append(f'<rect y="328" width="{W}" height="52" fill="url(#brushed)" opacity=".35"/>')
    o.append(f'<rect y="339.6" width="{W}" height=".4" fill="#1A1C1F"/>')
    o.append(f'<rect y="340" width="{W}" height=".25" fill="{LIME}"/>')

    # 파크나라 로고 (밝은 배경용 컬러) – 세로 배치
    sc = 31 / 840
    o.append(f'''<g transform="translate({CX + 180*sc/2:.3f} {360.5 - 840*sc/2:.3f}) rotate(90) scale({sc:.5f}) translate(-90 -54)">
  <g transform="translate(90 45) scale(.95)">
    <rect x="20" y="10" width="7" height="44" rx="2" fill="#15181B"/>
    <path d="M21.5 54 h4 l-0.8 128 h-2.4z" fill="#15181B"/>
    <path d="M8 182 h40 a8 8 0 0 1 0 16 h-40 a6 6 0 0 1 -6 -6 v-4 a6 6 0 0 1 6 -6z" fill="#15181B"/>
    <circle cx="68" cy="52" r="42" fill="#B8995A"/>
  </g>
  <path d="{WORD}" fill="#15181B"/>
  <path d="{KOR}" fill="#4A463F"/>
  <rect x="371.6" y="215.0" width="299.1" height="1.4" fill="#8C7038"/>
  <path d="{TAG}" fill="#4A463F"/>
</g>''')
    o.append(f'<rect y="{H - .5}" width="{W}" height=".5" fill="#2A2C30"/>')
    return o

if __name__ == "__main__":
    for name, vivid in (("parknara-carbon-luxe-40x380.svg", False), ("parknara-carbon-luxe-gold-40x380.svg", True)):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm">\n'
               + defs() + "\n" + "\n".join(build(vivid)) + "\n</svg>\n")
        open(os.path.join(HERE, name), "w").write(svg)
    print("ok")
