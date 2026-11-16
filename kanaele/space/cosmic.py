"""Long-form 16:9 engine for By The Numbers – Cosmic Scale. Episode 1: How long to travel to the nearest star?
python3 cosmic.py still            -> contact sheet
python3 cosmic.py render           -> CS1_NearestStar.mp4 (+ .srt, chapters, thumbnail)"""
import os, sys, json, math, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "beyondexcuses"))
sys.path.insert(0, os.path.join(HERE, "..", "data"))
import skia
import lib
from lib import P, C, F_CAP, F_SANS, INK, ease, seg, clamp, lerp, lerpc, figure, stand, walk as walk_pose

W, H, FPS = 1920, 1080, 30
GOLD, RED, BLUE, WHITE, MUTED = (255, 200, 80), (255, 120, 110), (140, 200, 255), (245, 246, 250), (175, 182, 210)
GAP, CH, LEAD, OUTRO = 1.1, 1.6, 0.6, 20.0

META = json.load(open(os.path.join(HERE, "ep1_audio", "meta.json")))
# ---------------------------------------------------------------- timeline
TL = []
t = LEAD
for m in META:
    if m["chapter"] and m["i"] > 0: t += CH
    TL.append(dict(m, start=t, end=t + m["dur"]))
    t += m["dur"] + GAP
OUT0 = t + 0.4
T_END = OUT0 + OUTRO
CHAPTERS = [(s["start"] - (CH if s["i"] > 0 else LEAD), s["chapter"]) for s in TL if s["chapter"]]
CHAPTERS[0] = (0.0, CHAPTERS[0][1])

LANES = [("WALKING", "5 km/h", 917_362_537), ("CAR", "100 km/h", 45_868_127), ("JET", "900 km/h", 5_096_459),
         ("VOYAGER 1", "61,000 km/h", 74_948), ("PARKER PROBE", "692,000 km/h", 6_628), ("LIGHT", "1,079 million km/h", 4.24)]
LANE_OF = {"walk": 0, "car": 1, "jet": 2, "voyager": 3, "parker": 4, "light": 5}
MARKERS = [(80, "your life"), (4_500, "pyramids"), (5_000, "written history"), (2_800_000, "genus Homo"),
           (66_000_000, "dinosaurs die out"), (538_000_000, "first complex animals")]


def txt(c, s, x, y, size, col=WHITE, a=1.0, tf=None, align="center", stroke=0, spacing=0):
    if a <= 0 or not s: return 0
    f = skia.Font(tf or F_CAP, size)
    w = f.measureText(s) + spacing * max(0, len(s) - 1)
    if align == "center": x -= w / 2
    elif align == "right": x -= w
    if spacing:
        xx = x
        for ch in s:
            if stroke: c.drawString(ch, xx, y, f, P((0, 0, 0), a * 0.8, stroke=stroke))
            c.drawString(ch, xx, y, f, P(col, a)); xx += f.measureText(ch) + spacing
    else:
        if stroke: c.drawString(s, x, y, f, P((0, 0, 0), a * 0.8, stroke=stroke))
        c.drawString(s, x, y, f, P(col, a))
    return w


def fmt_years(v, final):
    if final < 10: return f"{v:.2f} YEARS"
    if final >= 1e6 and v >= 1e6: return f"{v / 1e6:,.1f} MILLION YEARS"
    return f"{int(v):,} YEARS"


def current(t):
    """active segment (or the one before a gap) and its local progress"""
    cur = TL[0]
    for s in TL:
        if t >= s["start"] - (CH if s["chapter"] and s["i"] > 0 else 0): cur = s
    u = clamp((t - cur["start"]) / max(0.1, cur["end"] - cur["start"]))
    return cur, u


def scene_segments(scene): return [s for s in TL if s["scene"] == scene]


# ---------------------------------------------------------------- backgrounds
RNG = np.random.default_rng(11)
STARS = [(RNG.uniform(0, W), RNG.uniform(0, H), RNG.uniform(0.6, 2.4), RNG.uniform(0.25, 0.9), RNG.uniform(0, 6.28)) for _ in range(420)]


def space(c, t, tint=(26, 30, 80), drift=6.0):
    sh = skia.GradientShader.MakeRadial((W * 0.62, H * 0.42), 1300, [C(tint), C((8, 9, 22))])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    for x, y, r, a, ph in STARS:
        xx = (x - t * drift * r * 0.4) % W
        c.drawCircle(xx, y, r, P((255, 255, 255), a * (0.75 + 0.25 * math.sin(t * 1.3 + ph))))


# ---------------------------------------------------------------- icons
def icon(c, kind, x, y, s=1.0, col=WHITE, t=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    if kind == 0:
        figure(c, 0, 26, walk_pose(t * 8), s=0.32, facing=1, body=col, rim=(GOLD, 0.4))
    elif kind == 1:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-34, -14, 68, 22), 8, 8), P(RED))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-18, -28, 34, 16), 6, 6), P(RED))
        c.drawRect(skia.Rect.MakeXYWH(-12, -25, 26, 10), P((190, 220, 255)))
        for wx in (-20, 20): c.drawCircle(wx, 9, 9, P((30, 30, 40))); c.drawCircle(wx, 9, 4, P(MUTED))
    elif kind == 2:
        c.drawPath(lib.poly([(-40, 0), (30, -6), (44, 0), (30, 6)]), P(WHITE))
        c.drawPath(lib.poly([(-2, -2), (-16, -26), (-6, -26), (14, -2)]), P(MUTED))
        c.drawPath(lib.poly([(-2, 2), (-16, 26), (-6, 26), (14, 2)]), P(MUTED))
        c.drawPath(lib.poly([(-40, 0), (-46, -14), (-36, -14), (-30, -2)]), P(MUTED))
    elif kind == 3:
        c.drawLine(-36, 0, 30, 0, P(MUTED, stroke=3)); c.drawLine(0, -26, 0, 26, P(MUTED, stroke=2))
        c.drawRect(skia.Rect.MakeXYWH(-10, -8, 20, 16), P((200, 170, 90)))
        pth = skia.Path(); pth.addOval(skia.Rect.MakeXYWH(-6, -24, 34, 48)); c.drawPath(pth, P(WHITE))
        c.drawPath(pth, P(INK, stroke=2))
    elif kind == 4:
        c.drawPath(lib.poly([(10 * math.cos(a), 10 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]]), P(MUTED))
        c.drawRect(skia.Rect.MakeXYWH(-30, -26, 12, 52), P((240, 240, 235)))
        c.drawRect(skia.Rect.MakeXYWH(-30, -26, 12, 52), P(INK, stroke=2))
        c.drawLine(10, 0, 36, 0, P(MUTED, stroke=3))
    elif kind == 5:
        c.drawCircle(0, 0, 18, P(BLUE, 0.35, blur=12)); c.drawCircle(0, 0, 8, P((235, 245, 255)))
    c.restore()


def earth(c, x, y, r=22):
    c.drawCircle(x, y, r + 6, P(BLUE, 0.25, blur=10)); c.drawCircle(x, y, r, P((70, 140, 230)))
    c.drawCircle(x - r * 0.3, y - r * 0.2, r * 0.45, P((90, 180, 110), 0.9))


def proxima(c, x, y, r=16, t=0.0, label=True, a=1.0):
    c.drawCircle(x, y, r * 3.2, P((255, 90, 70), 0.18 * a, blur=r * 2))
    c.drawCircle(x, y, r, P((255, 110, 80), a))
    if label: txt(c, "PROXIMA CENTAURI", x, y + r + 40, 24, (255, 170, 150), a, tf=F_SANS, spacing=2)


# ---------------------------------------------------------------- shared race board
LX0, LX1, LY0, LDY = 330, 1640, 210, 86


def race(c, t, active, s_scene, u_scene, show_light=False):
    n = 6 if show_light else 5
    for i in range(n):
        y = LY0 + i * LDY
        on = i == active
        a = 1.0 if on else 0.45
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(LX0 - 10, y - 30, LX1 + 10, y + 30), 30, 30),
                    P(GOLD if on else (255, 255, 255), 0.10 if on else 0.04))
        if on: c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(LX0 - 10, y - 30, LX1 + 10, y + 30), 30, 30), P(GOLD, 0.7, stroke=3))
        name, speed, yrs = LANES[i]
        txt(c, name, LX0 - 40, y - 2, 30, GOLD if on else WHITE, a, align="right")
        txt(c, speed, LX0 - 40, y + 26, 22, MUTED, a, tf=F_SANS, align="right")
        frac = min(1.0, 80.0 / yrs)
        p = frac * (ease(u_scene) if on else 1.0)
        x = LX0 + 40 + (LX1 - LX0 - 120) * p
        c.drawLine(LX0 + 40, y, LX1 - 80, y, P((255, 255, 255), 0.12 * a, stroke=4))
        icon(c, i, x, y, 1.0, WHITE, t)
        proxima(c, LX1 - 30, y, 9, t, label=False, a=a)
        if on and i < 5:
            pct = 100 * frac
            s = f"{pct:.7f}".rstrip("0") if pct < 0.001 else (f"{pct:.4f}".rstrip("0") if pct < 0.1 else f"{pct:.1f}")
            txt(c, f"in 80 years: {s} % of the way", x + 30, y - 38 if i else y - 40, 22, MUTED, seg(u_scene, 0.1, 0.3), tf=F_SANS, align="left")
    earth(c, LX0 + 10, LY0 - 70, 18); txt(c, "EARTH", LX0 + 46, LY0 - 62, 22, MUTED, tf=F_SANS, align="left")


def timeline(c, t, value, prog, a=1.0):
    """log time axis 1 … 1e9 years with history markers; value drops in with prog"""
    y = 900; x0, x1 = 180, 1740
    def X(v): return x0 + (x1 - x0) * math.log10(max(1, v)) / 9
    c.drawLine(x0, y, x1, y, P((255, 255, 255), 0.35 * a, stroke=4))
    for k in range(10):
        c.drawLine(X(10 ** k), y - 8, X(10 ** k), y + 8, P((255, 255, 255), 0.35 * a, stroke=2))
        lbl = ["1", "10", "100", "1k", "10k", "100k", "1M", "10M", "100M", "1B"][k]
        txt(c, lbl, X(10 ** k), y + 34, 18, MUTED, a * 0.8, tf=F_SANS)
    for i, (v, name) in enumerate(MARKERS):
        xx = X(v); up = i % 2 == 0
        c.drawCircle(xx, y, 6, P(BLUE, a)); txt(c, name, xx, y - 26 if up else y + 62, 20, BLUE, a * 0.9, tf=F_SANS)
    if value is not None and prog > 0:
        xx = X(1 + (value - 1) * ease(prog))
        c.drawCircle(xx, y, 12, P(GOLD, a)); c.drawCircle(xx, y, 22, P(GOLD, 0.25 * a, blur=8))


def counter(c, value, final, prog, x=960, y=830, size=72, col=GOLD, a=1.0, land=None, t=0):
    v = final * (1 - (1 - clamp(prog)) ** 3)
    pz = 1.0
    if land is not None and t >= land: pz = 1 + 0.25 * math.exp(-(t - land) * 7) * math.cos((t - land) * 18)
    c.save(); c.translate(x, y); c.scale(pz, pz)
    txt(c, fmt_years(v, final), 0, 0, size, col, a, stroke=10)
    c.restore()


# ---------------------------------------------------------------- scenes
def sc_hook(c, t, s, u):
    space(c, t)
    k = seg(t, s["start"], s["end"] - 1.6)
    # Voyager drifting, light-time counter towards 1 light-day
    icon(c, 3, lerp(1500, 1380, k), 470, 3.0, WHITE, t)
    secs = 86400 - 3 * (1 - k)
    hh, mm, ss = int(secs // 3600), int(secs % 3600 // 60), int(secs % 60)
    txt(c, "VOYAGER 1 · DISTANCE IN LIGHT-TIME", 1450, 640, 24, MUTED, 1.0, tf=F_SANS, spacing=3)
    lab = "1 LIGHT-DAY" if k > 0.98 else f"{hh:02d}:{mm:02d}:{ss:02d}"
    txt(c, lab, 1450, 720, 66, GOLD, 1.0, stroke=10)
    earth(c, 220, 470, 26)
    c.drawLine(260, 470, lerp(1500, 1380, k) - 60, 470, P(BLUE, 0.35, stroke=3))
    q = seg(t, s["end"] - 1.6, s["end"] - 0.6)
    if q > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((6, 6, 16), 0.85 * q))
        proxima(c, 960, 520, 22, t, a=q)
        txt(c, "1,549 LIGHT-DAYS AWAY", 960, 690, 48, (255, 170, 150), q, stroke=8)
    txt(c, "How long would YOU need", 120, 170, 64, WHITE, seg(t, 0.4, 0.9), align="left", stroke=10)
    txt(c, "to reach the nearest star?", 120, 250, 64, GOLD, seg(t, 0.8, 1.3), align="left", stroke=10)


def sc_lanes(c, t, s, u):
    space(c, t)
    for i in range(6):
        a = seg(u, i * 0.13, i * 0.13 + 0.1)
        if a <= 0: continue
        c.saveLayerAlpha(None, int(255 * a)); race(c, t, -1, s, 0.0, show_light=True); c.restore()
        break
    n_on = sum(1 for i in range(6) if u > i * 0.13)
    c.drawRect(skia.Rect.MakeLTRB(0, LY0 - 40 + n_on * LDY, W, LY0 + 6 * LDY), P((8, 9, 22), 0.92))


def sc_ladder(c, t, s, u):
    space(c, t, tint=(30, 26, 86))
    idx = [x["i"] for x in scene_segments("ladder")].index(s["i"])
    if idx == 0:
        txt(c, "PROXIMA CENTAURI", 960, 330, 40, (255, 170, 150), seg(u, 0.0, 0.1), tf=F_SANS, spacing=4)
        txt(c, "4.24 LIGHT-YEARS", 960, 450, 110, WHITE, seg(u, 0.15, 0.3), stroke=12)
        k = seg(u, 0.55, 0.95)
        txt(c, f"{int(40_208_000_000_000 * (1 - (1 - k) ** 3)):,} km", 960, 600, 84, GOLD, seg(u, 0.5, 0.6), stroke=10)
        proxima(c, 960, 800, 18, t, label=False, a=seg(u, 0.1, 0.3))
    elif idx == 1:
        rungs = [("MOON", "1.3 light-seconds", 0.05), ("SUN", "8 min 20 s", 0.28), ("VOYAGER 1", "1 light-day · 49 years of travel", 0.55)]
        for j, (a_, b_, at) in enumerate(rungs):
            al = seg(u, at, at + 0.08); y = 300 + j * 190
            c.drawCircle(300, y, 26 if j else 18, P([(200, 200, 210), (255, 205, 110), MUTED][j], al))
            txt(c, a_, 380, y + 10, 56, WHITE, al, align="left", stroke=8)
            txt(c, b_, 1600, y + 10, 46, GOLD, al, align="right", stroke=8)
    elif idx == 2:
        # 1,549 light-days as a grid; one cell lit
        cols, size = 62, 22; n = 1549
        shown = int(n * seg(u, 0.05, 0.75))
        x0 = (W - cols * size) / 2; y0 = 230
        for k in range(shown):
            r, q = divmod(k, cols)
            c.drawRect(skia.Rect.MakeXYWH(x0 + q * size + 2, y0 + r * size + 2, size - 4, size - 4), P(GOLD if k == 0 else (255, 120, 100), 0.95 if k == 0 else 0.55))
        txt(c, "1 LIGHT-DAY = VOYAGER, AFTER 49 YEARS", x0, 200, 28, GOLD, seg(u, 0.05, 0.15), tf=F_SANS, align="left", spacing=2)
        txt(c, f"{shown:,} / 1,549 LIGHT-DAYS TO PROXIMA", 960, 860, 52, WHITE, 1.0, stroke=8)
    else:
        earth(c, 300, 540, 30); icon(c, 3, 1600, 540, 2.0, WHITE, t)
        p = (t * 0.6) % 1.0
        c.drawCircle(lerp(340, 1560, p), 540, 8, P(BLUE)); c.drawCircle(lerp(340, 1560, p), 540, 20, P(BLUE, 0.3, blur=8))
        txt(c, "1 LIGHT-YEAR = 9.46 TRILLION km", 960, 280, 58, WHITE, seg(u, 0.0, 0.1), stroke=8)
        txt(c, "1 LIGHT-DAY = 26 BILLION km", 960, 370, 58, GOLD, seg(u, 0.2, 0.3), stroke=8)
        txt(c, "COMMAND: 1 DAY  ·  ANSWER: 1 DAY", 960, 760, 46, BLUE, seg(u, 0.55, 0.65), stroke=8)


def sc_model(c, t, s, u):
    space(c, t, tint=(24, 40, 70))
    if u < 0.55:
        k = seg(u, 0.0, 0.12)
        c.drawRect(skia.Rect.MakeLTRB(0, 700, W, H), P((40, 90, 60), k))
        c.drawCircle(420, 600, 100, P((255, 200, 90), k)); txt(c, "SUN = 1 m", 420, 760, 40, WHITE, k, stroke=6)
        k2 = seg(u, 0.15, 0.3)
        c.drawCircle(1500, 690, 5, P((90, 160, 255), k2)); txt(c, "EARTH = 9 mm", 1500, 760, 40, WHITE, k2, stroke=6)
        c.drawLine(520, 820, 1500, 820, P(WHITE, k2, stroke=4)); txt(c, "107 m", 1010, 870, 44, GOLD, k2, stroke=6)
    else:
        k = seg(u, 0.55, 0.7)
        R = 300; cx, cy = 960, 560
        c.drawCircle(cx, cy, R, P((50, 110, 200), k)); c.drawCircle(cx, cy, R, P((255, 255, 255), 0.3 * k, stroke=3))
        arc = skia.Path(); arc.addArc(skia.Rect.MakeXYWH(cx - R - 30, cy - R - 30, 2 * R + 60, 2 * R + 60), -90, 360 * 0.72 * seg(u, 0.65, 0.92))
        c.drawPath(arc, P(GOLD, k, stroke=10))
        txt(c, "≈ 28,900 km", cx, cy + 16, 80, WHITE, seg(u, 0.75, 0.85), stroke=10)
        txt(c, "NEAREST STAR ON THE SAME SCALE", cx, 160, 40, GOLD, seg(u, 0.6, 0.7), tf=F_SANS, spacing=3)


def sc_race(c, t, s, u):
    space(c, t)
    lane = LANE_OF[s["scene"]]
    segs = scene_segments(s["scene"]); idx = [x["i"] for x in segs].index(s["i"])
    uu = (idx + u) / len(segs)
    race(c, t, lane, s, uu, show_light=(lane == 5))
    name, speed, yrs = LANES[lane]
    if lane < 5:
        land_seg = segs[1] if len(segs) > 1 else segs[0]
        prog = clamp((t - land_seg["start"]) / max(0.5, land_seg["end"] - land_seg["start"] - 1.0))
        if idx >= 1 or len(segs) == 1:
            counter(c, None, yrs, prog, y=780, land=land_seg["start"] + max(0.5, land_seg["end"] - land_seg["start"] - 1.0), t=t)
            timeline(c, t, yrs, prog)
        else:
            extra = {0: "MOON: ~9 YEARS ON FOOT", 1: "MOON: 160 DAYS BY CAR", 2: "68× FASTER THAN THE JET" if False else "",
                     3: "", 4: ""}.get(lane, "")
            if lane == 3: extra = "68× FASTER THAN THE JET"
            if lane == 2: extra = "5.1 MILLION YEARS"
            txt(c, extra, 960, 800, 58, GOLD, seg(u, 0.4, 0.5), stroke=8)
        if lane == 3 and idx == 2:
            g = int(3000 * ease(seg(u, 0.1, 0.6)))
            c.drawRect(skia.Rect.MakeLTRB(0, 700, W, H), P((8, 9, 22), 0.92))
            txt(c, f"{g:,} GENERATIONS ON BOARD", 960, 860, 70, GOLD, seg(u, 0.05, 0.15), stroke=10)
        if lane == 4 and idx == 2:
            c.drawRect(skia.Rect.MakeLTRB(0, 700, W, H), P((8, 9, 22), 0.92))
            txt(c, "MOON ≈ 30 MIN  ·  MARS (CLOSEST) ≈ 3 DAYS", 960, 860, 54, GOLD, seg(u, 0.05, 0.15), stroke=8)
        if lane == 4 and idx == 1:
            txt(c, "BRIEF PEAK NEAR THE SUN – NOT A CRUISING SPEED", 960, 700, 30, RED, seg(u, 0.7, 0.8), tf=F_SANS, spacing=2)
    else:
        k = seg(u, 0.0, 0.25) if idx == 0 else 1.0
        y = LY0 + 5 * LDY
        c.drawLine(LX0 + 40, y, lerp(LX0 + 40, LX1 - 40, k), y, P(BLUE, stroke=8))
        c.drawLine(LX0 + 40, y, lerp(LX0 + 40, LX1 - 40, k), y, P(BLUE, 0.4, stroke=26, blur=10))
        if idx == 0:
            counter(c, None, 4.24, seg(u, 0.1, 0.4), y=800, col=BLUE, land=s["start"] + 0.4 * (s["end"] - s["start"]), t=t)
        else:
            c.drawRect(skia.Rect.MakeLTRB(0, 720, W, H), P((8, 9, 22), 0.92))
            txt(c, "\"HELLO\": 4.24 YEARS THERE + 4.24 BACK = 8.5 YEARS", 960, 860, 54, BLUE, seg(u, 0.1, 0.2), stroke=8)


def sc_energy(c, t, s, u):
    space(c, t, tint=(60, 24, 50))
    x0, y0, x1, y1 = 300, 880, 1620, 220
    c.drawLine(x0, y0, x1, y0, P(WHITE, 0.6, stroke=3)); c.drawLine(x0, y0, x0, y1, P(WHITE, 0.6, stroke=3))
    txt(c, "SPEED", x1, y0 + 50, 30, MUTED, tf=F_SANS, align="right", spacing=3)
    txt(c, "ENERGY NEEDED", x0 - 20, y1 - 20, 30, MUTED, tf=F_SANS, align="left", spacing=3)
    k = seg(u, 0.05, 0.6)
    pth = skia.Path(); pth.moveTo(x0, y0)
    for i in range(1, 101):
        v = i / 100 * k
        pth.lineTo(x0 + (x1 - x0) * v, y0 - (y0 - y1) * v * v)
    c.drawPath(pth, P(RED, stroke=8))
    txt(c, "2× FASTER = 4× THE ENERGY", 960, 330, 52, WHITE, seg(u, 0.25, 0.35), stroke=8)
    txt(c, "10× FASTER = 100× THE ENERGY", 960, 420, 52, GOLD, seg(u, 0.45, 0.55), stroke=8)
    txt(c, "1,000× FASTER = 1,000,000× THE ENERGY", 960, 510, 52, RED, seg(u, 0.7, 0.8), stroke=8)


def sc_proximab(c, t, s, u):
    space(c, t, tint=(70, 26, 30))
    cx, cy = 760, 540
    fl = 0.5 + 0.5 * math.sin(t * 3.0) ** 8
    c.drawCircle(cx, cy, 220 + 30 * fl, P((255, 90, 60), 0.25, blur=60)); c.drawCircle(cx, cy, 120, P((255, 110, 80)))
    c.drawCircle(cx, cy, 300, P((255, 255, 255), 0.18, stroke=2))
    ang = t * 2 * math.pi / 11.2 * 3
    px, py = cx + 300 * math.cos(ang), cy + 300 * math.sin(ang) * 0.35
    c.drawCircle(px, py, 18, P((140, 160, 200)))
    txt(c, "PROXIMA b", 1500, 380, 64, WHITE, seg(u, 0.05, 0.15), stroke=8)
    idx = [x["i"] for x in scene_segments("proximab")].index(s["i"])
    if idx == 0:
        txt(c, "FOUND 2016", 1500, 470, 40, GOLD, seg(u, 0.15, 0.25), tf=F_SANS, spacing=2)
        txt(c, "≥ ~1 EARTH MASS", 1500, 540, 40, GOLD, seg(u, 0.4, 0.5), tf=F_SANS, spacing=2)
        txt(c, "1 ORBIT = 11.2 DAYS", 1500, 610, 40, GOLD, seg(u, 0.55, 0.65), tf=F_SANS, spacing=2)
        txt(c, "IN THE HABITABLE ZONE", 1500, 680, 40, BLUE, seg(u, 0.75, 0.85), tf=F_SANS, spacing=2)
    else:
        txt(c, "RED DWARF · FLARE STAR", 1500, 470, 40, RED, seg(u, 0.05, 0.15), tf=F_SANS, spacing=2)
        txt(c, "LIFE?  UNKNOWN", 1500, 600, 56, WHITE, seg(u, 0.7, 0.8), stroke=8)


def sc_scoreboard(c, t, s, u):
    space(c, t, tint=(30, 30, 70))
    idx = [x["i"] for x in scene_segments("scoreboard")].index(s["i"])
    x0, x1 = 520, 1380
    def X(v): return x0 + (x1 - x0) * math.log10(max(1, v)) / 9
    for i, (name, speed, yrs) in enumerate(LANES):
        y = 210 + i * 105
        k = seg(u, 0.08 + i * 0.14, 0.18 + i * 0.14) if idx == 0 else 1.0
        txt(c, name, x0 - 30, y + 14, 34, WHITE, k, align="right")
        col = BLUE if i == 5 else (GOLD if yrs < 10000 else RED)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y - 22, lerp(x0, X(yrs), k), y + 22), 10, 10), P(col, 0.9))
        txt(c, fmt_years(yrs, yrs), lerp(x0, X(yrs), k) + 20, y + 14, 30, col, k, align="left")
    if idx >= 1:
        k = seg(u, 0.0, 0.2) if idx == 1 else 1.0
        xl = X(80)
        c.drawLine(xl, 160, xl, 820, P(GOLD, k, stroke=6))
        txt(c, "YOUR LIFE ≈ 80 YEARS", xl, 140, 34, GOLD, k, stroke=6)


def sc_starshot(c, t, s, u):
    sc_scoreboard(c, t, dict(s, i=scene_segments("scoreboard")[-1]["i"]), 1.0)
    k = seg(u, 0.05, 0.25)
    y = 210 + 6 * 105 - 40
    x0, x1 = 520, 1380
    xe = x0 + (x1 - x0) * math.log10(20) / 9
    pth = skia.Path(); pth.moveTo(x0, y); pth.lineTo(lerp(x0, xe, k), y)
    p = P(GOLD, 0.9, stroke=6); p.setPathEffect(skia.DashPathEffect.Make([18, 12], 0)); c.drawPath(pth, p)
    txt(c, "STARSHOT", x0 - 30, y + 12, 34, GOLD, k, align="right")
    txt(c, "~20 YEARS · PROPOSAL, NOT BUILT", xe + 20, y + 12, 30, GOLD, seg(u, 0.4, 0.5), align="left")


def sc_close(c, t, s, u):
    space(c, t, tint=(26, 30, 80))
    txt(c, "NEXT WEEK", 960, 360, 40, MUTED, seg(u, 0.0, 0.1), tf=F_SANS, spacing=6)
    txt(c, "How far has Voyager 1 really gone?", 960, 470, 72, WHITE, seg(u, 0.05, 0.2), stroke=10)
    txt(c, "Which of the five would you have bet on?", 960, 680, 50, GOLD, seg(u, 0.5, 0.65), stroke=8)


def sc_outro(c, t):
    space(c, t, tint=(20, 24, 60))
    txt(c, "BY THE NUMBERS · COSMIC SCALE", 960, 150, 34, GOLD, 1.0, tf=F_SANS, spacing=6)
    for x in (560, 1360):   # end-screen video slots (YouTube places the elements here)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 330, 330, 660, 372), 24, 24), P((255, 255, 255), 0.06))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 330, 330, 660, 372), 24, 24), P((255, 255, 255), 0.2, stroke=3))
    txt(c, "WATCH NEXT", 960, 800, 44, WHITE, 1.0, stroke=6)


SCENES = dict(hook=sc_hook, lanes=sc_lanes, ladder=sc_ladder, model=sc_model, walk=sc_race, car=sc_race, jet=sc_race,
              voyager=sc_race, parker=sc_race, light=sc_race, energy=sc_energy, proximab=sc_proximab,
              scoreboard=sc_scoreboard, starshot=sc_starshot, close=sc_close)


def chapter_card(c, t):
    for s in TL:
        if s["chapter"] and s["i"] > 0 and s["start"] - CH <= t < s["start"] + 0.2:
            k = seg(t, s["start"] - CH, s["start"] - CH + 0.35) * (1 - seg(t, s["start"] - 0.1, s["start"] + 0.2))
            n = [x for x in TL if x["chapter"]].index(s) + 1
            c.drawRect(skia.Rect.MakeWH(W, H), P((6, 7, 18), 0.88 * k))
            txt(c, f"{n:02d}", 960, 470, 60, GOLD, k, tf=F_SANS, spacing=6)
            txt(c, s["chapter"].upper(), 960, 590, 92, WHITE, k, stroke=10)


def chapter_label(c, t):
    cur = [s for s in TL if s["chapter"] and s["start"] - 0.1 <= t]
    if not cur or t >= OUT0: return
    s = cur[-1]; n = [x for x in TL if x["chapter"]].index(s) + 1
    txt(c, f"{n:02d} · {s['chapter'].upper()}", 60, 70, 24, MUTED, 0.85, tf=F_SANS, align="left", spacing=3)
    c.drawRect(skia.Rect.MakeXYWH(0, H - 6, W * t / T_END, 6), P(GOLD, 0.7))


def frame(c, t):
    lib.NOW = t
    if t >= OUT0:
        sc_outro(c, t); return
    s, u = current(t)
    SCENES[s["scene"]](c, t, s, u)
    chapter_card(c, t)
    chapter_label(c, t)
    if t < 0.12: c.drawRect(skia.Rect.MakeWH(W, H), P((255, 255, 255), 0.4 * (1 - t / 0.12)))


# ---------------------------------------------------------------- audio, subtitles, chapters
def build_audio(out):
    import soundfile as sf
    sys.path.insert(0, os.path.join(HERE, "..", "data")); import music
    SR = 44100
    n = int(T_END * SR) + SR
    voice = np.zeros(n, np.float32)
    for s in TL:
        x, sr = sf.read(os.path.join(HERE, "ep1_audio", f"seg{s['i']:02d}.wav"), dtype="float32")
        if sr != SR:
            from scipy.signal import resample_poly
            x = resample_poly(x, SR, sr).astype(np.float32)
        i = int(s["start"] * SR); voice[i:i + len(x)] += x[: n - i]
    light = scene_segments("light")[0]["start"]
    bed = music.render("cinematic", 96, T_END, dict(build=light - 6.0, drop=light, outro=OUT0), seed=21)
    bed = np.pad(bed, ((0, n - len(bed)), (0, 0)))
    env = np.abs(voice); k = int(0.25 * SR)
    sm = np.convolve(env, np.ones(k) / k, mode="same")
    duck = 1 - 0.75 * np.clip(sm / (sm.max() * 0.15 + 1e-9), 0, 1)
    mix = bed * (0.16 * duck)[:, None] + voice[:, None] * 0.9
    # chapter whooshes from the CC0 kit
    meta = {m["id"]: m for m in json.load(open(os.path.join(HERE, "..", "data", "assets", "sfx", "sounds.json")))["sounds"]}
    def add(sid, at, g):
        x, sr = sf.read(os.path.join(HERE, "..", "data", "assets", "sfx", meta[sid]["file"]), dtype="float32")
        if x.ndim == 1: x = np.stack([x, x], 1)
        if sr != SR:
            from scipy.signal import resample_poly
            x = resample_poly(x, SR, sr, axis=0).astype(np.float32)
        i = int((at - meta[sid]["sync"]["at"]) * SR); i = max(0, i)
        mix[i:i + len(x)] += x[: n - i] * 10 ** (g / 20)
    add("boom-hit-medium", 0.02, -6)
    for s in TL:
        if s["chapter"] and s["i"] > 0: add("whoosh-slow-medium", s["start"] - CH + 0.2, -14)
    add("cinematic-drum-big", light + 0.05, -10)
    mix = np.tanh(mix * 1.0)
    sf.write(out + ".raw.wav", mix[: int(T_END * SR)], SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out + ".raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", out], check=True)
    os.remove(out + ".raw.wav")


def write_chapters(path):
    def ts(x): x = int(x); return f"{x // 60}:{x % 60:02d}"
    lines = [f"{ts(t0)} {name}" for t0, name in CHAPTERS]
    open(path, "w").write("\n".join(lines) + "\n")
    return lines


def write_srt(path):
    """subtitles from the known script text, timed per segment and split into ~7-word cues by word share"""
    def ts(x):
        ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s_, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s_:02d},{ms:03d}"
    out = []; n = 1
    for s in TL:
        words = s["text"].split(); chunks = [words[i:i + 7] for i in range(0, len(words), 7)]
        tot = sum(len(" ".join(ch)) for ch in chunks); t = s["start"]
        for ch in chunks:
            d = (s["end"] - s["start"]) * len(" ".join(ch)) / tot
            out.append(f"{n}\n{ts(t)} --> {ts(t + d)}\n{' '.join(ch)}\n"); n += 1; t += d
    open(path, "w").write("\n".join(out))


def render(out):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    tmp = out[:-4] + "_v.part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(int(T_END * FPS)):
        c.clear(skia.ColorBLACK); frame(c, f / FPS)
        ff.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    ff.stdin.close(); ff.wait()
    audio = out[:-4] + "_a.wav"
    build_audio(audio)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", out], check=True)
    os.remove(tmp)


def stills(ts, out):
    from PIL import Image
    tiles = []
    for t in ts:
        surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.ColorBLACK); frame(c, t)
        tiles.append(Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]).resize((480, 270)))
    cols = 4; rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (480 * cols, 270 * rows))
    for i, im in enumerate(tiles): sheet.paste(im, ((i % cols) * 480, (i // cols) * 270))
    sheet.save(out, quality=88)


if __name__ == "__main__":
    print(f"duration {T_END:.1f} s = {T_END / 60:.2f} min", file=sys.stderr)
    if sys.argv[1] == "still":
        mids = [(s["start"] + s["end"]) / 2 for s in TL] + [OUT0 + 5]
        stills(mids, os.path.join(HERE, "check_cs1.jpg"))
    else:
        out = os.path.join(HERE, "CS1_NearestStar.mp4")
        render(out)
        print("\n".join(write_chapters(os.path.join(HERE, "CS1_chapters.txt"))), file=sys.stderr)
        write_srt(os.path.join(HERE, "CS1_NearestStar.en.srt"))
