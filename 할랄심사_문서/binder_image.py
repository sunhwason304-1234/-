"""할랄 심사 바인더 탭 구성 예시 그림."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "images" / "19_바인더구성.png"
FD = "/usr/share/fonts/truetype/nanum/"
F = lambda s, b=False: ImageFont.truetype(FD + ("NanumSquareB.ttf" if b else "NanumGothic.ttf"), s)

TABS = [("1", "HAS 매뉴얼"), ("2", "할랄팀"), ("3", "교육"), ("4", "재료"), ("5", "공급업체"),
        ("6", "제품"), ("7", "입고·보관"), ("8", "생산·위생"), ("9", "출고·추적"), ("10", "검사"),
        ("11", "부적합"), ("12", "감사·검토"), ("13", "첨부 1~8")]
COLS = ["#2E7D32", "#1565C0", "#6A1B9A", "#EF6C00", "#00838F", "#AD1457", "#F9A825",
        "#558B2F", "#4527A0", "#D84315", "#C62828", "#37474F", "#5D4037"]

W, H = 1600, 900
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 70), fill="#2E7D32")
t = "할랄 심사 바인더 탭 구성 (예시)"
bb = d.textbbox((0, 0), t, font=F(32, True))
d.text(((W - bb[2]) / 2, 15), t, font=F(32, True), fill="white")

# 바인더 본체
x0, y0, x1, y1 = 120, 120, 1080, 860
d.rounded_rectangle((x0 - 30, y0, x1, y1), 20, fill="#263238")
d.rectangle((x0, y0 + 20, x1 - 20, y1 - 20), fill="#FAFAFA")
for k in range(3):
    cy = y0 + 150 + k * 250
    d.ellipse((x0 - 20, cy - 22, x0 + 24, cy + 22), fill="#B0BEC5", outline="#546E7A", width=4)
# 표지
d.rectangle((x0 + 90, y0 + 90, x1 - 110, y0 + 330), fill="#2E7D32")
for i, (txt, sz) in enumerate([("할랄 보증시스템", 44), ("HAS 심사 바인더", 40), ("주약석원농업회사법인 · 관리본", 26)]):
    bb = d.textbbox((0, 0), txt, font=F(sz, True))
    d.text(((x0 + 90 + x1 - 110 - bb[2]) / 2, y0 + 115 + i * 70), txt, font=F(sz, True), fill="white")
lines = ["• 인증기관 : 한국할랄인증원(KHA)", "• 매뉴얼 : YSW-100 (개정 0)", "• 심사원 요청 시 1분 내 제시",
         "• 탭 번호 = 본문 2장 표의 번호"]
for i, s in enumerate(lines):
    d.text((x0 + 110, y0 + 390 + i * 60), s, font=F(28), fill="#212121")

# 탭
th = (y1 - y0 - 40) / len(TABS)
for i, ((n, name), c) in enumerate(zip(TABS, COLS)):
    ty = y0 + 20 + i * th
    d.rounded_rectangle((x1 - 20, ty + 3, x1 + 470, ty + th - 3), 10, fill=c)
    d.text((x1 + 5, ty + th / 2 - 17), f"{n:>2}", font=F(28, True), fill="white")
    d.text((x1 + 75, ty + th / 2 - 16), name, font=F(28, True), fill="white")
im.save(OUT, optimize=True)
print(OUT)
