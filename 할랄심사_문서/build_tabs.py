"""바인더 앞표지·등표지·전체 목차·탭 간지·탭 라벨을 한글(HWP/HWPX)과 PDF로 만든다."""
import base64
import html
import subprocess
from pathlib import Path

from hwpx import HwpxDocument
from PIL import Image, ImageDraw, ImageFont

from tabs_data import CERT_BODY, COMPANY, KEEPER, MANUAL, TABS

HERE = Path(__file__).parent
IMG = HERE / "images"
OUT = "HAS바인더_탭표지_및_목차"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FD = "/usr/share/fonts/truetype/nanum/"
MM = 283.46
BODY_MM = 180
FONT = "맑은 고딕"
GREEN, GREEN_D, GREEN_L, INK, MUTED = "#2E7D32", "#1B5E20", "#E8F5E9", "#212121", "#616161"


# ------------------------------------------------------------------ 등표지 이미지
def spine_image():
    px = 10  # 1mm = 10px
    widths = [30, 50, 70]
    H = 255
    W = sum(widths) + 2 * 25 + 10
    im = Image.new("RGB", (W * px, H * px), "white")
    d = ImageDraw.Draw(im)
    x = 5
    for w in widths:
        x0, x1 = x * px, (x + w) * px
        d.rectangle((x0, 0, x1 - 1, H * px - 1), outline="#9E9E9E", width=3)  # 절취선
        d.rectangle((x0 + 20, 20, x1 - 20, 45 * px), fill=GREEN)
        d.rectangle((x0 + 20, 200 * px, x1 - 20, H * px - 20), fill=GREEN_D)

        def vtext(text, size, box, color, bold=True):
            bx0, by0, bx1, by1 = box
            while True:  # 상자에 들어갈 때까지 글자 크기를 줄인다
                f = ImageFont.truetype(FD + ("NanumSquareB.ttf" if bold else "NanumGothic.ttf"), size)
                bb = f.getbbox(text)
                tw, th = bb[2] - bb[0], bb[3] - bb[1]
                if (tw <= (by1 - by0) * 0.9 and th <= (bx1 - bx0) * 0.8) or size < 12:
                    break
                size -= 4
            t = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
            ImageDraw.Draw(t).text((10 - bb[0], 10 - bb[1]), text, font=f, fill=color)
            t = t.rotate(-90, expand=True)
            im.paste(t, (int((bx0 + bx1 - t.width) / 2), int((by0 + by1 - t.height) / 2)), t)
        s = min(w * px * 0.55, 190)
        vtext("HALAL", int(s), (x0, 20, x1, 45 * px), "white")
        vtext("할랄 보증시스템 심사 바인더", int(s * 0.7), (x0, 47 * px, x1, 165 * px), INK)
        vtext(f"{MANUAL} · 관리본", int(s * 0.45), (x0, 165 * px, x1, 198 * px), MUTED, bold=False)
        vtext(COMPANY if w > 30 else "약석원", int(s * 0.6), (x0, 200 * px, x1, H * px - 20), "white")
        x += w + 25
    im.save(IMG / "20_등표지.png", optimize=True)


# ------------------------------------------------------------------ HWP
spine_image()
doc = HwpxDocument.new()
doc.page.set_margins(left=int(15 * MM), right=int(15 * MM), top=int(15 * MM), bottom=int(12 * MM),
                     header=int(6 * MM), footer=int(6 * MM))
fmt = doc.styles.apply_paragraph_format


def para(text="", *, size=10.5, bold=False, color=INK, align=None, before=None, after=None, page_break=False):
    p = doc.add_paragraph("", inherit_style=False)
    if text:
        p.add_run(text, bold=bold, color=color, size=size, font=FONT)
    kw = {"line_spacing_percent": 150}
    if align:
        kw["alignment"] = align
    if before is not None:
        kw["spacing_before_pt"] = before
    if after is not None:
        kw["spacing_after_pt"] = after
    if page_break:
        kw["page_break_before"] = True
    fmt(paragraphs=[p], **kw)
    return p


def cw(t, r, c, text, *, bold=False, color=INK, size=10, align="left", fill=None, ls=140):
    cell = t.cell(r, c)
    lines = str(text).split("\n")
    ps = [cell.paragraphs[0]]
    ps[0].add_run(lines[0], bold=bold, color=color, size=size, font=FONT)
    for ln in lines[1:]:
        q = cell.add_paragraph("")
        q.add_run(ln, bold=bold, color=color, size=size, font=FONT)
        ps.append(q)
    fmt(paragraphs=ps, alignment=align, line_spacing_percent=ls)
    if fill:
        t.set_cell_shading(r, c, fill)


def table(nrows, ncols, weights):
    t = doc.add_table(nrows, ncols, width=int(BODY_MM * MM))
    t.set_column_widths(weights)
    return t


def picture(name, width_mm):
    w, h = Image.open(IMG / name).size
    doc.add_picture((IMG / name).read_bytes(), "png", width_mm=width_mm, height_mm=width_mm * h / w, align="center")


# 1) 앞표지
doc.paragraphs[0].text = ""
para("", before=40)
t = table(1, 1, [1])
cw(t, 0, 0, "HALAL ASSURANCE SYSTEM", bold=True, color="#C8E6C9", size=14, align="center", fill=GREEN)
for txt, sz in (("할랄 보증시스템", 34), ("심사 바인더", 34), (f"{COMPANY}", 16)):
    q = t.cell(0, 0).add_paragraph("")
    q.add_run(txt, bold=True, color="#FFFFFF", size=sz, font=FONT)
    fmt(paragraphs=[q], alignment="center", line_spacing_percent=170)
para("", after=16)
t = table(1, 2, [1, 1])
cw(t, 0, 0, "■  관리본 (CONTROL)", bold=True, color="#C62828", size=16, align="center", fill="#FFEBEE")
cw(t, 0, 1, "□  비관리본 (NO CONTROL)", bold=True, color=MUTED, size=16, align="center", fill="#F5F5F5")
para("", after=10)
rows = [("매뉴얼 번호", f"{MANUAL}  (개정번호 ____ )"), ("인증기관", CERT_BODY), ("인증 제품", ""),
        ("바인더 번호", "제 ____ 권 / 총 ____ 권"), ("보관 부서 / 책임자", f"{KEEPER} /"),
        ("편철 기간", "20___. ___. ___  ~  20___. ___. ___")]
t = table(len(rows), 2, [1, 2.4])
for i, (k, v) in enumerate(rows):
    cw(t, i, 0, k, bold=True, color=GREEN, size=13, align="center", fill=GREEN_L, ls=220)
    cw(t, i, 1, v, size=13, ls=220)
para("", after=10)
t = table(1, 4, [1, 1, 1, 1])
for c, k in enumerate(["작성", "검토", "승인", "최종 점검일"]):
    cw(t, 0, c, f"{k}\n\n\n", bold=True, color=GREEN, size=11, align="center")
para("※ 이 바인더는 현장심사 시 심사원에게 제시하는 할랄 보증시스템 문서철입니다. 무단 반출 금지.",
     size=9, color=MUTED, align="center", before=12)

# 2) 등표지
para("바인더 등표지 (옆면 라벨)", size=18, bold=True, color=GREEN, page_break=True, after=2)
para("바인더 두께에 맞는 것을 회색 선을 따라 잘라 옆면 꽂이에 넣으세요. (왼쪽부터 3cm · 5cm · 7cm 폭)",
     size=10, color=MUTED, after=6)
picture("20_등표지.png", 160)

# 3) 전체 목차
para("전 체 목 차", size=20, bold=True, color=GREEN, align="center", page_break=True, after=4)
para(f"{COMPANY} · 할랄 보증시스템 매뉴얼 {MANUAL} 기준 · 보관 부서 {KEEPER}", size=10, color=MUTED,
     align="center", after=8)
flat = [(n, name, color, doc_) for n, name, color, _, docs, _ in TABS for doc_ in docs]
t = table(len(flat) + 1, 6, [0.7, 1.3, 4.2, 1.8, 1.7, 1.0])
for c, h in enumerate(["탭", "구분", "문서명", "서식번호", "작성주기", "보존"]):
    cw(t, 0, c, h, bold=True, color="#FFFFFF", align="center", fill=GREEN_D)
r = 1
for n, name, color, _, docs, _ in TABS:
    start = r
    for dname, form, cyc, keep in docs:
        cw(t, r, 2, dname, size=9.5)
        cw(t, r, 3, form, size=9, align="center")
        cw(t, r, 4, cyc, size=9, align="center")
        cw(t, r, 5, keep, size=9, align="center")
        r += 1
    cw(t, start, 0, n, bold=True, color="#FFFFFF", size=12, align="center", fill=color)
    cw(t, start, 1, name, bold=True, color=color, size=10, align="center")
    if r - 1 > start:
        doc.tables.merge_cells(t, f"A{start + 1}:A{r}")
        doc.tables.merge_cells(t, f"B{start + 1}:B{r}")
t.set_treat_as_char(False)
para("※ 서식번호·작성주기·보존연한은 매뉴얼 4.17 기록 및 보관관리, 6.0 첨부 목록 기준입니다. "
     "'-'는 매뉴얼에 정해지지 않은 항목입니다.", size=9, color=MUTED, before=6)

# 4) 탭 간지 13장
for n, name, color, basis, docs, note in TABS:
    para("", size=2, page_break=True)
    t = table(1, 2, [1, 3])
    cw(t, 0, 0, n, bold=True, color="#FFFFFF", size=60, align="center", fill=color, ls=110)
    cw(t, 0, 1, f"{name}", bold=True, color="#FFFFFF", size=32, fill=color, ls=120)
    q = t.cell(0, 1).add_paragraph("")
    q.add_run(f"매뉴얼 근거 : {basis}", color="#FFFFFF", size=12, font=FONT)
    para("", after=10)
    para("이 탭에 편철하는 문서", size=14, bold=True, color=color, after=4)
    t = table(len(docs) + 1, 7, [0.5, 3.6, 1.7, 1.6, 0.9, 0.7, 1.5])
    for c, h in enumerate(["No", "문서명", "서식번호", "작성주기", "보존", "비치", "최종 편철일"]):
        cw(t, 0, c, h, bold=True, color="#FFFFFF", size=10, align="center", fill=color)
    for i, (dname, form, cyc, keep) in enumerate(docs, start=1):
        for c, v in enumerate([str(i), dname, form, cyc, keep, "□", "   .    .   "]):
            cw(t, i, c, v, size=10.5 if c == 1 else 9.5, align="left" if c == 1 else "center",
               bold=(c == 1), color=INK if c != 6 else MUTED, ls=200)
    para("", after=8)
    t = table(1, 2, [1, 9])
    cw(t, 0, 0, "주의", bold=True, color="#FFFFFF", align="center", fill="#C62828")
    cw(t, 0, 1, note, size=10.5, fill="#FFEBEE", ls=160)
    para("", after=10)
    t = table(2, 4, [1, 1, 1, 1])
    for c, h in enumerate(["보관 부서", "편철 담당", "확인자", "확인일"]):
        cw(t, 0, c, h, bold=True, color=color, align="center", fill="#F5F5F5")
        cw(t, 1, c, KEEPER if c == 0 else "", align="center", ls=260)

# 5) 탭 라벨
para("탭 인덱스 라벨 (잘라서 사용)", size=18, bold=True, color=GREEN, page_break=True, after=2)
para("색지 인덱스 탭의 라벨 꽂이에 넣거나, 라벨지에 출력해 붙이세요.", size=10, color=MUTED, after=8)
t = table(7, 4, [0.5, 2, 0.5, 2])
for i, (n, name, color, *_rest) in enumerate(TABS):
    r, c = i % 7, (i // 7) * 2
    cw(t, r, c, n, bold=True, color="#FFFFFF", size=18, align="center", fill=color, ls=200)
    cw(t, r, c + 1, name, bold=True, color=color, size=16, ls=200)

doc.page.set_footer(text=f"{COMPANY} · 할랄 보증시스템 심사 바인더")


# ------------------------------------------------------------------ PDF (같은 내용)
def e(s):
    return html.escape(str(s)).replace("\n", "<br>")


def img64(name):
    return "data:image/png;base64," + base64.b64encode((IMG / name).read_bytes()).decode()


def build_pdf():
    P = []
    P.append(f"""<section class="cover">
<div class="band"><small>HALAL ASSURANCE SYSTEM</small><h1>할랄 보증시스템<br>심사 바인더</h1><div class="co">{e(COMPANY)}</div></div>
<table class="ctl"><tr><td class="on">■ 관리본 (CONTROL)</td><td class="off">□ 비관리본 (NO CONTROL)</td></tr></table>
<table class="kv">{''.join(f'<tr><th>{e(k)}</th><td>{e(v)}</td></tr>' for k, v in rows)}</table>
<table class="sign"><tr>{''.join(f'<th>{k}</th>' for k in ['작성', '검토', '승인', '최종 점검일'])}</tr><tr>{'<td></td>' * 4}</tr></table>
<p class="muted c">※ 이 바인더는 현장심사 시 심사원에게 제시하는 할랄 보증시스템 문서철입니다. 무단 반출 금지.</p></section>""")
    P.append(f"""<section><h2>바인더 등표지 (옆면 라벨)</h2><p class="muted">바인더 두께에 맞는 것을 회색 선을 따라 잘라 옆면 꽂이에 넣으세요. (왼쪽부터 3cm · 5cm · 7cm 폭)</p>
<img src="{img64('20_등표지.png')}" style="width:160mm;display:block;margin:0 auto"></section>""")
    trs = []
    for n, name, color, _, docs, _ in TABS:
        for i, (dn, fo, cy, ke) in enumerate(docs):
            lead = (f'<td rowspan="{len(docs)}" class="c tabno" style="background:{color}">{n}</td>'
                    f'<td rowspan="{len(docs)}" class="c b" style="color:{color}">{e(name)}</td>') if i == 0 else ""
            trs.append(f"<tr>{lead}<td>{e(dn)}</td><td class='c s'>{e(fo)}</td><td class='c s'>{e(cy)}</td><td class='c s'>{e(ke)}</td></tr>")
    P.append(f"""<section><h1 class="c g">전 체 목 차</h1><p class="c muted">{e(COMPANY)} · 할랄 보증시스템 매뉴얼 {MANUAL} 기준 · 보관 부서 {KEEPER}</p>
<table class="idx"><colgroup><col style="width:6%"><col style="width:12%"><col style="width:39%"><col style="width:16%"><col style="width:17%"><col style="width:10%"></colgroup>
<tr><th>탭</th><th>구분</th><th>문서명</th><th>서식번호</th><th>작성주기</th><th>보존</th></tr>{''.join(trs)}</table>
<p class="muted s">※ 서식번호·작성주기·보존연한은 매뉴얼 4.17 기록 및 보관관리, 6.0 첨부 목록 기준입니다. '-'는 매뉴얼에 정해지지 않은 항목입니다.</p></section>""")
    for n, name, color, basis, docs, note in TABS:
        rows_ = "".join(f"<tr><td class='c'>{i}</td><td class='b'>{e(dn)}</td><td class='c s'>{e(fo)}</td><td class='c s'>{e(cy)}</td>"
                        f"<td class='c s'>{e(ke)}</td><td class='c'>□</td><td class='c muted'>&nbsp;.&nbsp;&nbsp;&nbsp;.&nbsp;</td></tr>"
                        for i, (dn, fo, cy, ke) in enumerate(docs, 1))
        P.append(f"""<section><div class="tabband" style="background:{color}"><div class="no">{n}</div><div><div class="nm">{e(name)}</div><div>매뉴얼 근거 : {e(basis)}</div></div></div>
<h3 style="color:{color}">이 탭에 편철하는 문서</h3>
<table class="docs"><colgroup><col style="width:5%"><col style="width:34%"><col style="width:16%"><col style="width:15%"><col style="width:8%"><col style="width:7%"><col style="width:15%"></colgroup>
<tr>{''.join(f'<th style="background:{color}">{h}</th>' for h in ['No', '문서명', '서식번호', '작성주기', '보존', '비치', '최종 편철일'])}</tr>{rows_}</table>
<div class="note"><b>주의</b><div>{e(note)}</div></div>
<table class="sign"><tr>{''.join(f'<th style="color:{color}">{k}</th>' for k in ['보관 부서', '편철 담당', '확인자', '확인일'])}</tr><tr><td class="c">{KEEPER}</td><td></td><td></td><td></td></tr></table></section>""")
    def lab(i):
        if i >= len(TABS):
            return "<td></td><td></td>"
        n, name, color = TABS[i][:3]
        return (f'<td class="lno" style="background:{color}">{n}</td>'
                f'<td class="lnm" style="color:{color}">{e(name)}</td>')
    labels = "".join("<tr>" + lab(r) + lab(r + 7) + "</tr>" for r in range(7))
    P.append(f"""<section><h2>탭 인덱스 라벨 (잘라서 사용)</h2><p class="muted">색지 인덱스 탭의 라벨 꽂이에 넣거나, 라벨지에 출력해 붙이세요.</p>
<table class="lab"><colgroup><col style="width:10%"><col style="width:40%"><col style="width:10%"><col style="width:40%"></colgroup>{labels}</table></section>""")
    css = """
@page { size:A4; margin:15mm 15mm 12mm; }
body { font-family:'Malgun Gothic','NanumGothic',sans-serif; color:#212121; font-size:10.5pt; margin:0; }
section { break-after:page; } section:last-child { break-after:auto; }
.c { text-align:center; } .b { font-weight:bold; } .s { font-size:9pt; } .muted { color:#616161; } .g { color:#2E7D32; }
table { width:100%; border-collapse:collapse; table-layout:fixed; }
th, td { border:1px solid #BDBDBD; padding:1.6mm 2mm; }
th { background:#1B5E20; color:#fff; }
.cover .band { background:#2E7D32; color:#fff; text-align:center; padding:14mm 8mm; margin-top:12mm; }
.cover .band small { color:#C8E6C9; font-weight:bold; letter-spacing:2px; font-size:13pt; }
.cover .band h1 { font-size:34pt; line-height:1.35; margin:5mm 0; } .co { font-size:16pt; font-weight:bold; }
.ctl { margin:8mm 0; } .ctl td { text-align:center; font-weight:bold; font-size:15pt; padding:4mm; }
.ctl .on { background:#FFEBEE; color:#C62828; } .ctl .off { background:#F5F5F5; color:#616161; }
.kv th { background:#E8F5E9; color:#2E7D32; width:30%; font-size:13pt; padding:4.5mm; } .kv td { font-size:13pt; }
.sign { margin-top:8mm; } .sign th { background:#F5F5F5; color:#2E7D32; } .sign td { height:18mm; }
h2 { color:#2E7D32; font-size:18pt; margin:0 0 2mm; } h1.g { font-size:20pt; margin:0; letter-spacing:4px; }
.idx td { font-size:9.5pt; padding:1.2mm 2mm; } .idx tr { break-inside:avoid; }
.tabno { color:#fff; font-weight:bold; font-size:13pt; }
.tabband { display:flex; align-items:center; color:#fff; padding:6mm 8mm; gap:10mm; margin-bottom:8mm; }
.tabband .no { font-size:64pt; font-weight:bold; min-width:34mm; text-align:center; }
.tabband .nm { font-size:32pt; font-weight:bold; }
h3 { font-size:14pt; margin:0 0 3mm; } .docs th { color:#fff; } .docs td { height:10mm; }
.note { display:flex; margin:8mm 0; } .note b { background:#C62828; color:#fff; padding:3mm 5mm; display:flex; align-items:center; }
.note div { background:#FFEBEE; padding:3mm 4mm; flex:1; }
.lab td { height:16mm; } .lno { color:#fff; font-weight:bold; font-size:20pt; text-align:center; } .lnm { font-weight:bold; font-size:17pt; }
"""
    page = f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>HAS 바인더 탭표지</title><style>{css}</style></head><body>{"".join(P)}</body></html>'
    hp = HERE / "_tabs.html"
    hp.write_text(page, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={HERE / (OUT + '.pdf')}", hp.as_uri()], check=True, capture_output=True)
    hp.unlink()


if __name__ == "__main__":
    print(doc.validate())
    doc.save_to_path(HERE / f"{OUT}.hwpx")
    doc.save_to_path(HERE / f"{OUT}.hwp")
    print(HwpxDocument.open(HERE / f"{OUT}.hwp").conversion_report)
    build_pdf()
    print("done")
