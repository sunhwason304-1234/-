"""할랄팀 조직도·임명장·구성 현황 예시 그림 (채움에프앤비). 이름은 자리표시(○○)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "images"
FD = "/usr/share/fonts/truetype/nanum/"


def F(size, w="r"):
    return ImageFont.truetype(FD + {"r": "NanumGothic.ttf", "b": "NanumGothicBold.ttf",
                                    "s": "NanumSquareB.ttf", "m": "NanumMyeongjoBold.ttf"}[w], size)


GREEN, GREEN_D, GREEN_L, GOLD = "#2E7D32", "#1B5E20", "#E8F5E9", "#B8860B"
INK, MUTED, RED, BLUE = "#212121", "#616161", "#C62828", "#1565C0"
COMPANY = "채움에프앤비 농업회사법인 주식회사"


def ctext(d, box, text, font, fill=INK, spacing=8):
    x0, y0, x1, y1 = box
    bb = d.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    d.multiline_text(((x0 + x1 - (bb[2] - bb[0])) / 2, (y0 + y1 - (bb[3] - bb[1])) / 2 - bb[1]),
                     text, font=font, fill=fill, spacing=spacing, align="center")


def node(d, box, title, name, role, color, light):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, 16, fill="white", outline=color, width=4)
    d.rounded_rectangle((x0, y0, x1, y0 + 56), 16, fill=color)
    d.rectangle((x0, y0 + 36, x1, y0 + 56), fill=color)
    ctext(d, (x0, y0, x1, y0 + 56), title, F(26, "s"), "white")
    d.rectangle((x0 + 14, y0 + 68, x1 - 14, y0 + 118), fill=light)
    ctext(d, (x0, y0 + 68, x1, y0 + 118), name, F(26, "b"), INK)
    if role:
        ctext(d, (x0 + 8, y0 + 122, x1 - 8, y1 - 6), role, F(19), MUTED, 6)


def org_chart():
    W, H = 1600, 1180
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 80), fill=GREEN)
    ctext(d, (0, 0, W, 80), "할랄팀 조직도 (예시)", F(38, "s"), "white")
    ctext(d, (0, 88, W, 128), f"{COMPANY} · 매뉴얼 4.2.1 · 제정일 20__.__.__", F(22), MUTED)

    # 최고경영자
    ceo = (620, 150, 980, 330)
    node(d, ceo, "최고경영자 (CEO)", "대표이사  ○○○",
         "할랄 방침 수립·전달\n자원 지원 · 경영검토", GREEN_D, GREEN_L)
    # 할랄팀장
    hm = (620, 400, 980, 600)
    node(d, hm, "할랄팀장 (Halal Manager)", "박○○  팀장",
         "할랄팀 운영 · 교육계획 · 내부감사\n원료·공급업체 승인 · 인증원 소통", GREEN, GREEN_L)
    d.line((800, 330, 800, 400), fill=INK, width=5)
    # 인증기관 (점선)
    cb = (1160, 430, 1500, 570)
    d.rounded_rectangle(cb, 16, fill="#FFF8E1", outline=GOLD, width=4)
    ctext(d, cb, "할랄 인증기관\n(외부 소통 창구)", F(24, "b"), GOLD)
    for x in range(980, 1160, 24):
        d.line((x, 500, x + 12, 500), fill=GOLD, width=4)
    # 내부감사 (보조)
    ia = (100, 430, 440, 570)
    d.rounded_rectangle(ia, 16, fill="#E3F2FD", outline=BLUE, width=4)
    ctext(d, ia, "내부감사원\n(타 부서 교차 감사)", F(24, "b"), BLUE)
    for x in range(440, 620, 24):
        d.line((x, 500, x + 12, 500), fill=BLUE, width=4)

    # 부서
    depts = [("구매", "이○○  대리", "승인 재료만 구매\n공급업체 평가\n할랄 서류 수집·관리", "#EF6C00", "#FFF3E0"),
             ("품질 (QC)", "최○○  과장", "입고 검사·인증서 대조\n이력추적·세척 절차\n교육일지·감사 기록", "#1565C0", "#E3F2FD"),
             ("창고", "정○○  주임", "할랄 구분 보관·식별\n입출고 관리\n부적합품 격리", "#F9A825", "#FFF8E1"),
             ("생산", "강○○  반장", "교차오염 방지\n표준 배합대로 생산\n생산·세척 기록", "#558B2F", "#F1F8E9"),
             ("연구개발 (R&D)", "박○○  팀장 (겸임)", "신재료 선택\n제품 성분 구성\n신제품 할랄 확인", "#6A1B9A", "#F3E5F5")]
    n = len(depts)
    bw, gap = 268, 28
    x = (W - (bw * n + gap * (n - 1))) // 2
    ytop = 720
    d.line((800, 600, 800, 670), fill=INK, width=5)
    d.line((x + bw // 2, 670, x + (bw + gap) * (n - 1) + bw // 2, 670), fill=INK, width=5)
    for i, (t, nm, role, c, l) in enumerate(depts):
        bx = x + i * (bw + gap)
        d.line((bx + bw // 2, 670, bx + bw // 2, ytop), fill=INK, width=5)
        node(d, (bx, ytop, bx + bw, ytop + 250), t, nm, role, c, l)

    # 하단 주석
    d.rounded_rectangle((60, 1000, 1540, 1150), 14, fill="#FAFAFA", outline="#BDBDBD", width=2)
    notes = ["• 이름·직위는 실제 인원으로 기입 (○○는 자리표시)   • 할랄팀원은 회사 정규직원이어야 함 (매뉴얼 4.2.3)",
             "• 1인이 여러 부서를 맡으면 '(겸임)'으로 표시   • 할랄팀장은 기술직 매니저급 이상 + 외부 할랄교육 이수",
             "• 조직 변경 시 조직도 개정·재게시, 할랄팀 이력현황(4.2.2)도 함께 수정"]
    for i, s in enumerate(notes):
        d.text((90, 1018 + i * 42), s, font=F(22), fill=INK)
    im.save(OUT / "24_할랄팀_조직도.png", optimize=True)


def appointment():
    W, H = 1240, 1754
    im = Image.new("RGB", (W, H), "#FFFDF7")
    d = ImageDraw.Draw(im)
    d.rectangle((30, 30, W - 31, H - 31), outline=GOLD, width=12)
    d.rectangle((58, 58, W - 59, H - 59), outline=GREEN, width=3)
    ctext(d, (0, 120, W, 260), "임  명  장", F(110, "m"), GREEN_D)
    ctext(d, (0, 270, W, 320), "Letter of Appointment · Halal Team", F(28), MUTED)
    rows = [("성      명", "최 ○ ○"), ("소      속", "품질관리팀"), ("직      위", "과장"),
            ("할랄팀 직무", "할랄팀원 (품질·QC 담당)")]
    y = 400
    for k, v in rows:
        d.text((220, y), k, font=F(38, "b"), fill=INK)
        d.text((520, y), ":", font=F(38, "b"), fill=INK)
        d.text((570, y), v, font=F(38), fill=INK)
        d.line((560, y + 56, 1020, y + 56), fill="#BDBDBD", width=2)
        y += 95
    body = ("위 사람을 당사 할랄 보증시스템(HAS)의\n"
            "할랄팀원(품질·QC 담당)으로 임명합니다.\n\n"
            "귀하는 할랄 매뉴얼에 정한 책임과 권한에 따라\n"
            "입고 재료 검사, 이력추적, 세척 절차 운영 및\n"
            "할랄 교육·내부감사 기록 업무를 성실히 수행하여 주시기 바랍니다.")
    ctext(d, (100, 800, W - 100, 1160), body, F(34), INK, 16)
    ctext(d, (0, 1250, W, 1310), "20 ____ 년  ____ 월  ____ 일", F(38, "b"), INK)
    ctext(d, (0, 1360, W, 1420), COMPANY, F(36, "b"), GREEN_D)
    d.text((330, 1470), "대표이사", font=F(44, "b"), fill=INK)
    d.text((560, 1470), "○  ○  ○", font=F(44, "b"), fill=INK)
    d.ellipse((830, 1435, 960, 1565), outline=RED, width=5)
    ctext(d, (830, 1435, 960, 1565), "직인\n(서명)", F(28, "b"), RED, 4)
    ctext(d, (0, 1620, W, 1670), "※ 할랄팀장·팀원 각각 1부씩 발급하고 사본을 바인더 2번 탭에 보관", F(24), MUTED)
    im.save(OUT / "25_할랄팀_임명장.png", optimize=True)


def roster():
    W, H = 1600, 900
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 80), fill=GREEN)
    ctext(d, (0, 0, W, 80), "할랄팀 구성 현황 (이력현황 예시 · 매뉴얼 4.2.2)", F(36, "s"), "white")
    head = ["구분", "부서", "성명", "직위", "할랄팀 직무", "할랄 교육 이수", "비고"]
    cw = [150, 200, 160, 120, 380, 330, 180]
    rows = [["최고경영자", "경영", "○○○", "대표이사", "방침·자원 지원·경영검토", "사내 4시간 (20__.__.__)", ""],
            ["할랄팀장", "품질관리팀", "박○○", "팀장", "HAS 총괄·교육·내부감사·인증원 소통", "외부 8시간 (수료증)", "R&D 겸임"],
            ["팀원", "구매팀", "이○○", "대리", "승인 재료 구매·공급업체 평가", "사내 4시간", ""],
            ["팀원", "품질관리팀", "최○○", "과장", "입고 검사·이력추적·세척 절차", "사내 4시간", "내부감사원"],
            ["팀원", "물류팀", "정○○", "주임", "할랄 구분 보관·입출고", "사내 4시간", ""],
            ["팀원", "생산팀", "강○○", "반장", "교차오염 방지·생산 기록", "사내 4시간", "내부감사원"],
            ["팀원", "연구개발", "박○○", "팀장", "신재료·제품 성분 구성", "(팀장 겸임)", "겸임"]]
    x0, y0, rh = 30, 120, 82
    xs = [x0]
    for w in cw:
        xs.append(xs[-1] + w)
    for c, h in enumerate(head):
        d.rectangle((xs[c], y0, xs[c + 1], y0 + rh), fill=GREEN_D, outline="white", width=2)
        ctext(d, (xs[c], y0, xs[c + 1], y0 + rh), h, F(24, "b"), "white")
    for r, row in enumerate(rows):
        yy = y0 + rh * (r + 1)
        for c, v in enumerate(row):
            fill = GREEN_L if r == 1 else ("#FAFAFA" if r % 2 == 0 else "white")
            d.rectangle((xs[c], yy, xs[c + 1], yy + rh), fill=fill, outline="#C8E6C9", width=2)
            col = RED if (c == 6 and v) else INK
            ctext(d, (xs[c] + 6, yy, xs[c + 1] - 6, yy + rh), v, F(21, "b" if c in (0, 2) else "r"), col)
    ctext(d, (0, y0 + rh * 8 + 20, W, y0 + rh * 8 + 70),
          "※ 이름은 자리표시(○○)입니다. 실제 인원·직위·교육 이수일로 기입하고, 조직도와 반드시 일치시키세요.",
          F(23), MUTED)
    im.save(OUT / "26_할랄팀_구성현황.png", optimize=True)


if __name__ == "__main__":
    org_chart()
    appointment()
    roster()
    print("ok")
