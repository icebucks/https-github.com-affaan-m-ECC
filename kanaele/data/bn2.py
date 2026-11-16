"""By The Numbers #2: The world's tallest buildings – to scale.
Camera starts at a 1.75 m person and zooms out object by object: Statue of Liberty (93 m incl. pedestal),
Eiffel Tower (330 m), then the 10 tallest buildings (heights as listed on Wikipedia/CTBUH, Nov 2026) up to Burj Khalifa (828 m).
828 / 330 = 2.5 -> "2.5x the Eiffel Tower"."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "beyondexcuses"))
sys.path.insert(0, HERE)
os.environ.setdefault("OUT_DIR", HERE)
from lib import *
from dlib import flag, sfx

T_END = 17.6
GY = 1370                      # ground line on screen
GOLD = (255, 200, 80)

# kind, name, country, height (m), x (m), body width (m), top width (m), spire (m)
OBJ = [
    ("person", "You", None, 1.75, 0, 0.6, 0, 0),
    ("liberty", "Statue of Liberty", "us", 93, 32, 22, 0, 0),
    ("eiffel", "Eiffel Tower", "fr", 330, 160, 125, 0, 0),
    ("tower", "CITIC Tower", "cn", 528, 330, 70, 62, 0),
    ("tower", "Tianjin CTF Finance Centre", "cn", 530, 440, 68, 34, 8),
    ("tower", "Guangzhou CTF Finance Centre", "cn", 530, 550, 66, 40, 6),
    ("tower", "One World Trade Center", "us", 541, 660, 62, 34, 124),
    ("tower", "Lotte World Tower", "kr", 555, 770, 72, 10, 0),
    ("tower", "Ping An Finance Center", "cn", 599, 880, 70, 40, 40),
    ("clock", "Makkah Royal Clock Tower", "sa", 601, 990, 90, 34, 150),
    ("tower", "Shanghai Tower", "cn", 632, 1100, 76, 36, 0),
    ("tower", "Merdeka 118", "my", 679, 1215, 70, 20, 160),
    ("burj", "Burj Khalifa", "ae", 828, 1345, 90, 6, 220),
]
# stop schedule: (start time of the move, index); first 3 slower (hook), last one big
STOPS = []
t = 0.3
for i in range(len(OBJ)):
    STOPS.append((t, i))
    t += 1.4 if i < 3 else 0.8
REVEAL = STOPS[-1][0]          # Burj Khalifa move starts (riser before it)
OVER = REVEAL + 1.4            # zoom out to the whole skyline
END = OVER + 1.9               # end text
MOVE = 0.55                    # length of each camera move


def rank_of(i):
    return {3: 10, 4: 8, 5: 8, 6: 7, 7: 6, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}.get(i)


def cam_target(i):
    k, name, cc, h, x, w, wt, sp = OBJ[i]
    return x, 760 / max(h, 1.75)          # object fills ~760 px


def cam(t):
    """camera centre (m) and scale (px/m); scale moves in log space"""
    cur = 0
    for ts, i in STOPS:
        if t >= ts: cur = i
    ts = [s for s, i in STOPS if i == cur][0]
    x1, s1 = cam_target(cur)
    if cur == 0: return x1, s1
    x0, s0 = cam_target(cur - 1)
    u = ease((t - ts) / MOVE)
    x, s = lerp(x0, x1, u), math.exp(lerp(math.log(s0), math.log(s1), u))
    if t > OVER:                              # final zoom-out: whole skyline
        v = ease((t - OVER) / 1.2)
        x = lerp(x, 690, v); s = math.exp(lerp(math.log(s), math.log(0.62), v))
    return x, s


def sx(xm, xc, sc): return 540 + (xm - xc) * sc
def sy(hm, sc): return GY - hm * sc


# ------------------------------------------------------------------ drawing
def background(c, t, xc):
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, GY)], [C((10, 12, 30)), C((30, 32, 70)), C((90, 70, 110))], [0, 0.6, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    rng = np.random.default_rng(4)
    for _ in range(140):
        x, y, r = rng.uniform(0, W), rng.uniform(0, GY - 300), rng.uniform(1, 2.6)
        c.drawCircle(x, y, r, P((255, 255, 255), 0.25 + 0.4 * abs(math.sin(t * 0.7 + x))))
    # distant skyline with slight parallax
    rng = np.random.default_rng(8)
    off = -(xc * 0.08) % 2000
    x = -300 + off - 2000
    while x < W + 300:
        w = rng.uniform(40, 110); h = rng.uniform(40, 220)
        c.drawRect(skia.Rect.MakeXYWH(x, GY - h, w, h), P((40, 40, 72), 0.9))
        x += w + rng.uniform(2, 14)
    c.drawRect(skia.Rect.MakeLTRB(0, GY, W, H), P((14, 14, 26)))
    c.drawLine(0, GY, W, GY, P((120, 120, 170), 0.6, stroke=3))


def windows(c, left, top, right, bottom, sc, seed, a=1.0):
    if sc < 0.25: return
    rng = np.random.default_rng(seed)
    step = max(6.0, 12 * sc)
    y = top + step
    while y < bottom - step * 0.5:
        x = left + step * 0.6
        while x < right - step * 0.6:
            if rng.random() < 0.55:
                c.drawRect(skia.Rect.MakeXYWH(x, y, max(1.5, step * 0.35), max(1.5, step * 0.45)), P((255, 220, 150), 0.45 * a))
            x += step
        y += step


def draw_tower(c, o, xc, sc, hi, idx):
    k, name, cc, h, x, w, wt, sp = o
    body = h - sp
    bx, top, base = sx(x, xc, sc), sy(body, sc), GY
    hw, ht = w * sc / 2, wt * sc / 2
    col = (70, 90, 130) if not hi else (95, 120, 170)
    if k == "burj":   # stepped setbacks
        path = skia.Path(); steps = 6
        path.moveTo(bx - hw, base)
        for j in range(steps):
            y0 = base - (base - top) * j / steps; y1 = base - (base - top) * (j + 1) / steps
            ww = lerp(hw, ht + 3, (j + 1) / steps)
            path.lineTo(bx - lerp(hw, ht + 3, j / steps), y1 + (y0 - y1) * 0.15); path.lineTo(bx - ww, y1)
        path.lineTo(bx + ht + 3, top)
        for j in range(steps - 1, -1, -1):
            y1 = base - (base - top) * (j + 1) / steps; y0 = base - (base - top) * j / steps
            path.lineTo(bx + lerp(hw, ht + 3, (j + 1) / steps), y1); path.lineTo(bx + lerp(hw, ht + 3, j / steps), y1 + (y0 - y1) * 0.15)
        path.lineTo(bx + hw, base); path.close()
    elif k == "clock":
        path = skia.Path()
        bw = 130 * sc / 2
        path.addRect(skia.Rect.MakeLTRB(bx - bw * 1.6, sy(250, sc), bx + bw * 1.6, base))
        path.addRect(skia.Rect.MakeLTRB(bx - hw, top, bx + hw, base))
    else:
        path = poly([(bx - hw, base), (bx - ht, top), (bx + ht, top), (bx + hw, base)])
    c.drawPath(path, P(col)); c.drawPath(path, P((14, 16, 30), stroke=max(1.5, 2.5)))
    if hi: c.drawPath(path, P(GOLD, 0.8, stroke=3))
    windows(c, bx - hw * 0.8, top, bx + hw * 0.8, base, sc, idx, 0.9)
    if k == "clock":
        r = 23 * sc
        c.drawCircle(bx, top + body * 0.08 * sc + r, r, P((240, 240, 230))); c.drawCircle(bx, top + body * 0.08 * sc + r, r, P(INK, stroke=2))
    if sp > 0:
        c.drawLine(bx, top, bx, sy(h, sc), P((200, 205, 220), stroke=max(1.5, 3.5 * sc)))


def draw_eiffel(c, o, xc, sc, hi):
    k, name, cc, h, x, w, wt, sp = o
    bx = sx(x, xc, sc)
    pts = [(-62.5, 0), (-40, 57), (-26, 57), (-18, 115), (-9, 115), (-4, 276), (-1.5, 300), (0, 330),
           (1.5, 300), (4, 276), (9, 115), (18, 115), (26, 57), (40, 57), (62.5, 0), (35, 0), (0, 40), (-35, 0)]
    path = poly([(bx + px * sc, sy(py, sc)) for px, py in pts])
    c.drawPath(path, P((150, 105, 70) if not hi else (180, 130, 85)))
    c.drawPath(path, P((14, 16, 30), stroke=2.5))
    if hi: c.drawPath(path, P(GOLD, 0.8, stroke=3))
    if sc > 0.6:   # lattice
        for yy in range(20, 300, 18):
            wl = lerp(55, 3, yy / 300)
            c.drawLine(bx - wl * sc, sy(yy, sc), bx + wl * sc, sy(yy + 9, sc), P((90, 60, 40), 0.6, stroke=1.5))


def draw_liberty(c, o, xc, sc, hi):
    k, name, cc, h, x, w, wt, sp = o
    bx = sx(x, xc, sc)
    green = (110, 175, 150) if not hi else (130, 200, 170)
    ped = poly([(bx - 11 * sc, GY), (bx - 8 * sc, sy(47, sc)), (bx + 8 * sc, sy(47, sc)), (bx + 11 * sc, GY)])
    c.drawPath(ped, P((150, 140, 120))); c.drawPath(ped, P((14, 16, 30), stroke=2.5))
    body = poly([(bx - 5 * sc, sy(47, sc)), (bx - 3 * sc, sy(80, sc)), (bx + 3 * sc, sy(80, sc)), (bx + 5 * sc, sy(47, sc))])
    c.drawPath(body, P(green)); c.drawPath(body, P((14, 16, 30), stroke=2.5))
    c.drawCircle(bx, sy(83, sc), 3 * sc, P(green)); c.drawCircle(bx, sy(83, sc), 3 * sc, P((14, 16, 30), stroke=2))
    c.drawLine(bx + 2.5 * sc, sy(78, sc), bx + 5 * sc, sy(90, sc), P(green, stroke=max(2, 1.8 * sc)))
    c.drawCircle(bx + 5 * sc, sy(92, sc), 1.6 * sc + 2, P((255, 200, 90)))
    if hi: c.drawPath(ped, P(GOLD, 0.8, stroke=3))


def label(c, t, i, xc, sc, a):
    k, name, cc, h, x, w, wt, sp = OBJ[i]
    ts = [s for s, j in STOPS if j == i][0]
    cx = clamp(sx(x, xc, sc), 230, 850)
    top = min(sy(h, sc), GY - 60) - 30
    y = max(540, top - 50)
    v = h * (1 - (1 - clamp((t - ts - 0.15) / 0.6)) ** 3)
    num = f"{v:,.2f} m" if h < 10 else f"{v:,.0f} m"
    r = rank_of(i)
    text(c, num, cx, y, F_CAP, 76 if i == len(OBJ) - 1 else 64, GOLD if i == len(OBJ) - 1 else (255, 255, 255), a, stroke=14)
    line = name if r is None else f"#{r}  {name}"
    fw = 46
    tw = skia.Font(F_SANS, 30).measureText(line)
    if cc:
        flag(c, cc, cx - (tw + fw + 14) / 2, y - 132, fw, a)
        text(c, line, cx - (tw + fw + 14) / 2 + fw + 14, y - 104, F_SANS, 30, (210, 215, 235), a, align="left", stroke=6)
    else:
        text(c, line, cx, y - 104, F_SANS, 30, (210, 215, 235), a, stroke=6)


def frame(c, t):
    xc, sc = cam(t)
    background(c, t, xc)
    cur = max(i for s, i in STOPS if t >= s) if t >= STOPS[0][0] else 0
    for i, o in enumerate(OBJ):
        bx = sx(o[4], xc, sc)
        if bx < -600 or bx > W + 600: continue
        hi = (i == cur)
        if o[0] == "person":
            s_fig = 1.75 * sc / 204
            if s_fig > 0.02:
                figure(c, bx, GY, stand(), s=s_fig, facing=1, body=(246, 246, 242), rim=(GOLD, 0.5))
        elif o[0] == "liberty": draw_liberty(c, o, xc, sc, hi)
        elif o[0] == "eiffel": draw_eiffel(c, o, xc, sc, hi)
        else: draw_tower(c, o, xc, sc, hi, i)
    if t < OVER + 0.4:
        a = seg(t, [s for s, j in STOPS if j == cur][0] + 0.1, [s for s, j in STOPS if j == cur][0] + 0.35)
        label(c, t, cur, xc, sc, a * (1 - seg(t, OVER, OVER + 0.4)))
    # overview: small height tags on every building
    if t > OVER + 0.6:
        a = seg(t, OVER + 0.6, OVER + 1.0) * (1 - seg(t, END + 1.2, END + 1.5))
        for i, o in enumerate(OBJ[2:], start=2):
            text(c, f"{o[3]}", sx(o[4], xc, sc), sy(o[3], sc) - 14, F_SANS, 22, GOLD if i == len(OBJ) - 1 else (220, 225, 240), a, stroke=5)
        text(c, "THE 10 TALLEST BUILDINGS", 540, 700, F_SANS, 34, (210, 215, 235), a, spacing=4, stroke=6)
        text(c, "TO SCALE", 540, 790, F_CAP, 84, GOLD, a, stroke=16)
        text(c, "heights in meters incl. spires", 540, 845, F_SANS, 24, (150, 155, 180), a)
    grain(c, t, 0.02)
    end_text(c, t, END, "Burj Khalifa: 828 m.", "2.5x the Eiffel Tower.", "Where would your city rank?", y=1450)


def events():
    ev = []
    for ts, i in STOPS:
        if i == 0: continue
        if i == len(OBJ) - 1:
            ev += [sfx(ts - 0.05, "riser-2s-strong", -2), sfx(ts + 0.45, "cinematic-drum-big", -1), sfx(ts + 0.8, "data-countup-medium", -6),
                   sfx(ts + 1.4, "data-number-land", -2)]
        else:
            ev += [sfx(ts + 0.25, "whoosh-fast-medium" if i >= 3 else "whoosh-slow-medium", -6), sfx(ts + 0.75, "data-number-land", -8 if i >= 3 else -4)]
    ev += [sfx(OVER + 0.5, "whoosh-slow-medium", -4), sfx(OVER + 1.0, "shimmer-long-sparkle", -6), ["text", END], ["text2", END + 0.8]]
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still":
        stills(lambda c, t: (frame(c, t + 0.3), series_overlay(c, t, 2, "How tall is the tallest building?", 16.3, series="BY THE NUMBERS")),
               [0.8, 2.4, 4.2, 6.5, 9.5, 12.2, 13.6, 14.8, 16.8], os.path.join(HERE, "check_bn2"))
    else:
        finish_v2("BN2_Tallest", frame, T_END, events(), REVEAL, 2, "How tall is the tallest building?", 0.3, 16.6, series="BY THE NUMBERS")
