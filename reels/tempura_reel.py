# 당진 호풍미 호박고구마 '고구마 튀김' 릴스 — 음악 박자에 맞춘 빠른 컷 편집
# 사용: python3 tempura_reel.py <작업폴더>   (ai/t0~t4.mp4, music.mp3, fonts/BHS.ttf 필요)
# 음악: Kevin MacLeod "Local Forecast" (incompetech.com, CC BY 4.0)
import os, subprocess, sys
import numpy as np

W, H, FPS = 1080, 1920, 30
D = sys.argv[1] if len(sys.argv) > 1 else "."
FONT = f"{D}/fonts/BHS.ttf"
os.makedirs(f"{D}/seg", exist_ok=True)
os.makedirs(f"{D}/txt", exist_ok=True)
YEL, WHT = "0xFFE14D", "white"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:])
        raise SystemExit("ffmpeg failed")


# ── 1. 음악 박자 분석: 템포·박 위치 찾기, 인트로 지나 꽉 찬 구간에서 시작 ──
def beat_grid(path, bpm_lo=90, bpm_hi=160, sr=11025, hop=128):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-t", "60", "-i", path, "-ac", "1", "-ar", str(sr),
                          "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float)
    n = len(x) // hop
    e = (x[: n * hop].reshape(n, hop) ** 2).sum(1)
    o = np.maximum(np.diff(np.log1p(e), prepend=0), 0)
    fps = sr / hop
    oc = o - o.mean()
    ac = np.correlate(oc, oc, "full")[len(oc) - 1:]
    lags = np.arange(int(fps * 60 / bpm_hi), int(fps * 60 / bpm_lo))
    period = lags[np.argmax(ac[lags])] / fps
    # 박 위상: 그리드 위 onset 합이 최대가 되는 오프셋
    k = np.arange(0, 60 / period - 1)
    best = max(np.arange(0, period, 1 / fps),
               key=lambda ph: o[np.clip(((ph + k * period) * fps).astype(int), 0, n - 1)].sum())
    rms = np.sqrt(e / hop)
    sm = np.convolve(rms, np.ones(int(fps)) / fps, "same")
    full = np.argmax(sm > 0.75 * np.median(sm[: int(40 * fps)])) / fps
    start = best + np.ceil((full - best) / period) * period
    return period, start


# ── 2. 컷 구성 (클립, 소스 시작초, 박 수, [자막]) ──
def dt(text, y, size=88, color=WHT, a=0.0):
    p = f"{D}/txt/{abs(hash((text, y, a)))}.txt"
    open(p, "w", encoding="utf-8").write(text)
    return (f"drawtext=fontfile={FONT}:textfile={p}:fontsize={size}:fontcolor={color}"
            f":borderw=8:bordercolor=black:shadowcolor=black@0.5:shadowx=3:shadowy=5"
            f":x=(w-text_w)/2:y={y}:enable='gte(t,{a})'")


TOP1, TOP2, LOW = 300, 410, 1300
CUTS = [
    ("t4", 1.0, 3, [dt("고구마 튀김 이렇게 하면", TOP1), dt("겉바속촉 끝판왕", TOP2, 96, YEL)]),
    ("t0", 0.4, 2, [dt("당진 호풍미 호박고구마", TOP1, 84, YEL)]),
    ("t0", 3.2, 1, []),
    ("t1", 0.6, 2, [dt("튀김옷 얇게 입히고", TOP1, 84)]),
    ("t1", 2.6, 2, []),
    ("t2", 0.4, 2, [dt("지글지글~", TOP1, 96, YEL)]),
    ("t2", 2.8, 2, []),
    ("t3", 0.4, 2, [dt("바삭하게 건져서", TOP1, 84)]),
    ("t3", 2.6, 2, []),
    ("t4", 0.0, 4, [dt("속은 꿀처럼 촉촉", TOP1, 92, YEL)]),
    ("t4", 3.0, 3, [dt("당진 호풍미 호박고구마", TOP1, 84, YEL),
                    dt("주문은 프로필 링크 클릭!", LOW, 80, WHT)]),
]


def main():
    music = f"{D}/music.mp3"
    period, mstart = beat_grid(music)
    print(f"tempo {60/period:.1f} BPM, music start {mstart:.2f}s")
    parts, t = [], 0.0
    for i, (clip, ss, beats, texts) in enumerate(CUTS):
        # 프레임 단위 누적 오차 없이 박에 정확히 맞춤
        f0, f1 = round(t * FPS), round((t + beats * period) * FPS)
        dur = (f1 - f0) / FPS
        t += beats * period
        vf = ",".join([f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                       f"fps={FPS}", "setsar=1",
                       "eq=contrast=1.04:saturation=1.06"] + texts + ["format=yuv420p"])
        out = f"{D}/seg/c{i:02d}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", f"{dur:.4f}", "-i", f"{D}/ai/{clip}.mp4",
             "-f", "lavfi", "-t", f"{dur:.4f}", "-i", "anullsrc=r=44100:cl=stereo",
             "-filter_complex", f"[0:v]{vf}[v];[0:a]aresample=44100,apad[a0];[a0][1:a]amix=inputs=2:duration=shortest[a]",
             "-map", "[v]", "-map", "[a]", "-frames:v", str(f1 - f0),
             "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "aac", "-ar", "44100", "-ac", "2", out])
        parts.append(out)
    lst = f"{D}/seg/list.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    body = f"{D}/seg/body.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", body])
    total = t
    out = f"{D}/reel3_goguma_tempura.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", body, "-ss", f"{mstart:.3f}", "-i", music, "-filter_complex",
         f"[1:a]atrim=0:{total:.3f},afade=t=in:d=0.05,afade=t=out:st={total-0.6:.3f}:d=0.6,volume=0.9[m];"
         f"[0:a]volume=0.55[s];[m][s]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", f"{total:.3f}", "-movflags", "+faststart", out])
    print(out, f"{total:.2f}s")


main()
