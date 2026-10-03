"""content.py 를 한글(HWP 5.0 / HWPX) 문서로 만든다."""
from pathlib import Path

from hwpx import HwpxDocument

import importlib
import os

_c = importlib.import_module(os.environ.get("CONTENT", "content"))
BLOCKS, TITLE, SUBTITLE = _c.BLOCKS, _c.TITLE, _c.SUBTITLE
OUT_BASE = getattr(_c, "OUT_NAME", "할랄인증_현장심사_준비가이드")
COVER_IMG = getattr(_c, "COVER_IMG", "02_창고배치도.png")
COVER_ROWS = getattr(_c, "COVER_ROWS", ["회사명", "대상 공장 / 제품", "인증기관 / 심사 예정일", "작성자 / 작성일"])
COVER_TAG = getattr(_c, "COVER_TAG", "HALAL CERTIFICATION · ON-SITE AUDIT")
FOOTER = getattr(_c, "FOOTER", "할랄인증 현장심사 준비 가이드")

HERE = Path(__file__).parent
IMG = HERE / "images"
OUT_NAME = OUT_BASE

MM = 283.46
BODY_MM = 180
FONT = "맑은 고딕"

GREEN, GREEN_L = "#2E7D32", "#E8F5E9"
GRADE = {"필수": ("#C62828", "#FFEBEE"), "중요": ("#E65100", "#FFF3E0"), "권장": ("#2E7D32", "#E8F5E9")}
NOTE = {"warn": ("주의", "#C62828", "#FFEBEE"), "info": ("참고", "#1565C0", "#E3F2FD"), "tip": ("TIP", "#2E7D32", "#E8F5E9")}
INK, MUTED = "#212121", "#616161"

doc = HwpxDocument.new()
doc.page.set_margins(left=int(15 * MM), right=int(15 * MM), top=int(15 * MM), bottom=int(15 * MM),
                     header=int(8 * MM), footer=int(8 * MM))
fmt = doc.styles.apply_paragraph_format


def para(text="", *, size=10.5, bold=False, color=INK, align=None, before=None, after=None, page_break=False):
    p = doc.add_paragraph("", inherit_style=False)
    if text:
        p.add_run(text, bold=bold, color=color, size=size, font=FONT)
    kw = {}
    if align:
        kw["alignment"] = align
    if before is not None:
        kw["spacing_before_pt"] = before
    if after is not None:
        kw["spacing_after_pt"] = after
    if page_break:
        kw["page_break_before"] = True
    kw["line_spacing_percent"] = 150
    fmt(paragraphs=[p], **kw)
    return p


def cell_write(table, r, c, text, *, bold=False, color=INK, size=9.5, align="left", fill=None):
    cell = table.cell(r, c)
    lines = str(text).split("\n")
    first = cell.paragraphs[0]
    first.add_run(lines[0], bold=bold, color=color, size=size, font=FONT)
    paras = [first]
    for ln in lines[1:]:
        q = cell.add_paragraph("")
        q.add_run(ln, bold=bold, color=color, size=size, font=FONT)
        paras.append(q)
    fmt(paragraphs=paras, alignment=align, line_spacing_percent=ROOMY.get("ls", 130))
    if fill:
        table.set_cell_shading(r, c, fill)
    if ROOMY:
        # 셀 안쪽 여백을 넓히고 세로 가운데 정렬
        cell.set_margins(left=int(2.2 * MM), right=int(2.2 * MM), top=int(1.6 * MM), bottom=int(1.6 * MM))
        sub = cell.element.find("{http://www.hancom.co.kr/hwpml/2011/paragraph}subList")
        if sub is not None:
            sub.set("vertAlign", "CENTER")


ROOMY = getattr(_c, "ROOMY", {})


def make_table(header, rows, weights, *, header_fill=GREEN, center_cols=(), opts=None):
    opts = opts or {}
    body_size = ROOMY.get("size", 9.5)
    center_cols = set(center_cols) | set(opts.get("center", ()))
    t = doc.add_table(len(rows) + 1, len(header), width=int(BODY_MM * MM))
    t.set_column_widths(weights)
    for c, h in enumerate(header):
        cell_write(t, 0, c, h, bold=True, color="#FFFFFF", size=body_size + 0.5, align="center", fill=header_fill)
        if ROOMY:
            t.cell(0, c).set_size(height=int(ROOMY.get("head_h", 9) * MM))
    for r, row in enumerate(rows, start=1):
        for c, v in enumerate(row):
            cell_write(t, r, c, v, size=body_size, align="center" if c in center_cols else "left",
                       fill="#FAFAFA" if r % 2 == 0 else None)
            row_h = opts.get("row_h", ROOMY.get("row_h"))
            if row_h:
                t.cell(r, c).set_size(height=int(row_h * MM))
    if len(rows) > 8:
        t.set_treat_as_char(False)
    para("", size=4)
    return t


def check_table(items):
    t = doc.add_table(len(items) + 1, 4, width=int(BODY_MM * MM))
    t.set_column_widths([0.6, 0.8, 6.2, 2.4])
    for c, h in enumerate(["확인", "등급", "점검 항목", "증빙·비고"]):
        cell_write(t, 0, c, h, bold=True, color="#FFFFFF", size=10, align="center", fill=GREEN)
    for r, (grade, item, ev) in enumerate(items, start=1):
        fg, bg = GRADE[grade]
        cell_write(t, r, 0, "□", size=12, align="center")
        cell_write(t, r, 1, grade, bold=True, color=fg, align="center", fill=bg)
        cell_write(t, r, 2, item)
        cell_write(t, r, 3, ev, color=MUTED, size=9)
    if len(items) > 8:
        t.set_treat_as_char(False)
    para("", size=4)


def section_bar(num, title):
    t = doc.add_table(1, 2, width=int(BODY_MM * MM))
    t.set_column_widths([1, 11])
    cell_write(t, 0, 0, num, bold=True, color="#FFFFFF", size=16, align="center", fill="#1B5E20")
    cell_write(t, 0, 1, title, bold=True, color="#FFFFFF", size=15, fill=GREEN)
    para("", size=4)


def note_box(text, kind):
    label, fg, bg = NOTE[kind]
    t = doc.add_table(1, 2, width=int(BODY_MM * MM))
    t.set_column_widths([1, 11])
    cell_write(t, 0, 0, label, bold=True, color="#FFFFFF", size=10, align="center", fill=fg)
    cell_write(t, 0, 1, text, color=INK, size=10, fill=bg)
    para("", size=4)


def image(name, caption, width_mm):
    data = (IMG / name).read_bytes()
    from PIL import Image
    w, h = Image.open(IMG / name).size
    pic = doc.add_picture(data, "png", width_mm=width_mm, height_mm=width_mm * h / w, align="center")
    para(caption, size=9, bold=True, color=MUTED, align="center", after=6)
    return pic


# ------------------------------------------------------------------ 표지
doc.paragraphs[0].text = ""
para("", size=20, before=60)
cover = doc.add_table(1, 1, width=int(BODY_MM * MM))
cell_write(cover, 0, 0, COVER_TAG, bold=True, color="#C8E6C9", size=12, align="center",
           fill=GREEN)
q = cover.cell(0, 0).add_paragraph("")
q.add_run(TITLE, bold=True, color="#FFFFFF", size=26, font=FONT)
q2 = cover.cell(0, 0).add_paragraph("")
q2.add_run(SUBTITLE, color="#FFFFFF", size=12, font=FONT)
fmt(paragraphs=[q, q2], alignment="center", line_spacing_percent=180)
para("", size=10, after=20)
image(COVER_IMG, "", 150)
info = doc.add_table(len(COVER_ROWS), 2, width=int(BODY_MM * MM))
info.set_column_widths([1, 3])
for i, k in enumerate(COVER_ROWS):
    cell_write(info, i, 0, k, bold=True, color=GREEN, align="center", fill=GREEN_L)
    cell_write(info, i, 1, "")

# ------------------------------------------------------------------ 목차
para("목  차", size=18, bold=True, color=GREEN, page_break=True, after=10)
toc_rows = [[b[1], b[2]] for b in BLOCKS if b[0] == "section"]
make_table(["No", "내용"], toc_rows, [1, 9], center_cols=(0,))

# ------------------------------------------------------------------ 본문
first = True
for blk in BLOCKS:
    kind = blk[0]
    if kind == "section":
        # 대단원마다 새 쪽에서 시작
        para("", size=2, page_break=True)
        section_bar(blk[1], blk[2])
    elif kind == "sub":
        para(blk[1], size=12.5, bold=True, color="#1B5E20", before=8, after=4)
    elif kind == "p":
        para(blk[1], size=10.5, after=6)
    elif kind == "note":
        note_box(blk[1], blk[2])
    elif kind == "check":
        check_table(blk[1])
    elif kind == "table":
        make_table(blk[1], blk[2], blk[3], opts=blk[4] if len(blk) > 4 else None)
    elif kind == "img":
        image(blk[1], blk[2], blk[3])

doc.page.set_footer(text=FOOTER)
doc.page.set_page_number(target="header", align="RIGHT", position="TOP_RIGHT", prefix="- ", suffix=" -")

print(doc.validate())
doc.save_to_path(HERE / f"{OUT_NAME}.hwpx")
doc.save_to_path(HERE / f"{OUT_NAME}.hwp")
chk = HwpxDocument.open(HERE / f"{OUT_NAME}.hwp")
print("hwp reopened; conversion report:", chk.conversion_report)
print("pictures:", len(chk.oxml.sections[0].element.findall(".//{*}pic")))
