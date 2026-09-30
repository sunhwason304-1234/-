"""content.py 를 PDF(미리보기·인쇄용)로 만든다. Chromium 헤드리스 인쇄 사용."""
import base64
import html
import subprocess
from pathlib import Path

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
OUT = HERE / f"{OUT_BASE}.pdf"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

GRADE = {"필수": "g-must", "중요": "g-imp", "권장": "g-rec"}
NOTE = {"warn": "주의", "info": "참고", "tip": "TIP"}


def e(s):
    return html.escape(str(s)).replace("\n", "<br>")


def img_tag(name, width_mm):
    data = base64.b64encode((IMG / name).read_bytes()).decode()
    return f'<img src="data:image/png;base64,{data}" style="width:{width_mm}mm">'


ROOMY = getattr(_c, "ROOMY", {})


def table(header, rows, weights, cls="", opts=None):
    opts = opts or {}
    tot = sum(weights)
    cols = "".join(f'<col style="width:{w / tot * 100:.1f}%">' for w in weights)
    th = "".join(f"<th>{e(h)}</th>" for h in header)
    row_h = opts.get("row_h", ROOMY.get("row_h"))
    center = set(opts.get("center", ()))
    def td(i, c):
        st = (f"height:{row_h}mm;" if row_h else "") + ("text-align:center;" if i in center else "")
        return f'<td style="{st}">{e(c)}</td>'
    body = "".join("<tr>" + "".join(td(i, c) for i, c in enumerate(r)) + "</tr>" for r in rows)
    if ROOMY:
        cls += " roomy"
    return f'<table class="{cls}"><colgroup>{cols}</colgroup><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


parts = []
for b in BLOCKS:
    k = b[0]
    if k == "section":
        parts.append(f'<h1 class="sec"><span>{e(b[1])}</span>{e(b[2])}</h1>')
    elif k == "sub":
        parts.append(f"<h2>{e(b[1])}</h2>")
    elif k == "p":
        parts.append(f"<p>{e(b[1])}</p>")
    elif k == "note":
        parts.append(f'<div class="note n-{b[2]}"><b>{NOTE[b[2]]}</b><div>{e(b[1])}</div></div>')
    elif k == "check":
        rows = "".join(
            f'<tr><td class="c">□</td><td class="c {GRADE[g]}">{g}</td><td>{e(i)}</td><td class="ev">{e(v)}</td></tr>'
            for g, i, v in b[1])
        parts.append('<table class="chk"><colgroup><col style="width:6%"><col style="width:8%">'
                     '<col style="width:62%"><col style="width:24%"></colgroup>'
                     f'<thead><tr><th>확인</th><th>등급</th><th>점검 항목</th><th>증빙·비고</th></tr></thead><tbody>{rows}</tbody></table>')
    elif k == "table":
        parts.append(table(b[1], b[2], b[3], opts=b[4] if len(b) > 4 else None))
    elif k == "img":
        parts.append(f'<figure>{img_tag(b[1], b[3])}<figcaption>{e(b[2])}</figcaption></figure>')

toc = table(["No", "내용"], [[b[1], b[2]] for b in BLOCKS if b[0] == "section"], [1, 9], "toc")

CSS = """
@page { size: A4; margin: 15mm; @bottom-center { content: counter(page); } }
body { font-family: 'Malgun Gothic','NanumGothic',sans-serif; color:#212121; font-size:10pt; line-height:1.55; }
.cover { height: 260mm; display:flex; flex-direction:column; justify-content:center; }
.cover .band { background:#2E7D32; color:#fff; padding:16mm 10mm; text-align:center; border-radius:4mm; }
.cover .band small { color:#C8E6C9; letter-spacing:2px; font-weight:bold; }
.cover .band h1 { font-size:26pt; margin:4mm 0; }
.cover figure { margin:8mm 0; }
.info td:first-child { background:#E8F5E9; color:#2E7D32; font-weight:bold; text-align:center; width:30%; }
.info td { height:9mm; }
h1.sec { break-before: page; background:#2E7D32; color:#fff; font-size:15pt; padding:2.5mm 4mm; margin:0 0 4mm; }
h1.sec span { display:inline-block; background:#1B5E20; padding:0 4mm; margin:-2.5mm 4mm -2.5mm -4mm; line-height:12mm; }
h2 { break-after:avoid; color:#1B5E20; font-size:12.5pt; margin:5mm 0 2mm; border-left:5px solid #2E7D32; padding-left:3mm; }
table { width:100%; border-collapse:collapse; margin:2mm 0 4mm; table-layout:fixed; }
th { background:#2E7D32; color:#fff; padding:1.6mm; font-size:9.5pt; }
td { border:1px solid #C8E6C9; padding:1.4mm 2mm; font-size:9.3pt; vertical-align:middle; }
tbody tr:nth-child(even) td { background:#FAFAFA; }
tr { break-inside: avoid; }
td.c { text-align:center; }
td.ev { color:#616161; font-size:8.8pt; }
td.g-must { background:#FFEBEE !important; color:#C62828; font-weight:bold; }
td.g-imp { background:#FFF3E0 !important; color:#E65100; font-weight:bold; }
td.g-rec { background:#E8F5E9 !important; color:#2E7D32; font-weight:bold; }
table.roomy td { padding:2.2mm 2.6mm; font-size:10.3pt; white-space:pre-wrap; }
table.roomy th { padding:2.4mm; font-size:10.5pt; }
.toc td:first-child { text-align:center; }
.note { display:flex; margin:3mm 0; border-radius:2mm; overflow:hidden; break-inside:avoid; }
.note b { color:#fff; min-width:16mm; display:flex; align-items:center; justify-content:center; }
.note div { padding:2.5mm 3mm; }
.n-warn b { background:#C62828; } .n-warn div { background:#FFEBEE; }
.n-info b { background:#1565C0; } .n-info div { background:#E3F2FD; }
.n-tip b { background:#2E7D32; } .n-tip div { background:#E8F5E9; }
figure { text-align:center; margin:3mm 0 5mm; break-inside:avoid; }
figure img { max-width:100%; border:1px solid #E0E0E0; }
figcaption { color:#616161; font-size:9pt; font-weight:bold; margin-top:1.5mm; }
.tochead { break-before: page; color:#2E7D32; font-size:18pt; }
"""

page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{e(TITLE)}</title><style>{CSS}</style></head><body>
<div class="cover"><div class="band"><small>{e(COVER_TAG)}</small><h1>{e(TITLE)}</h1><div>{e(SUBTITLE)}</div></div>
<figure>{img_tag(COVER_IMG, 150)}</figure>
<table class="info">{"".join(f"<tr><td>{e(k)}</td><td></td></tr>" for k in COVER_ROWS)}</table></div>
<h1 class="tochead">목 차</h1>{toc}
{''.join(parts)}
</body></html>"""

html_path = HERE / "_preview.html"
html_path.write_text(page, encoding="utf-8")
subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={OUT}", html_path.as_uri()], check=True, capture_output=True)
html_path.unlink()
print("PDF:", OUT, OUT.stat().st_size)
