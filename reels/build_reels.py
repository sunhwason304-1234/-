# 당진 호풍미 호박고구마 × 말티즈 릴스 2편 편집 스크립트 (ffmpeg)
# 사용: python3 build_reels.py <작업폴더>  (src/, ai/, music/, fonts/ 가 준비돼 있어야 함)
import os, subprocess, sys

W, H, FPS = 1080, 1920, 30
D = sys.argv[1] if len(sys.argv) > 1 else "."
FONT = f"{D}/fonts/BHS.ttf"
TXT = f"{D}/txt"
os.makedirs(TXT, exist_ok=True)
os.makedirs(f"{D}/seg", exist_ok=True)
YEL, WHT, PINK = "0xFFE14D", "white", "0xFF7EB6"
_n = [0]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:])
        raise SystemExit(f"ffmpeg failed: {' '.join(cmd[:6])}")


def dt(text, y, size=84, color=WHT, a=0.0, b=99.0, border=9):
    _n[0] += 1
    p = f"{TXT}/t{_n[0]}.txt"
    open(p, "w", encoding="utf-8").write(text)
    return (f"drawtext=fontfile={FONT}:textfile={p}:fontsize={size}:fontcolor={color}"
            f":borderw={border}:bordercolor=black:shadowcolor=black@0.6:shadowx=4:shadowy=6"
            f":x=(w-text_w)/2:y={y}:enable='between(t,{a},{b})'"
            f":alpha='if(lt(t,{a}),0,min(1,(t-{a})*7))'")


def frame_fit(kind, fgw=W):
    # kind: cover (꽉 채우기) / blur (흐린 배경 + 가운데 원본)
    if kind == "cover":
        return f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    return (f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"boxblur=40:6,eq=brightness=-0.08[bg];[b]scale={fgw}:-2,crop=min(iw\\,{W}):ih[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")


def seg(out, src, dur, texts, ss=0.0, fit="cover", still=False, audio=False, zoom=True):
    fl = [frame_fit(fit, 1460 if (fit == "blur" and not still) else W)]
    if still and zoom:  # 사진은 천천히 줌인 (켄번즈)
        fl.append(f"scale={W*2}:{H*2},zoompan=z='min(1+0.0016*on,1.12)':x='iw/2-(iw/zoom/2)'"
                  f":y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}")
    fl += [f"fps={FPS}", "setsar=1"] + texts + ["format=yuv420p"]
    vf = ",".join(fl)
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if still:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", src]
    else:
        cmd += ["-ss", str(ss), "-t", str(dur), "-i", src]
    cmd += ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo"]
    amap = "0:a" if audio else "1:a"
    cmd += ["-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", amap,
            "-t", str(dur), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k", out]
    run(cmd)
    return out


def build(name, parts, music, music_vol=0.55):
    lst = f"{D}/seg/{name}.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    body = f"{D}/seg/{name}_body.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", body])
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", body]).decode())
    out = f"{D}/{name}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", body, "-i", music, "-filter_complex",
         f"[1:a]atrim=0:{dur},afade=t=out:st={dur-1.0}:d=1,volume={music_vol}[m];"
         f"[0:a]volume=1.0[s];[s][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", out])
    return out


S, A, M = f"{D}/src", f"{D}/ai", f"{D}/music"
TOP1, TOP2, MID, LOW = 290, 400, 1180, 1300
TIP = "* 강아지는 껍질 벗기고 식혀서 아주 조금만!"

# ───────── 릴스 1 : 말티즈 몰카 (냄새 맡더니 충격) ─────────
r1 = [
    seg(f"{D}/seg/r1_1.mp4", f"{A}/ai0.mp4", 4.5, [
        dt("말티즈한테 이 고구마", TOP1, 88),
        dt("냄새만 맡게 했더니ㅋㅋ", TOP2, 88, YEL),
        dt("동공지진 실화?!", LOW, 96, PINK, a=2.6)], audio=True),
    seg(f"{D}/seg/r1_2.mp4", f"{S}/v_pan1.mp4", 2.5, [
        dt("범인은 바로 이 녀석", TOP1, 84),
        dt("당진 호풍미 호박고구마", TOP2, 84, YEL)], fit="blur"),
    seg(f"{D}/seg/r1_3.mp4", f"{S}/v_pan2.mp4", 2.0, [
        dt("뚜껑 덮고 노릇노릇 굽굽", TOP1, 84)], ss=0.4, fit="blur"),
    seg(f"{D}/seg/r1_4.mp4", f"{S}/v_halves.mp4", 0.76, [
        dt("반 갈라보니...", TOP1, 90, YEL)], fit="blur"),
    seg(f"{D}/seg/r1_5.mp4", f"{S}/v_review.mp4", 3.0, [
        dt("이 색깔 실화??", TOP1, 96, YEL),
        dt("꿀이 줄줄 흐르는 호박고구마", TOP2, 76)], ss=28.0),
    seg(f"{D}/seg/r1_6.mp4", f"{A}/ai1.mp4", 5.0, [
        dt("결국 못 참은 말티즈", TOP1, 88),
        dt("한 입만 주세요 ㅠㅠ", LOW, 92, PINK, a=2.2)], audio=True),
    seg(f"{D}/seg/r1_7.mp4", f"{S}/honey.jpg", 3.2, [
        dt("당진 호풍미 호박고구마", MID - 140, 92, YEL),
        dt("우리 강아지도 반한 그 맛", MID - 10, 74),
        dt("주문은 프로필 링크 클릭!", LOW + 40, 80, PINK, a=0.5),
        dt(TIP, 1560, 40, WHT, border=5)], fit="blur", still=True),
]

# ───────── 릴스 2 : 깐깐한 말티즈 셰프의 고구마 심사 ─────────
r2 = [
    seg(f"{D}/seg/r2_1.mp4", f"{A}/ai2.mp4", 5.0, [
        dt("깐깐한 말티즈 셰프의", TOP1, 88),
        dt("고구마 심사 시작합니다", TOP2, 88, YEL),
        dt("과연 통과할까?!", LOW, 90, PINK, a=3.0)], audio=True),
    seg(f"{D}/seg/r2_2.mp4", f"{S}/raw.jpg", 2.2, [
        dt("후보: 당진 호풍미 호박고구마", TOP1, 76, YEL),
        dt("황토밭에서 갓 캐온 녀석", TOP2, 76)], still=True),
    seg(f"{D}/seg/r2_3.mp4", f"{S}/v_pan1.mp4", 2.5, [
        dt("심사 1단계: 통째로 굽기", TOP1, 84)], ss=4.0, fit="blur"),
    seg(f"{D}/seg/r2_4.mp4", f"{S}/cut.jpg", 2.4, [
        dt("심사 2단계: 반 가르기", TOP1, 84),
        dt("꿀 마블링 무엇...", TOP2, 84, YEL)], still=True),
    seg(f"{D}/seg/r2_5.mp4", f"{S}/honey.jpg", 2.0, [
        dt("이 색깔 실화??", LOW, 96, YEL)], fit="blur", still=True),
    seg(f"{D}/seg/r2_6.mp4", f"{S}/pan.jpg", 1.8, [
        dt("껍질까지 쫀득 달달", TOP1, 86)], fit="blur", still=True),
    seg(f"{D}/seg/r2_7.mp4", f"{A}/ai3.mp4", 5.0, [
        dt("셰프 판정 결과는?!", TOP1, 88),
        dt("합격!! 100점", TOP2 + 10, 120, YEL, a=1.4),
        dt("당진 호풍미 호박고구마", LOW, 80, WHT, a=2.6),
        dt("주문은 프로필 링크 클릭!", LOW + 110, 74, PINK, a=3.0),
        dt(TIP, 1560, 40, WHT, border=5)], audio=True),
]

print(build("reel1_maltese_molka", r1, f"{M}/bouncy_cute.m4a"))
print(build("reel2_maltese_chef", r2, f"{M}/cozy_lofi.m4a"))
