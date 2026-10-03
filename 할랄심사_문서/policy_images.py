"""할랄 방침 게시물과 게시 위치 예시 그림 (채움에프앤비)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "images"
FD = "/usr/share/fonts/truetype/nanum/"


def F(size, w="r"):
    return ImageFont.truetype(FD + {"r": "NanumGothic.ttf", "b": "NanumGothicBold.ttf",
                                    "s": "NanumSquareB.ttf", "m": "NanumMyeongjoBold.ttf"}[w], size)


GREEN, GREEN_D, GOLD, INK, MUTED, RED = "#2E7D32", "#1B5E20", "#B8860B", "#212121", "#616161", "#C62828"
COMPANY = "채움에프앤비 농업회사법인 주식회사"

POLICY_INTRO = ("당사는 할랄 인증 제품을 지속적으로 생산하여 고객 만족에 최선을 다하며,\n"
                "위생적이고 안전한 제품을 공급하기 위하여 다음 사항을 실천합니다.")
POLICY = [
    ("할랄 인증 제품에 사용하는 모든 원료는 할랄이며, 인체에 적합하지 않은\n제품은 구매·생산·공급하지 않습니다.",
     "All ingredients are Halal; we never purchase, produce or supply unsuitable products."),
    ("돼지 및 돼지 유래 성분, 불결한(나지스) 원료를 사용하지 않는\n생산시설을 유지합니다.",
     "Our facility is free from pork, its derivatives and Najis materials."),
    ("모든 임직원이 할랄 보증시스템을 이해하고 지키도록\n교육·훈련을 실시합니다.",
     "All employees are trained to understand and follow the Halal Assurance System."),
    ("할랄팀을 구성·운영하여 할랄 보증시스템을 계획·실행하고\n지속적으로 개선합니다.",
     "A Halal Team plans, implements and continually improves the system."),
]


def ctext(d, cx, y, text, font, fill=INK, spacing=10):
    bb = d.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    d.multiline_text((cx - (bb[2] - bb[0]) / 2, y), text, font=font, fill=fill, spacing=spacing, align="center")
    return y + (bb[3] - bb[1])


def poster(W=1240, H=1754):
    im = Image.new("RGB", (W, H), "#FFFDF7")
    d = ImageDraw.Draw(im)
    # 테두리
    d.rectangle((24, 24, W - 25, H - 25), outline=GREEN, width=10)
    d.rectangle((44, 44, W - 45, H - 45), outline=GOLD, width=3)
    # 머리
    d.rectangle((44, 44, W - 45, 300), fill=GREEN)
    ctext(d, W / 2, 80, "HALAL POLICY", F(46, "s"), "#C8E6C9")
    ctext(d, W / 2, 150, "할 랄 방 침", F(96, "m"), "white")
    y = 340
    y = ctext(d, W / 2, y, COMPANY, F(34, "b"), GREEN_D) + 40
    y = ctext(d, W / 2, y, POLICY_INTRO, F(29), INK, 14) + 50
    for i, (ko, en) in enumerate(POLICY, 1):
        d.ellipse((110, y, 180, y + 70), fill=GREEN)
        ctext(d, 145, y + 10, str(i), F(42, "s"), "white")
        d.multiline_text((210, y + 2), ko, font=F(31, "b"), fill=INK, spacing=12)
        bb = d.multiline_textbbox((210, y + 2), ko, font=F(31, "b"), spacing=12)
        d.text((210, bb[3] + 12), en, font=F(21), fill=MUTED)
        y = bb[3] + 80
    # 날짜·서명
    y = max(y + 10, 1330)
    d.line((110, y, W - 110, y), fill="#BDBDBD", width=2)
    ctext(d, W / 2, y + 40, "20 ____ 년  ____ 월  ____ 일", F(34, "b"), INK)
    sy = y + 130
    d.text((330, sy + 30), "대표이사", font=F(40, "b"), fill=INK)
    d.text((540, sy + 30), "○  ○  ○", font=F(40, "b"), fill=INK)
    # 서명 자리 (예시)
    d.rounded_rectangle((760, sy, 1010, sy + 120), 12, outline=RED, width=4)
    for k in range(0, 250, 16):
        pass
    ctext(d, 885, sy + 22, "대표 서명\n(자필)", F(30, "b"), RED, 8)
    ctext(d, W / 2, sy + 160, "※ 대표이사가 직접 자필 서명한 원본을 게시합니다.", F(24), MUTED)
    return im


def callout(d, x, y, tx, ty, text, color=RED, w=430):
    d.line((x, y, tx, ty), fill=color, width=4)
    d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=color)
    f = F(25, "b")
    bb = d.multiline_textbbox((0, 0), text, font=f, spacing=8)
    bw, bh = max(w, bb[2] + 30), bb[3] + 28
    d.rounded_rectangle((tx, ty - bh / 2, tx + bw, ty + bh / 2), 12, fill="white", outline=color, width=4)
    d.multiline_text((tx + 15, ty - bh / 2 + 14), text, font=f, fill=INK, spacing=8)


def framed(poster_im, w):
    p = poster_im.resize((w, int(w * poster_im.height / poster_im.width)))
    fr = Image.new("RGB", (p.width + 36, p.height + 36), "#5D4037")
    fr.paste(p, (18, 18))
    return fr


def office_scene(pim):
    W, H = 1600, 1000
    im = Image.new("RGB", (W, H), "#ECEFF1")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 70), fill=GREEN)
    ctext(d, W / 2, 14, "게시 예시 ① 사무실 (회의실·출입구 벽면)", F(34, "s"), "white")
    d.rectangle((0, 760, W, H), fill="#BCAAA4")  # 바닥
    d.line((0, 760, W, 760), fill="#8D6E63", width=6)
    # 문
    d.rectangle((90, 300, 330, 760), fill="#A1887F", outline="#6D4C41", width=6)
    d.ellipse((290, 520, 312, 542), fill="#FFD54F")
    ctext(d, 210, 250, "사무실 출입문", F(24, "b"), MUTED)
    # 액자 (방침)
    fr = framed(pim, 300)
    px, py = 470, 150
    im.paste(fr, (px, py))
    # 품질방침 액자 (옆)
    d.rectangle((830, 210, 1010, 450), fill="white", outline="#5D4037", width=14)
    ctext(d, 920, 290, "품질방침\nHACCP", F(26, "b"), MUTED)
    # 높이 표시
    cy = py + fr.height // 2
    d.line((440, cy, 440, 760), fill=RED, width=3)
    for yy in (cy, 760):
        d.line((425, yy, 455, yy), fill=RED, width=3)
    d.text((360, (cy + 760) / 2 - 15), "약\n1.5m", font=F(24, "b"), fill=RED, spacing=4)
    callout(d, px + fr.width - 10, py + 60, 1090, 110, "대표 자필 서명 원본 (복사본 ×)", w=420)
    callout(d, px + fr.width - 10, py + 300, 1090, 560, "액자 또는 코팅으로 훼손 방지", w=420)
    callout(d, px + fr.width // 2, py + fr.height, 600, 860, "눈높이(약 1.5m), 누구나 보이는 곳", w=480)
    callout(d, 210, 760, 60, 935, "출입문 옆·회의실 등 방문객도 보는 위치", GREEN, w=420)
    callout(d, 1010, 330, 1090, 330, "다른 방침(품질·HACCP)과 나란히 OK", GREEN, w=420)
    return im


def factory_scene(pim):
    W, H = 1600, 1000
    im = Image.new("RGB", (W, H), "#CFD8DC")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 70), fill=GREEN)
    ctext(d, W / 2, 14, "게시 예시 ② 생산동 입구 (위생 전실 앞)", F(34, "s"), "white")
    # 건물 벽
    d.rectangle((60, 130, 1540, 800), fill="#ECEFF1", outline="#78909C", width=6)
    d.rectangle((0, 800, W, H), fill="#90A4AE")
    # 출입문 (생산동)
    d.rectangle((640, 330, 960, 800), fill="#B0BEC5", outline="#546E7A", width=8)
    d.line((800, 330, 800, 800), fill="#546E7A", width=6)
    d.rectangle((660, 350, 780, 520), fill="#E3F2FD")
    d.rectangle((820, 350, 940, 520), fill="#E3F2FD")
    d.rectangle((640, 250, 960, 320), fill=GREEN_D)
    ctext(d, 800, 262, "생 산 동", F(40, "s"), "white")
    # 방침 액자 (문 왼쪽)
    fr = framed(pim, 250)
    px, py = 300, 240
    im.paste(fr, (px, py))
    # 반입 금지 표지 (문 오른쪽)
    d.rectangle((1010, 260, 1230, 470), fill="white", outline=RED, width=8)
    d.ellipse((1060, 290, 1180, 410), outline=RED, width=10)
    d.line((1078, 308, 1162, 392), fill=RED, width=10)
    ctext(d, 1120, 420, "음식 반입 금지", F(22, "b"), RED)
    # 손세척대
    d.rectangle((1280, 560, 1500, 620), fill="white", outline="#78909C", width=4)
    d.rectangle((1300, 620, 1480, 800), fill="#ECEFF1", outline="#78909C", width=4)
    d.line((1390, 500, 1390, 560), fill="#78909C", width=8)
    d.rectangle((1280, 420, 1500, 490), fill="#E3F2FD", outline="#1565C0", width=3)
    ctext(d, 1390, 435, "손 세척 절차", F(22, "b"), "#1565C0")
    # 외국인 근로자용 번역본
    d.rectangle((110, 300, 260, 500), fill="white", outline="#5D4037", width=10)
    ctext(d, 185, 360, "방침\n번역본\n(EN/VN)", F(20, "b"), MUTED, 6)
    callout(d, px + fr.width // 2, py + 20, 120, 170, "생산동 입구 = 전 직원이 매일 지나는 곳", w=520)
    callout(d, 185, 500, 90, 880, "외국인 근로자용 모국어 번역본 함께 게시", GREEN, w=540)
    callout(d, px + fr.width // 2, py + fr.height, 660, 880, "물·증기에 젖지 않게 코팅·아크릴 커버", w=520)
    callout(d, 1120, 470, 1180, 880, "반입 금지·손세척 표지와 함께", GREEN, w=380)
    return im


if __name__ == "__main__":
    pim = poster()
    pim.save(OUT / "21_할랄방침_게시물.png", optimize=True)
    office_scene(pim).save(OUT / "22_게시예시_사무실.png", optimize=True)
    factory_scene(pim).save(OUT / "23_게시예시_생산동입구.png", optimize=True)
    print("ok")
