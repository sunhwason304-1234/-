"""할랄 현장심사 준비 문서용 예시 도안(PNG)을 생성한다."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "images"
OUT.mkdir(exist_ok=True)

FD = "/usr/share/fonts/truetype/nanum/"
REG = FD + "NanumGothic.ttf"
BOLD = FD + "NanumGothicBold.ttf"
SQB = FD + "NanumSquareB.ttf"

GREEN, GREEN_L = "#2E7D32", "#E8F5E9"
YELLOW, YELLOW_L = "#F9A825", "#FFF8E1"
RED, RED_L = "#C62828", "#FFEBEE"
ORANGE, ORANGE_L = "#EF6C00", "#FFF3E0"
BLUE, BLUE_L = "#1565C0", "#E3F2FD"
GRAY, GRAY_L = "#424242", "#EEEEEE"
PURPLE, PURPLE_L = "#6A1B9A", "#F3E5F5"
INK = "#212121"
MUTED = "#616161"


def f(size, bold=False, sq=False):
    return ImageFont.truetype(SQB if sq else (BOLD if bold else REG), size)


def canvas(w, h, bg="white"):
    im = Image.new("RGB", (w, h), bg)
    return im, ImageDraw.Draw(im)


def ctext(d, box, text, font, fill=INK, spacing=6):
    x0, y0, x1, y1 = box
    bb = d.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.multiline_text(((x0 + x1 - tw) / 2, (y0 + y1 - th) / 2 - bb[1]), text, font=font,
                     fill=fill, spacing=spacing, align="center")


def title(d, w, text, sub=None):
    d.rectangle([0, 0, w, 70], fill=GREEN)
    ctext(d, (0, 0, w, 70), text, f(32, sq=True), "white")
    if sub:
        ctext(d, (0, 72, w, 108), sub, f(20), MUTED)


def arrow(d, p0, p1, fill=GRAY, width=5, head=16):
    import math
    d.line([p0, p1], fill=fill, width=width)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    a1, a2 = ang + math.radians(150), ang - math.radians(150)
    d.polygon([p1, (p1[0] + head * math.cos(a1), p1[1] + head * math.sin(a1)),
               (p1[0] + head * math.cos(a2), p1[1] + head * math.sin(a2))], fill=fill)


def rbox(d, box, fill, outline=None, r=16, w=3):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=w)


def save(im, name):
    im.save(OUT / name, "PNG", optimize=True)


# 1. 현장심사 흐름도 ----------------------------------------------------------
def img_audit_flow():
    W, H = 1600, 560
    im, d = canvas(W, H)
    title(d, W, "현장심사 진행 흐름 (예시)")
    steps = [("①", "개회 회의", "심사 범위·일정\n확인"), ("②", "서류 확인", "매뉴얼·인증서\n기록 대조"),
             ("③", "현장 순회", "입고→창고→생산\n→포장→출하"), ("④", "인터뷰", "책임자·작업자\n질의응답"),
             ("⑤", "샘플 채취", "돼지DNA·알코올\n검사(필요 시)"), ("⑥", "종료 회의", "부적합 통보\n시정 기한")]
    bw, gap, y0 = 220, 44, 130
    x = (W - (bw * 6 + gap * 5)) // 2
    cols = [GREEN, BLUE, ORANGE, PURPLE, RED, GREEN]
    for i, (n, t, s) in enumerate(steps):
        rbox(d, (x, y0, x + bw, y0 + 250), "white", cols[i], 18, 4)
        d.rounded_rectangle((x, y0, x + bw, y0 + 90), 18, fill=cols[i])
        d.rectangle((x, y0 + 60, x + bw, y0 + 90), fill=cols[i])
        ctext(d, (x, y0, x + bw, y0 + 90), f"{n} {t}", f(28, sq=True), "white")
        ctext(d, (x, y0 + 95, x + bw, y0 + 250), s, f(22), INK)
        if i < 5:
            arrow(d, (x + bw + 4, y0 + 125), (x + bw + gap - 4, y0 + 125), GRAY, 5, 14)
        x += bw + gap
    rbox(d, (120, 420, W - 120, 520), YELLOW_L, YELLOW, 14, 3)
    ctext(d, (120, 420, W - 120, 520),
          "핵심 원칙 : 서류에 쓴 내용  =  현장에서 보이는 모습  =  직원이 말하는 내용\n(세 가지가 일치해야 합격)",
          f(24, bold=True), INK)
    save(im, "01_심사흐름.png")


# 2. 원료창고 배치도 ----------------------------------------------------------
def img_warehouse_layout():
    W, H = 1600, 1100
    im, d = canvas(W, H, "#FAFAFA")
    title(d, W, "원재료 창고 구역 배치도 (평면 예시)", "바닥 라인 색상 = 구역 색상 · 화살표 = 원료 이동 동선")
    X0, Y0, X1, Y1 = 80, 130, 1520, 930
    d.rectangle((X0, Y0, X1, Y1), fill="white", outline=INK, width=6)
    # 입고 도크
    d.rectangle((X0 - 6, 380, X0 + 6, 560), fill="white")
    ctext(d, (0, 395, X0 - 6, 450), "입고\n도크", f(20, bold=True), INK)

    def zone(box, col, light, name, sub):
        x0, y0, x1, y1 = box
        d.rectangle(box, fill=light)
        # 바닥 라인 (두꺼운 테이프)
        d.rectangle(box, outline=col, width=12)
        d.rectangle((x0 + 18, y0 + 18, x1 - 18, y0 + 70), fill=col)
        ctext(d, (x0 + 18, y0 + 18, x1 - 18, y0 + 70), name, f(26, sq=True), "white")
        ctext(d, (x0, y0 + 75, x1, y0 + 130), sub, f(20), INK)

    zone((120, 170, 470, 560), YELLOW, YELLOW_L, "검수 대기", "입고 원료\n검수 전 보관")
    zone((120, 600, 470, 900), RED, RED_L, "부적합 격리", "불합격·만료·파손\n사용 금지 (시건)")
    zone((520, 170, 1160, 720), GREEN, GREEN_L, "할랄 원료 보관", "승인·검수 합격 원료")
    zone((1200, 170, 1490, 460), BLUE, BLUE_L, "포장재", "할랄 확인 포장재")
    zone((1200, 500, 1490, 720), ORANGE, ORANGE_L, "반품 대기", "공급사 반품 예정")
    zone((520, 760, 900, 900), PURPLE, PURPLE_L, "소분·계량실", "전용 도구 사용")
    # 화학물질 별도 잠금실
    d.rectangle((950, 760, 1490, 900), fill=GRAY_L, outline=GRAY, width=8)
    ctext(d, (950, 760, 1490, 900), "세제·소독제·윤활유 보관실 (별도 잠금)\n※ 식품 원료와 분리", f(22, bold=True), GRAY)
    # 선반 표시
    for r in range(3):
        for c in range(4):
            x = 560 + c * 150
            y = 330 + r * 125
            d.rectangle((x, y, x + 120, y + 80), fill="white", outline=GREEN, width=3)
            ctext(d, (x, y, x + 120, y + 80), f"H-{chr(65 + r)}{c + 1}\n선반", f(18, bold=True), GREEN)
    # 동선
    arrow(d, (20, 500), (150, 500), INK, 6)
    arrow(d, (470, 360), (560, 360), INK, 6)
    arrow(d, (300, 560), (300, 630), RED, 6)
    arrow(d, (840, 720), (740, 790), INK, 6)
    arrow(d, (1160, 610), (1230, 610), ORANGE, 6)
    # 범례
    ly = 960
    items = [(GREEN, "할랄 원료"), (YELLOW, "검수 대기"), (RED, "부적합 격리"), (ORANGE, "반품"),
             (BLUE, "포장재"), (PURPLE, "소분·계량"), (GRAY, "화학물질")]
    x = 90
    for col, name in items:
        d.rectangle((x, ly, x + 44, ly + 30), fill=col)
        d.text((x + 54, ly), name, font=f(22), fill=INK)
        x += 205
    d.text((90, ly + 55), "※ 비할랄 원료는 공장 내 반입하지 않는 것이 원칙. 돼지 유래 물질·주류는 반입 금지.",
           font=f(22, bold=True), fill=RED)
    save(im, "02_창고배치도.png")


# 3. 구역 표지판 ---------------------------------------------------------------
def img_zone_signs():
    W, H = 1600, 900
    im, d = canvas(W, H)
    title(d, W, "구역 표지판 예시 (벽·천장 부착, A3 이상 권장)")
    signs = [(GREEN, "HALAL", "할랄 원료 보관구역", "HALAL RAW MATERIALS ONLY"),
             (YELLOW, "대기", "입고 검수 대기구역", "QUARANTINE - PENDING INSPECTION"),
             (RED, "금지", "부적합품 격리구역 · 사용 금지", "REJECTED - DO NOT USE"),
             (ORANGE, "반품", "반품 대기구역", "RETURN TO SUPPLIER"),
             (BLUE, "포장", "할랄 포장재 보관구역", "HALAL PACKAGING MATERIALS"),
             (GRAY, "잠금", "화학물질 보관실 · 관계자 외 출입금지", "CHEMICALS - AUTHORIZED ONLY")]
    bw, bh = 720, 220
    for i, (col, badge, ko, en) in enumerate(signs):
        x = 60 + (i % 2) * (bw + 40)
        y = 110 + (i // 2) * (bh + 30)
        rbox(d, (x, y, x + bw, y + bh), col, None, 14)
        rbox(d, (x + 12, y + 12, x + bw - 12, y + bh - 12), None, "white", 10, 4)
        d.ellipse((x + 40, y + 45, x + 170, y + 175), fill="white")
        ctext(d, (x + 40, y + 45, x + 170, y + 175), badge, f(30 if len(badge) > 2 else 36, sq=True), col)
        ctext(d, (x + 180, y + 40, x + bw - 20, y + 130), ko, f(32 if len(ko) < 14 else 27, sq=True), "white")
        ctext(d, (x + 180, y + 120, x + bw - 20, y + 180), en, f(22, bold=True), "white")
    save(im, "03_구역표지판.png")


# 4. 원료 식별 라벨 ------------------------------------------------------------
def img_material_label():
    W, H = 1600, 900
    im, d = canvas(W, H, "#F5F5F5")
    title(d, W, "원료 식별 라벨 작성 예시 (포장·팔레트마다 부착)")
    x0, y0, x1, y1 = 260, 110, 1340, 870
    d.rectangle((x0 + 10, y0 + 10, x1 + 10, y1 + 10), fill="#BDBDBD")
    d.rectangle((x0, y0, x1, y1), fill="white", outline=GREEN, width=8)
    d.rectangle((x0, y0, x1, y0 + 100), fill=GREEN)
    ctext(d, (x0, y0, x1, y0 + 100), "HALAL 승인 원료  |  APPROVED HALAL MATERIAL", f(36, sq=True), "white")
    rows = [("원료명 / 코드", "변성전분 / RM-0231"), ("제조사", "○○전분(주) 제2공장"),
            ("공급사", "△△상사"), ("로트번호", "LOT 2609-1182"),
            ("입고일 / 유통기한", "2026.09.12  /  2027.09.11"),
            ("할랄 인증", "KMF  No. 000-000  (유효기간 2027.03.31)"),
            ("검수 결과", "■ 합격   □ 불합격      검수자 : 홍길동 (서명)"),
            ("소분 정보", "소분일 2026.09.20   소분자 : 김○○")]
    rh = (y1 - y0 - 110) / len(rows)
    for i, (k, v) in enumerate(rows):
        yy = y0 + 105 + i * rh
        d.rectangle((x0 + 8, yy, x0 + 330, yy + rh - 4), fill=GREEN_L)
        ctext(d, (x0 + 8, yy, x0 + 330, yy + rh - 4), k, f(26, bold=True), GREEN)
        d.text((x0 + 360, yy + rh / 2 - 17), v, font=f(28), fill=INK)
        d.line((x0 + 8, yy + rh - 2, x1 - 8, yy + rh - 2), fill="#C8E6C9", width=2)
    # 주석 말풍선
    notes = [(y0 + 105 + 3 * rh + rh / 2, "추적성의 핵심"), (y0 + 105 + 5 * rh + rh / 2, "인증서와 대조"),
             (y0 + 105 + 7 * rh + rh / 2, "소분 시 재부착")]
    for yy, t in notes:
        d.line((x1, yy, x1 + 40, yy), fill=RED, width=4)
        rbox(d, (x1 + 40, yy - 30, x1 + 250, yy + 30), RED_L, RED, 10, 3)
        ctext(d, (x1 + 40, yy - 30, x1 + 250, yy + 30), t, f(22, bold=True), RED)
    save(im, "04_원료라벨.png")


# 5. 선반·팔레트 적재 측면도 ---------------------------------------------------
def img_shelf():
    W, H = 1600, 900
    im, d = canvas(W, H)
    title(d, W, "선반·팔레트 적재 기준 (측면 예시)")
    floor = 800
    d.rectangle((60, floor, 1540, floor + 20), fill="#9E9E9E")
    d.rectangle((60, 120, 90, floor), fill="#BDBDBD")
    ctext(d, (40, 90, 110, 120), "벽", f(22, bold=True), MUTED)
    # 선반
    sx0, sx1 = 250, 1050
    for y in (300, 540, 770):
        d.rectangle((sx0, y, sx1, y + 16), fill="#78909C")
    d.rectangle((sx0, 280, sx0 + 16, floor), fill="#546E7A")
    d.rectangle((sx1 - 16, 280, sx1, floor), fill="#546E7A")
    # 상자
    def box(x, y, w, h, col, t):
        d.rectangle((x, y, x + w, y + h), fill="#D7B98E", outline="#8D6E63", width=3)
        d.rectangle((x + 15, y + 15, x + w - 15, y + 55), fill=col)
        ctext(d, (x + 15, y + 15, x + w - 15, y + 55), t, f(18, bold=True), "white")
    for i in range(3):
        box(290 + i * 250, 150, 210, 150, GREEN, "HALAL 라벨")
        box(290 + i * 250, 390, 210, 150, GREEN, "HALAL 라벨")
    # 선반 라벨
    for y, t in ((316, "H-A1  할랄 선반  |  원료 목록 게시"), (556, "H-A2  할랄 선반  |  FIFO: 왼쪽부터 사용")):
        d.rectangle((sx0 + 20, y + 2, sx0 + 560, y + 36), fill=GREEN)
        d.text((sx0 + 32, y + 6), t, font=f(20, bold=True), fill="white")
    # 팔레트
    px = 1150
    d.rectangle((px, floor - 40, px + 330, floor), fill=GREEN)
    for k in range(4):
        d.rectangle((px + 20 + k * 80, floor - 30, px + 70 + k * 80, floor), fill="white")
    for r in range(3):
        box(px + 20, floor - 40 - 150 * (r + 1), 290, 150, GREEN, "HALAL 라벨")
    ctext(d, (px, floor - 40, px + 330, floor), "", f(10))
    ctext(d, (px, floor - 40 - 450 - 50, px + 330, floor - 40 - 455), "할랄 전용 팔레트(녹색)", f(24, bold=True), GREEN)
    # 치수 표시
    def dim(p0, p1, t, horizontal=True):
        d.line([p0, p1], fill=RED, width=3)
        if horizontal:
            for p in (p0, p1):
                d.line((p[0], p[1] - 12, p[0], p[1] + 12), fill=RED, width=3)
            d.text(((p0[0] + p1[0]) / 2 - 60, p0[1] - 60), t, font=f(22, bold=True), fill=RED)
        else:
            for p in (p0, p1):
                d.line((p[0] - 12, p[1], p[0] + 12, p[1]), fill=RED, width=3)
            d.text((p0[0] + 16, (p0[1] + p1[1]) / 2 - 14), t, font=f(22, bold=True), fill=RED)
    dim((90, 700), (250, 700), "벽 이격\n15cm↑")
    dim((1100, 740), (1100, floor), "", horizontal=False)
    d.multiline_text((1062, 660), "바닥\n이격\n15cm↑", font=f(20, bold=True), fill=RED)
    rbox(d, (60, 845, 1540, 895), RED_L, RED, 10, 2)
    ctext(d, (60, 845, 1540, 895), "금지 : 바닥 직적재 · 할랄/비할랄 같은 선반 · 라벨 없는 상자 · 개봉 후 방치",
          f(22, bold=True), RED)
    save(im, "05_선반적재.png")


# 6. 소분 용기 ------------------------------------------------------------------
def img_subdivide():
    W, H = 1600, 700
    im, d = canvas(W, H)
    title(d, W, "소분 용기·계량 도구 식별 (좋은 예 / 나쁜 예)")
    # 좋은 예
    rbox(d, (60, 110, 780, 670), GREEN_L, GREEN, 18, 4)
    ctext(d, (60, 115, 780, 165), "○ 좋은 예", f(32, sq=True), GREEN)
    for i in range(3):
        x = 110 + i * 220
        d.rounded_rectangle((x, 250, x + 180, 520), 16, fill="white", outline=GREEN, width=6)
        d.rectangle((x - 5, 225, x + 185, 255), fill=GREEN)
        d.rectangle((x + 15, 300, x + 165, 440), fill="white", outline=GREEN, width=3)
        ctext(d, (x + 15, 300, x + 165, 440), "HALAL\n원료명\nLOT·기한\n소분일", f(20, bold=True), GREEN)
    ctext(d, (60, 540, 780, 660), "녹색 뚜껑 = 할랄 전용 · 뚜껑 밀폐\n모든 용기에 라벨 · 전용 스쿱 동봉",
          f(24), INK)
    # 나쁜 예
    rbox(d, (820, 110, 1540, 670), RED_L, RED, 18, 4)
    ctext(d, (820, 115, 1540, 165), "× 나쁜 예", f(32, sq=True), RED)
    for i in range(3):
        x = 870 + i * 220
        d.rounded_rectangle((x, 250, x + 180, 520), 16, fill="white", outline="#9E9E9E", width=6)
        if i != 1:
            d.rectangle((x - 5, 225, x + 185, 255), fill="#9E9E9E")
        ctext(d, (x, 300, x + 180, 440), ["??", "뚜껑\n없음", "라벨\n없음"][i], f(28, bold=True), RED)
    ctext(d, (820, 540, 1540, 660), "무엇이 들었는지·로트가 무엇인지 모름\n→ 대표적인 현장 지적사항",
          f(24), INK)
    save(im, "06_소분용기.png")


# 7. 입고 3자 대조 --------------------------------------------------------------
def img_receiving():
    W, H = 1600, 760
    im, d = canvas(W, H)
    title(d, W, "입고 검수 : 3자 대조 방법")
    items = [(BLUE, "① 입고 원료 포장", "제품명 · 제조사\n로트 · 유통기한\n할랄 로고"),
             (GREEN, "② 승인 원료 목록", "등록된 원료인가?\n승인 공급사인가?"),
             (PURPLE, "③ 할랄 인증서", "제품명·제조사 일치?\n유효기간 내?\n인정 기관인가?")]
    pos = [(560, 130), (140, 420), (980, 420)]
    for (col, t, s), (x, y) in zip(items, pos):
        rbox(d, (x, y, x + 480, y + 230), "white", col, 18, 5)
        d.rounded_rectangle((x, y, x + 480, y + 70), 18, fill=col)
        d.rectangle((x, y + 50, x + 480, y + 70), fill=col)
        ctext(d, (x, y, x + 480, y + 70), t, f(30, sq=True), "white")
        ctext(d, (x, y + 75, x + 480, y + 230), s, f(24), INK)
    arrow(d, (620, 360), (450, 420), INK, 5)
    arrow(d, (980, 360), (1150, 420), INK, 5)
    arrow(d, (620, 535), (980, 535), INK, 5)
    arrow(d, (980, 535), (620, 535), INK, 5)
    rbox(d, (140, 680, 780, 740), GREEN_L, GREEN, 10, 3)
    ctext(d, (140, 680, 780, 740), "모두 일치 → 합격 → 녹색 구역 입고", f(24, bold=True), GREEN)
    rbox(d, (820, 680, 1460, 740), RED_L, RED, 10, 3)
    ctext(d, (820, 680, 1460, 740), "하나라도 불일치 → 빨간 격리구역", f(24, bold=True), RED)
    save(im, "07_입고3자대조.png")


# 8. 위생 복장 ------------------------------------------------------------------
def img_hygiene_dress():
    W, H = 1600, 1000
    im, d = canvas(W, H)
    title(d, W, "작업자 위생 복장 기준 (예시)")
    cx = 560
    # 사람 실루엣
    d.ellipse((cx - 90, 170, cx + 90, 350), fill="#FFE0B2", outline=INK, width=3)
    d.chord((cx - 105, 140, cx + 105, 330), 180, 360, fill="white", outline=INK, width=4)  # 위생모
    d.rectangle((cx - 70, 270, cx + 70, 330), fill="#B3E5FC", outline=INK, width=3)  # 마스크
    d.rounded_rectangle((cx - 170, 360, cx + 170, 740), 40, fill="white", outline=INK, width=4)  # 위생복
    d.line((cx, 370, cx, 740), fill="#BDBDBD", width=3)
    d.rounded_rectangle((cx - 250, 380, cx - 175, 660), 30, fill="white", outline=INK, width=4)
    d.rounded_rectangle((cx + 175, 380, cx + 250, 660), 30, fill="white", outline=INK, width=4)
    d.ellipse((cx - 255, 650, cx - 170, 720), fill="#80DEEA", outline=INK, width=3)  # 장갑
    d.ellipse((cx + 170, 650, cx + 255, 720), fill="#80DEEA", outline=INK, width=3)
    d.rectangle((cx - 150, 740, cx - 20, 860), fill="white", outline=INK, width=4)
    d.rectangle((cx + 20, 740, cx + 150, 860), fill="white", outline=INK, width=4)
    d.rounded_rectangle((cx - 170, 860, cx - 10, 930), 20, fill="#FFFFFF", outline=INK, width=4)  # 장화
    d.rounded_rectangle((cx + 10, 860, cx + 170, 930), 20, fill="#FFFFFF", outline=INK, width=4)
    notes = [(200, "위생모 : 머리카락 완전히 덮기"), (300, "마스크 : 코·입 모두 가리기"),
             (470, "위생복 : 작업장 전용, 외부 착용 금지"), (600, "주머니 : 없거나 막힌 형태"),
             (690, "장갑 : 파손 시 즉시 교체"), (895, "위생화·장화 : 작업장 전용")]
    for y, t in notes:
        d.line((cx + 260 if y in (690,) else cx + 180, y, 960, y), fill=GREEN, width=3)
        d.ellipse((954, y - 8, 970, y + 8), fill=GREEN)
        d.text((985, y - 16), t, font=f(26, bold=True), fill=INK)
    rbox(d, (60, 120, 330, 560), RED_L, RED, 14, 3)
    ctext(d, (60, 125, 330, 180), "금지", f(30, sq=True), RED)
    ctext(d, (60, 180, 330, 560), "반지·시계\n귀걸이·목걸이\n매니큐어\n인조 손톱\n향수\n작업장 음식물\n흡연·껌",
          f(24), INK, 14)
    save(im, "08_위생복장.png")


# 9. 위생 전실 동선 ------------------------------------------------------------
def img_entry_flow():
    W, H = 1600, 520
    im, d = canvas(W, H)
    title(d, W, "작업장 입실 위생 절차 (전실 동선)")
    steps = ["탈의실\n개인복 보관", "위생복·모\n마스크 착용", "먼지 제거\n(롤러)", "손 세척\n(30초↑)",
             "손 소독", "에어샤워", "신발 소독조", "작업장\n입장"]
    bw, gap, y0 = 162, 30, 150
    x = (W - (bw * 8 + gap * 7)) // 2
    for i, s in enumerate(steps):
        col = GREEN if i == 7 else BLUE
        rbox(d, (x, y0, x + bw, y0 + 190), BLUE_L if i < 7 else GREEN_L, col, 14, 4)
        d.ellipse((x + bw / 2 - 26, y0 - 26, x + bw / 2 + 26, y0 + 26), fill=col)
        ctext(d, (x + bw / 2 - 26, y0 - 26, x + bw / 2 + 26, y0 + 26), str(i + 1), f(26, sq=True), "white")
        ctext(d, (x, y0 + 30, x + bw, y0 + 190), s, f(23, bold=True), INK)
        if i < 7:
            arrow(d, (x + bw + 3, y0 + 95), (x + bw + gap - 3, y0 + 95), GRAY, 4, 12)
        x += bw + gap
    rbox(d, (100, 390, 1500, 490), YELLOW_L, YELLOW, 12, 3)
    ctext(d, (100, 390, 1500, 490),
          "손 세척 : 비수동식 수전 · 액체비누 · 종이타월(또는 건조기) · 소독제 비치 / 절차를 세면대 앞에 게시\n방문객·심사원도 동일 절차 적용 (여분 위생복 준비)",
          f(22), INK)
    save(im, "09_입실절차.png")


# 10. 세척도구 색상 구분 --------------------------------------------------------
def img_cleaning_tools():
    W, H = 1600, 640
    im, d = canvas(W, H)
    title(d, W, "청소·세척 도구 구역별 색상 구분 (예시)")
    tools = [(GREEN, "녹색", "생산 설비\n식품 접촉면"), (BLUE, "파랑", "원료·완제품\n창고"),
             (YELLOW, "노랑", "벽·바닥\n일반 구역"), (RED, "빨강", "화장실\n폐기물 구역")]
    for i, (col, name, use) in enumerate(tools):
        x = 90 + i * 370
        # 솔
        d.rectangle((x + 140, 130, x + 170, 380), fill=col)
        d.rounded_rectangle((x + 60, 370, x + 250, 420), 10, fill=col)
        for k in range(10):
            d.line((x + 70 + k * 18, 420, x + 70 + k * 18, 460), fill=col, width=6)
        # 걸이 라벨
        rbox(d, (x + 30, 480, x + 290, 610), "white", col, 14, 4)
        ctext(d, (x + 30, 480, x + 290, 530), name, f(28, sq=True), col)
        ctext(d, (x + 30, 525, x + 290, 610), use, f(22, bold=True), INK)
    ctext(d, (0, 80, W, 125), "※ 돼지털 브러시 등 동물성 소재 도구 사용 금지 · 구역 간 혼용 금지 · 전용 걸이에 보관",
          f(22, bold=True), RED)
    save(im, "10_세척도구.png")


# 11. 나지스(Sertu) 세척 절차 --------------------------------------------------
def img_sertu():
    W, H = 1600, 700
    im, d = canvas(W, H)
    title(d, W, "나지스(무갈라자) 오염 시 의례 세척(Sertu) 절차 (예시)",
          "세부 방법·재료·입회 요건은 인증기관 기준을 따를 것")
    steps = [(RED, "발견·격리", "생산 중지\n오염 범위 표시\n인증기관 보고"),
             (ORANGE, "오염물 제거", "눈에 보이는\n오염 물질을\n완전히 제거"),
             (PURPLE, "흙물 세척 1회", "할랄 인증\n점토(흙)+물로\n1회 세척"),
             (BLUE, "물 세척 6회", "깨끗한 물로\n6회 세척\n(합계 7회)"),
             (GREEN, "확인·기록", "무슬림 감독자\n입회·확인\n세척 기록 작성")]
    bw, gap, y0 = 260, 40, 150
    x = (W - (bw * 5 + gap * 4)) // 2
    for i, (col, t, s) in enumerate(steps):
        rbox(d, (x, y0, x + bw, y0 + 300), "white", col, 18, 5)
        d.rounded_rectangle((x, y0, x + bw, y0 + 80), 18, fill=col)
        d.rectangle((x, y0 + 60, x + bw, y0 + 80), fill=col)
        ctext(d, (x, y0, x + bw, y0 + 80), f"{i + 1}. {t}", f(26, sq=True), "white")
        ctext(d, (x, y0 + 85, x + bw, y0 + 300), s, f(24), INK, 10)
        if i < 4:
            arrow(d, (x + bw + 4, y0 + 150), (x + bw + gap - 4, y0 + 150), GRAY, 5, 13)
        x += bw + gap
    rbox(d, (100, 500, 1500, 640), GRAY_L, GRAY, 12, 2)
    ctext(d, (100, 500, 1500, 640),
          "무갈라자(Mughallazah) = 돼지·개 및 그 유래 물질 (가장 엄격한 나지스)\n"
          "많은 기관이 돼지 제품과 설비 공용 시 인증 자체를 불허 → 사전 예방이 원칙",
          f(24), INK, 10)
    save(im, "11_Sertu절차.png")


# 12. 반입금지 게시물 ----------------------------------------------------------
def img_no_food_poster():
    W, H = 1200, 1500
    im, d = canvas(W, H)
    d.rectangle((0, 0, W, H), outline=RED, width=30)
    d.rectangle((30, 30, W - 30, 250), fill=RED)
    ctext(d, (30, 30, W - 30, 250), "반입 금지\nSTRICTLY PROHIBITED", f(70, sq=True), "white", 20)
    cx, cy, r = W // 2, 560, 260
    # 병(주류)
    d.rounded_rectangle((cx - 200, cy - 60, cx - 110, cy + 170), 18, fill="#8D6E63", outline=INK, width=4)
    d.rectangle((cx - 175, cy - 150, cx - 135, cy - 60), fill="#8D6E63", outline=INK, width=4)
    # 도시락
    d.rounded_rectangle((cx - 80, cy + 20, cx + 200, cy + 170), 14, fill="#FFCC80", outline=INK, width=4)
    d.line((cx + 60, cy + 20, cx + 60, cy + 170), fill=INK, width=4)
    # 돼지 얼굴
    d.ellipse((cx - 40, cy - 190, cx + 150, cy - 10), fill="#F8BBD0", outline=INK, width=4)
    d.ellipse((cx + 10, cy - 110, cx + 100, cy - 50), fill="#F48FB1", outline=INK, width=3)
    d.ellipse((cx + 30, cy - 90, cx + 45, cy - 72), fill=INK)
    d.ellipse((cx + 65, cy - 90, cx + 80, cy - 72), fill=INK)
    d.ellipse((cx + 5, cy - 150, cx + 25, cy - 130), fill=INK)
    d.ellipse((cx + 85, cy - 150, cx + 105, cy - 130), fill=INK)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=RED, width=40)
    d.line((cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7), fill=RED, width=40)
    ctext(d, (60, 850, W - 60, 960), "돼지고기 · 주류 · 외부 음식", f(64, sq=True), RED)
    ctext(d, (60, 1010, W - 60, 1200),
          "생산·창고 구역에 비할랄 음식, 도시락, 간식,\n주류(알코올 음료)를 반입할 수 없습니다.",
          f(40, bold=True), INK, 16)
    ctext(d, (60, 1220, W - 60, 1320), "NON-HALAL FOOD & ALCOHOLIC BEVERAGES\nARE NOT ALLOWED IN THIS AREA",
          f(34, bold=True), MUTED, 12)
    ctext(d, (60, 1360, W - 60, 1440), "할랄위원회 · 할랄 책임자", f(34, sq=True), GREEN)
    save(im, "12_반입금지게시물.png")


# 13. 방충방서 배치도 ----------------------------------------------------------
def img_pest():
    W, H = 1600, 970
    im, d = canvas(W, H, "#FAFAFA")
    title(d, W, "방충·방서 장치 배치도 (예시)")
    X0, Y0, X1, Y1 = 260, 170, 1340, 780
    d.rectangle((X0, Y0, X1, Y1), fill="white", outline=INK, width=6)
    d.line((800, Y0, 800, Y1), fill=INK, width=4)
    ctext(d, (X0, Y0, 800, Y1), "원료 창고", f(34, sq=True), "#BDBDBD")
    ctext(d, (800, Y0, X1, Y1), "생산 구역", f(34, sq=True), "#BDBDBD")
    # 외곽 먹이상자 (빨강 사각)
    outs = [(200, 200), (200, 480), (200, 740), (1400, 200), (1400, 480), (1400, 740),
            (520, 110), (1080, 110), (520, 840), (1080, 840)]
    for x, y in outs:
        d.rectangle((x - 22, y - 16, x + 22, y + 16), fill=RED)
    # 내부 트랩 (파랑 원)
    ins = [(300, 220), (300, 730), (760, 220), (760, 730), (840, 220), (840, 730), (1300, 220), (1300, 730)]
    for x, y in ins:
        d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=BLUE)
    # 포충등 (노랑 별)
    for x, y in ((530, 200), (1070, 200)):
        d.rectangle((x - 40, y - 14, x + 40, y + 14), fill=YELLOW, outline=INK, width=2)
    # 출입문
    d.rectangle((X0 - 6, 440, X0 + 6, 540), fill=ORANGE)
    d.rectangle((X1 - 6, 440, X1 + 6, 540), fill=ORANGE)
    ly = 875
    for col, shape, t, x in ((RED, "rect", "외곽 쥐 먹이상자 (건물 밖)", 120),
                             (BLUE, "circle", "내부 포획 트랩 (약제 금지)", 560),
                             (YELLOW, "rect", "포충등 (비산방지형)", 1000),
                             (ORANGE, "rect", "출입문·방충커튼", 1320)):
        if shape == "rect":
            d.rectangle((x, ly, x + 40, ly + 30), fill=col)
        else:
            d.ellipse((x, ly - 2, x + 34, ly + 32), fill=col)
        d.text((x + 50, ly), t, font=f(22, bold=True), fill=INK)
    ctext(d, (0, 915, W, 950), "번호를 붙여 배치도와 현장 장치 번호 일치 · 점검 기록 · 방역업체 보고서 비치",
          f(22, bold=True), MUTED)
    save(im, "13_방충방서배치도.png")


# 14. 추적성 ------------------------------------------------------------------
def img_trace():
    W, H = 1600, 620
    im, d = canvas(W, H)
    title(d, W, "추적성(Traceability) 연결 고리")
    nodes = [(BLUE, "공급사", "인증서\n거래명세서"), (GREEN, "원료 로트", "입고검수일지\nLOT 2609-1182"),
             (PURPLE, "배합·생산", "생산일지\n원료 로트 기록"), (ORANGE, "완제품 로트", "제조일자\nLOT F-260925"),
             (RED, "출하처", "출하 기록\n거래처 목록")]
    bw, gap, y0 = 250, 60, 150
    x = (W - (bw * 5 + gap * 4)) // 2
    for i, (col, t, s) in enumerate(nodes):
        rbox(d, (x, y0, x + bw, y0 + 220), "white", col, 18, 5)
        d.rounded_rectangle((x, y0, x + bw, y0 + 70), 18, fill=col)
        d.rectangle((x, y0 + 50, x + bw, y0 + 70), fill=col)
        ctext(d, (x, y0, x + bw, y0 + 70), t, f(28, sq=True), "white")
        ctext(d, (x, y0 + 75, x + bw, y0 + 220), s, f(22), INK, 8)
        if i < 4:
            arrow(d, (x + bw + 4, y0 + 90), (x + bw + gap - 4, y0 + 90), GREEN, 5, 13)
            arrow(d, (x + bw + gap - 4, y0 + 150), (x + bw + 4, y0 + 150), RED, 5, 13)
        x += bw + gap
    d.text((140, 420), "→ 녹색 : 정추적 (원료 로트 → 어느 제품·거래처로 갔나)", font=f(24, bold=True), fill=GREEN)
    d.text((140, 470), "← 빨강 : 역추적 (완제품 로트 → 어떤 원료·공급사였나)", font=f(24, bold=True), fill=RED)
    d.text((140, 530), "심사원이 임의 제품 1개를 골라 요청 → 2시간 이내 서류로 연결 가능해야 함",
           font=f(24), fill=INK)
    save(im, "14_추적성.png")


# 15. D-30 일정 ----------------------------------------------------------------
def img_timeline():
    W, H = 1600, 640
    im, d = canvas(W, H)
    title(d, W, "현장심사 D-30 준비 일정 (요약)")
    pts = [("D-30", "자체점검\n갭 분석"), ("D-25", "원료 인증서\n전수 점검"), ("D-21", "창고 구역\n표지·라벨"),
           ("D-18", "윤활유·세제\n포장재 확인"), ("D-14", "전 직원\n교육·평가"), ("D-10", "내부감사\n추적성 테스트"),
           ("D-7", "경영검토\n문서 바인더"), ("D-5", "시설 보수\n방역"), ("D-3", "리허설\n인터뷰 연습"),
           ("D-1", "대청소\n최종 점검"), ("D-Day", "현장심사")]
    y = 300
    x0, x1 = 90, 1510
    d.line((x0, y, x1, y), fill=GREEN, width=10)
    step = (x1 - x0) / (len(pts) - 1)
    for i, (dday, t) in enumerate(pts):
        x = x0 + i * step
        col = RED if dday == "D-Day" else GREEN
        d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=col, outline="white", width=4)
        ctext(d, (x - 70, y - 90, x + 70, y - 35), dday, f(26, sq=True), col)
        if i % 2 == 0:
            ctext(d, (x - 75, y + 35, x + 75, y + 120), t, f(20, bold=True), INK)
        else:
            ctext(d, (x - 75, y + 130, x + 75, y + 215), t, f(20, bold=True), INK)
            d.line((x, y + 22, x, y + 130), fill="#BDBDBD", width=2)
    save(im, "15_일정표.png")


# 16. 화학물질 보관함 ----------------------------------------------------------
def img_chemical():
    W, H = 1600, 860
    im, d = canvas(W, H)
    title(d, W, "화학물질(세제·소독제·윤활유) 보관 예시")
    x0, y0, x1, y1 = 120, 110, 760, 830
    d.rectangle((x0, y0, x1, y1), fill=GRAY_L, outline=GRAY, width=8)
    d.rectangle((x0, y0, x1, y0 + 70), fill=GRAY)
    ctext(d, (x0, y0, x1, y0 + 70), "화학물질 보관함 · 잠금", f(30, sq=True), "white")
    shelves = [("세척제", BLUE), ("소독제", GREEN), ("식품용 윤활유(H1)", ORANGE), ("방역 약품", RED)]
    for i, (t, col) in enumerate(shelves):
        yy = y0 + 90 + i * 150
        d.rectangle((x0 + 20, yy + 110, x1 - 20, yy + 122), fill="#9E9E9E")
        for k in range(4):
            bx = x0 + 50 + k * 145
            d.rounded_rectangle((bx, yy + 20, bx + 100, yy + 110), 10, fill=col)
        d.rectangle((x0 + 20, yy - 6, x0 + 300, yy + 20), fill="white")
        d.text((x0 + 28, yy - 6), t, font=f(22, bold=True), fill=INK)
    d.ellipse((x1 - 70, y0 + 330, x1 - 30, y0 + 370), fill="#FFD54F", outline=INK, width=3)
    notes = ["원료·포장재 창고와 분리된 별도 공간", "잠금장치 + 관리자 지정",
             "모든 용기에 제품명 라벨 (식품 용기에 소분 금지)", "MSDS(물질안전보건자료) 비치",
             "사용 대장 기록 (일자·품목·사용량·사용자)", "할랄 인증 또는 성분 확인서 확보",
             "  (동물성 유지·알코올 함유 여부)"]
    for i, t in enumerate(notes):
        yy = 170 + i * 75
        if not t.startswith(" "):
            d.ellipse((830, yy + 6, 856, yy + 32), fill=GREEN)
        d.text((875, yy), t.strip() if not t.startswith(" ") else t, font=f(26, bold=not t.startswith(" ")),
               fill=INK)
    save(im, "16_화학물질보관.png")


# 17. 화장실 / 기도실 ----------------------------------------------------------
def img_facility():
    W, H = 1600, 700
    im, d = canvas(W, H)
    title(d, W, "부대시설 준비 예시 : 화장실 물 세정 설비 · 기도 공간")
    # 화장실
    rbox(d, (60, 110, 780, 670), BLUE_L, BLUE, 18, 4)
    ctext(d, (60, 115, 780, 170), "화장실", f(32, sq=True), BLUE)
    d.rounded_rectangle((170, 330, 370, 560), 30, fill="white", outline=INK, width=4)
    d.ellipse((160, 300, 380, 400), fill="white", outline=INK, width=4)
    d.rectangle((190, 200, 350, 300), fill="white", outline=INK, width=4)
    d.line((380, 280, 470, 280), fill=INK, width=6)
    d.rounded_rectangle((460, 250, 520, 320), 10, fill=BLUE)
    ctext(d, (420, 330, 560, 380), "세정용 호스", f(22, bold=True), BLUE)
    ctext(d, (80, 580, 760, 660), "물 세정 설비(비데·호스) · 작업장과 직접 연결 금지\n손 세척 설비 · 청소 점검표 게시",
          f(22, bold=True), INK)
    # 기도실
    rbox(d, (820, 110, 1540, 670), GREEN_L, GREEN, 18, 4)
    ctext(d, (820, 115, 1540, 170), "기도 공간 (권장)", f(32, sq=True), GREEN)
    for i in range(3):
        x = 900 + i * 200
        d.rectangle((x, 250, x + 150, 500), fill="#A5D6A7", outline=GREEN, width=4)
        d.rectangle((x + 15, 265, x + 135, 485), outline="white", width=3)
    arrow(d, (1470, 520), (1470, 230), GREEN, 6)
    ctext(d, (1380, 180, 1540, 225), "키블라 방향", f(20, bold=True), GREEN)
    ctext(d, (840, 580, 1520, 660), "깨끗하고 조용한 공간 · 기도 매트 · 방향 표시\n세정(우두)용 수도 인접",
          f(22, bold=True), INK)
    save(im, "17_부대시설.png")


# 18. 운송 차량 점검 ------------------------------------------------------------
def img_vehicle():
    W, H = 1600, 640
    im, d = canvas(W, H)
    title(d, W, "출하 차량 적재 전 점검 (예시)")
    # 트럭
    d.rectangle((120, 200, 720, 470), fill="white", outline=INK, width=5)
    d.rectangle((720, 290, 900, 470), fill="#CFD8DC", outline=INK, width=5)
    d.rectangle((760, 310, 870, 380), fill="#B3E5FC", outline=INK, width=3)
    for x in (230, 600, 800):
        d.ellipse((x - 55, 430, x + 55, 540), fill=GRAY, outline=INK, width=4)
        d.ellipse((x - 22, 463, x + 22, 507), fill="#BDBDBD")
    d.rectangle((160, 240, 680, 300), fill=GREEN)
    ctext(d, (160, 240, 680, 300), "HALAL 제품 전용 적재", f(28, sq=True), "white")
    checks = ["□ 적재함 청결 (이물·악취 없음)", "□ 이전 적재물 확인 : 돼지고기·비할랄 없음",
              "□ 혼적 여부 : 비할랄 제품과 함께 싣지 않음", "□ 냉장·냉동 온도 확인 및 기록",
              "□ 차량번호 · 점검자 · 일시 기록"]
    for i, t in enumerate(checks):
        d.text((960, 190 + i * 70), t, font=f(26, bold=True), fill=INK)
    ctext(d, (0, 570, W, 620), "외부 물류업체 이용 시 계약서에 할랄 취급 조건 명시", f(24, bold=True), RED)
    save(im, "18_차량점검.png")


if __name__ == "__main__":
    for fn in [img_audit_flow, img_warehouse_layout, img_zone_signs, img_material_label, img_shelf,
               img_subdivide, img_receiving, img_hygiene_dress, img_entry_flow, img_cleaning_tools,
               img_sertu, img_no_food_poster, img_pest, img_trace, img_timeline, img_chemical,
               img_facility, img_vehicle]:
        fn()
    print(sorted(p.name for p in OUT.iterdir()))
