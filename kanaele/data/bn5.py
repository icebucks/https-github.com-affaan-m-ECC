"""By The Numbers #5: Animals to scale – from an ant to the blue whale (format B · scale zoom).
Numbers (checked 19.11.2026):
  black garden ant (Lasius niger) worker: 3.4–5 mm long (NatureSpot / Collingwood 1979: 3.5–5.0 mm) -> 5 mm
  you: 1.75 m (reference person, as in BN2)
  giraffe: tallest on record, "George" (Masai giraffe, Chester Zoo, 1969): 5.8 m (Guinness World Records "Tallest mammal")
  whale shark: largest scientifically documented, female, Veraval (India), 8 May 2001: 18.8 m (Guinness World Records "Largest fish")
  blue whale: longest scientifically measured, rostrum tip to tail notch: 29.9 m (Wikipedia "Blue whale")
Exact math: 29.9 / 1.75 = 17.1 -> "17 of you"; 29.9 m / 5 mm = 5,980 ants; 29.9 / 18.8 = 1.6x the largest fish.
No elephant (the record height differs between sources: 3.96 m vs. "about 4 m")."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "beyondexcuses"))
sys.path.insert(0, HERE)
os.environ.setdefault("OUT_DIR", HERE)
from lib import *
from dlib import sfx, finish_data, preview, punch, shake, burst, set_bpm, beats, pulse, music, end_card, rich

BPM = 88                       # lofi; every move and landing sits on the beat grid
set_bpm(BPM)
HOOK = ("You are *1.75 m* tall.", "How many of you = *1 blue whale*?")
STICKY = "WAIT FOR THE GIANT"
GY = 1330                      # ground line on screen
GOLD = (255, 200, 80)

# kind, name, sub, size (m), x0 (m, left end), length (m), height (m), number text
OBJ = [
    ("ant",   "Black garden ant", "worker",                      0.005, 0.0,  0.005, 0.0016, "5 mm"),
    ("you",   "You",              "",                            1.75,  0.20, 0.5,   1.75,   "1.75 m"),
    ("giraffe", "Giraffe",        "tallest on record",           5.8,   1.6,  3.4,   5.8,    "5.8 m"),
    ("shark", "Whale shark",      "largest fish ever measured",  18.8,  6.2,  18.8,  2.9,    "18.8 m"),
    ("whale", "Blue whale",       "longest ever measured",       29.9,  27.0, 29.9,  4.1,    "29.9 m"),
]
STOP_BEATS = [0, 3, 6, 9, 13]
MOVE_B = [0, 2, 1.5, 2, 3]                 # the jump to the blue whale is the slow 3-beat build
STOPS = [beats(b) for b in STOP_BEATS]
LAND_T = [0.0] + [beats(b + m) for b, m in zip(STOP_BEATS[1:], MOVE_B[1:])]
REVEAL = STOPS[-1]             # 8.9 s: build starts
LAND = LAND_T[-1]              # 10.9 s: blue whale lands = drop (bar 4 start)
OVER = LAND + beats(1.5)       # zoom out: all five in one view
TIMES_T = LAND + beats(2.5)    # "= 17 of you"
END = LAND + beats(4)          # end card
FOLLOW = LAND + beats(6.5)
LOOP = LAND + beats(7.5)       # zoom back to the ant -> loops into the first frame
T_END = LAND + beats(9.5)


def centre(i):
    o = OBJ[i]
    return o[4] + o[5] / 2


def cam_target(i):
    o = OBJ[i]
    if o[0] in ("shark", "whale"): return centre(i), 760 / o[5]
    if o[0] == "ant": return centre(i), 560 / o[5]
    return centre(i) + (0.35 if o[0] == "you" else 0.0), (560 if o[0] == "you" else 620) / o[6]


OVER_X, OVER_S = 28.5, 880 / 57.5
HOLD = 1.09
CLEAN = False                  # cover: scene without the overview texts


def cam(t):
    """camera centre (m) and scale (px/m); the scale moves in log space"""
    cur = max(i for i, s in enumerate(STOPS) if t >= s) if t >= 0 else 0
    x1, s1 = cam_target(cur)
    nxt = STOPS[cur + 1] if cur + 1 < len(STOPS) else LAND + beats(1.5)
    hold = 1 + (HOLD - 1) * clamp((t - LAND_T[cur]) / max(0.1, nxt - LAND_T[cur]))   # slow push-in while an animal is on screen
    if cur == 0:
        x, s = x1, s1 * hold
    else:
        x0, s0 = cam_target(cur - 1)
        s0 *= HOLD
        u = ease((t - STOPS[cur]) / beats(MOVE_B[cur]))
        s = math.exp(lerp(math.log(s0), math.log(s1), u)) * (hold if t >= LAND_T[cur] else 1.0)
        x = x1 - (1 - u) * (x1 - x0) * s0 / s
    if t > OVER:
        v = ease((t - OVER) / beats(2))
        xs, ss = x, s
        s = math.exp(lerp(math.log(ss), math.log(OVER_S), v)); x = OVER_X - (1 - v) * (OVER_X - xs) * ss / s
        s *= 1 + 0.10 * clamp((t - OVER - beats(2)) / (LOOP - OVER - beats(2)))     # keeps drifting under the end card
    if t > LOOP:
        w = ease((t - LOOP) / (T_END - LOOP))
        xs, ss = x, s
        x0, s0 = cam_target(0)
        s = math.exp(lerp(math.log(ss), math.log(s0), w)); x = x0 - (1 - w) * (x0 - xs) * ss / s
    return x, s


def sx(xm, xc, sc): return 540 + (xm - xc) * sc
def sy(hm, sc): return GY - hm * sc


# ------------------------------------------------------------------ drawing
def background(c, t, xc, sc):
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, GY)], [C((40, 52, 120)), C((86, 70, 150)), C((214, 128, 132))], [0, 0.55, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    c.drawCircle(540, GY - 40, 520, P((255, 190, 140), 0.18 + 0.06 * pulse(t, 4, 3), blur=140))
    rng = np.random.default_rng(5)
    for _ in range(90):
        x, y, r = rng.uniform(0, W), rng.uniform(560, GY - 120), rng.uniform(1.5, 3.2)
        c.drawCircle((x - xc * 2) % W, y, r, P((255, 236, 210), 0.12 + 0.25 * abs(math.sin(t * 0.8 + x))))
    # hills with a little parallax
    for k, (col, amp, base, par) in enumerate((((96, 70, 130), 80, GY - 150, 0.02), ((70, 54, 104), 50, GY - 60, 0.05))):
        p = skia.Path(); p.moveTo(-50, GY)
        for xx in range(-50, W + 60, 40):
            p.lineTo(xx, base - amp * (0.5 + 0.5 * math.sin((xx + xc * sc * par) * 0.006 + k * 2)))
        p.lineTo(W + 50, GY); p.close()
        c.drawPath(p, P(col, 0.9))
    c.drawRect(skia.Rect.MakeLTRB(0, GY, W, H), P((30, 26, 52)))
    c.drawLine(0, GY, W, GY, P((230, 215, 255), 0.7, stroke=4))
    # ruler ticks: one per 10^k metres, k chosen so ticks are 40–400 px apart
    k = math.floor(math.log10(120 / sc)); step = 10 ** k
    if 120 / sc / step > 5: step *= 5
    elif 120 / sc / step > 2: step *= 2
    m0 = math.floor((xc - 540 / sc) / step) * step
    m = m0
    while sx(m, xc, sc) < W + 10:
        X = sx(m, xc, sc)
        c.drawLine(X, GY, X, GY + 18, P((200, 190, 240), 0.55, stroke=2))
        m += step


def draw_ant(c, o, xc, sc, t, hi):
    L = o[5]; x0 = sx(o[4], xc, sc); u = L * sc       # u = body length in px
    if u < 1.2:
        c.drawCircle(x0 + u / 2, GY - 1, max(1.2, u / 2), P((20, 16, 24))); return
    y = GY - 0.55 * u * 0.3
    col = (26, 22, 30); rim = (255, 200, 80) if hi else (90, 80, 110)
    wob = math.sin(t * 22) * 0.04 * u
    # legs (3 pairs, walking)
    for j, fx in enumerate((0.38, 0.47, 0.56)):
        for s_ in (-1, 1):
            ph = math.sin(t * 22 + j * 2 + (s_ > 0) * 3)
            hx, hy = x0 + fx * u, y + 0.02 * u
            kx, ky = hx + (0.06 + 0.04 * ph) * u * s_ * 0.5 + 0.03 * u, y - 0.08 * u
            c.drawLine(hx, hy, kx, ky, P(col, stroke=max(1.0, 0.025 * u)))
            c.drawLine(kx, ky, kx + (0.1 * ph + 0.05 * s_) * u * 0.6, GY, P(col, stroke=max(1.0, 0.02 * u)))
    for cxr, ry, rx in ((0.18, 0.13, 0.17), (0.48, 0.09, 0.15), (0.8, 0.11, 0.12)):   # gaster, thorax, head
        e = skia.Rect.MakeXYWH(x0 + (cxr - rx) * u, y - ry * u + (wob if cxr > 0.7 else 0), 2 * rx * u, 2 * ry * u)
        c.drawOval(e, P(col)); c.drawOval(e, P(rim, 0.6, stroke=max(1.0, 0.012 * u)))
    hx, hy = x0 + 0.88 * u, y - 0.08 * u + wob
    c.drawLine(hx, hy, hx + 0.12 * u, hy - 0.22 * u, P(col, stroke=max(1.0, 0.015 * u)))
    c.drawLine(hx + 0.12 * u, hy - 0.22 * u, hx + 0.24 * u, hy - 0.12 * u, P(col, stroke=max(1.0, 0.015 * u)))
    c.drawCircle(x0 + 0.86 * u, y - 0.12 * u + wob, 0.025 * u, P((255, 255, 255), 0.5))


def draw_giraffe(c, o, xc, sc, t, hi):
    x0 = sx(o[4], xc, sc); m = sc                      # 1 m in px; body plan in metres (total height 5.8 m)
    def P2(xm, hm): return (x0 + xm * m, GY - hm * m)
    col = (204, 150, 92) if not hi else (208, 158, 100); spot = (140, 86, 40); ink = (24, 20, 30)   # r < 210: not read as gold text by the audit
    sw = math.sin(t * 2.2) * 0.05
    for lx in (0.35, 0.65, 2.25, 2.55):                 # legs
        c.drawLine(*P2(lx, 2.2), *P2(lx + (sw if lx > 1 else -sw), 0.0), P(ink, stroke=0.24 * m + 2))
        c.drawLine(*P2(lx, 2.2), *P2(lx + (sw if lx > 1 else -sw), 0.0), P(col, stroke=0.17 * m))
    body = skia.Path(); body.addOval(skia.Rect.MakeLTRB(*P2(0.1, 3.1), *P2(2.9, 1.95)))
    neck = poly([P2(2.25, 2.7), P2(2.75, 2.2), P2(3.25, 5.1), P2(2.95, 5.25)])
    head = poly([P2(2.85, 5.25), P2(3.2, 5.55), P2(3.75, 5.2), P2(3.6, 5.0), P2(3.1, 5.0)])
    for pth in (body, neck, head):
        c.drawPath(pth, P(col)); c.drawPath(pth, P(ink, stroke=max(2, 0.05 * m)))
    rng = np.random.default_rng(2)
    for _ in range(26):
        xm, hm = rng.uniform(0.4, 2.7), rng.uniform(2.15, 2.95)
        c.drawCircle(*P2(xm, hm), 0.09 * m, P(spot, 0.85))
    for hm in (2.9, 3.4, 3.9, 4.4, 4.85):
        c.drawCircle(*P2(2.62 + (hm - 2.9) * 0.18, hm), 0.07 * m, P(spot, 0.85))
    for dx in (0.0, 0.14):                              # ossicones up to 5.8 m
        c.drawLine(*P2(3.12 + dx, 5.5), *P2(3.1 + dx, 5.75), P(ink, stroke=0.06 * m + 1))
        c.drawCircle(*P2(3.1 + dx, 5.76), 0.045 * m + 1, P(ink))
    c.drawCircle(*P2(3.42, 5.32), 0.05 * m + 1, P(ink))
    c.drawLine(*P2(0.1, 2.9), *P2(-0.25, 2.2), P(ink, stroke=0.05 * m + 1))   # tail
    if hi: c.drawPath(neck, P(GOLD, 0.7, stroke=3))


def fish_path(x0, L, hmid, H, m, kind):
    """side outline of a long sea animal (whale shark / blue whale), x0 = snout left, pointing right"""
    def Q(f, h): return (x0 + (L - f * L) * m, GY - (hmid + h) * m)        # f = 0 at the snout (right), 1 at the tail
    p = skia.Path()
    top = [(0.0, 0.05), (0.04, 0.42), (0.12, 0.5), (0.3, 0.5), (0.55, 0.42), (0.78, 0.2), (0.88, 0.1)]
    bot = [(0.88, -0.1), (0.78, -0.17), (0.55, -0.32), (0.3, -0.48), (0.12, -0.5), (0.04, -0.4), (0.0, -0.05)]
    if kind == "whale":
        top = [(0.0, 0.0), (0.03, 0.3), (0.1, 0.42), (0.28, 0.48), (0.5, 0.42), (0.72, 0.22), (0.86, 0.1)]
        bot = [(0.86, -0.1), (0.72, -0.2), (0.5, -0.36), (0.28, -0.5), (0.12, -0.5), (0.03, -0.32), (0.0, 0.0)]
    pts = [Q(f, h * H) for f, h in top + bot]
    p.moveTo(*pts[0])
    for a in pts[1:]: p.lineTo(*a)
    p.close()
    return p, Q


def draw_shark(c, o, xc, sc, t, hi):
    L, H = o[5], o[6]; x0 = sx(o[4], xc, sc); m = sc; hmid = 1.9
    sway = math.sin(t * 2.5) * 0.06
    body, Q = fish_path(x0, L, hmid, H, m, "shark")
    col = (70, 96, 140) if not hi else (84, 114, 165); ink = (14, 16, 30)
    tail = poly([Q(0.86, 0.1 * H), Q(1.0, 1.3 * H + sway * H), Q(0.96, 0.05), Q(1.0, -0.8 * H + sway * H), Q(0.86, -0.1 * H)])
    dors = poly([Q(0.36, 0.48 * H), Q(0.46, 1.05 * H), Q(0.52, 0.44 * H)])
    pec = poly([Q(0.22, -0.3 * H), Q(0.32, -0.95 * H), Q(0.3, -0.38 * H)])
    for pth in (tail, dors, pec, body):
        c.drawPath(pth, P(col)); c.drawPath(pth, P(ink, stroke=max(2, 0.05 * m)))
    c.save(); c.clipPath(body, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(x0 - 10, GY - (hmid - 0.15 * H) * m, x0 + L * m + 10, GY), P((180, 192, 214), 0.9))   # pale belly
    rng = np.random.default_rng(3)
    for _ in range(120):
        f, h = rng.uniform(0.04, 0.85), rng.uniform(-0.05, 0.45)
        c.drawCircle(*Q(f, h * H), 0.07 * m + 0.6, P((186, 200, 228), 0.85))   # spots below the audit's white threshold
    c.restore()
    c.drawPath(body, P(ink, stroke=max(2, 0.05 * m)))
    c.drawCircle(*Q(0.035, 0.12 * H), 0.06 * m + 1, P(ink))
    if hi: c.drawPath(body, P(GOLD, 0.75, stroke=3))


def draw_whale(c, o, xc, sc, t, hi):
    L, H = o[5], o[6]; x0 = sx(o[4], xc, sc); m = sc; hmid = 2.6
    sway = math.sin(t * 1.8) * 0.08
    body, Q = fish_path(x0, L, hmid, H, m, "whale")
    col = (104, 136, 176) if not hi else (120, 156, 200); ink = (14, 16, 30)
    fl = poly([Q(0.86, 0.1 * H), Q(0.99, 0.9 * H + sway * H), Q(1.0, 0.75 * H + sway * H), Q(0.95, 0.0), Q(1.0, -0.6 * H + sway * H),
               Q(0.99, -0.75 * H + sway * H), Q(0.86, -0.1 * H)])
    dors = poly([Q(0.7, 0.26 * H), Q(0.75, 0.42 * H), Q(0.76, 0.22 * H)])
    pec = poly([Q(0.24, -0.3 * H), Q(0.36, -0.75 * H), Q(0.33, -0.36 * H)])
    for pth in (fl, dors, pec, body):
        c.drawPath(pth, P(col)); c.drawPath(pth, P(ink, stroke=max(2, 0.05 * m)))
    c.save(); c.clipPath(body, doAntiAlias=True)
    rng = np.random.default_rng(6)
    for _ in range(70):                                   # mottled skin
        f, h = rng.uniform(0.05, 0.85), rng.uniform(-0.3, 0.45)
        c.drawCircle(*Q(f, h * H), 0.12 * m + 0.6, P((176, 196, 222), 0.35))
    for k in range(7):                                    # throat grooves
        hh = -0.18 - 0.045 * k
        c.drawLine(*Q(0.02 + 0.02 * k, hh * H), *Q(0.32, hh * H), P((70, 92, 128), 0.8, stroke=max(1, 0.03 * m)))
    c.restore()
    c.drawPath(body, P(ink, stroke=max(2, 0.05 * m)))
    c.drawCircle(*Q(0.1, -0.02 * H), 0.08 * m + 1, P(ink))
    if hi: c.drawPath(body, P(GOLD, 0.75, stroke=3))


def label(c, t, i, xc, sc, a):
    k, name, sub, size, x0, L, Hh, num = OBJ[i]
    last = i == len(OBJ) - 1
    cx = sx(x0 + L / 2, xc, sc)
    top = sy(Hh + (2.6 if k == "whale" else 1.9 if k == "shark" else 0), sc)
    y = clamp(top - 70, 700, 1180)
    big = 96 if last else 72
    v = size * (1 - (1 - clamp((t - STOPS[i] - 0.05) / max(0.2, LAND_T[i] - STOPS[i] - 0.05))) ** 3) if i else size
    if k == "ant": txt = f"{v * 1000:.0f} mm"
    elif size < 10: txt = f"{v:.2f} m" if k == "you" else f"{v:.1f} m"
    else: txt = f"{v:.1f} m"
    line = name + (f" · {sub}" if sub else "")
    half = max(skia.Font(F_CAP, big).measureText(num) / 2, skia.Font(F_SANS, 30).measureText(line) / 2) + 10
    cx = clamp(cx, 60 + half, 880 - half)
    pz = punch(t, LAND_T[i], 0.4 if last else 0.24)
    c.save(); c.translate(cx, y - 26); c.scale(pz, pz)
    text(c, txt, 0, 26, F_CAP, big, GOLD if last else (255, 255, 255), a, stroke=14)
    c.restore()
    text(c, line, cx, y - 100, F_SANS, 30, (226, 228, 245), a, stroke=7)


def draw_all(c, t, xc, sc, cur):
    for i, o in enumerate(OBJ):
        L = o[5]
        if sx(o[4] + L, xc, sc) < -400 or sx(o[4], xc, sc) > W + 400: continue
        hi = i == cur
        if o[0] == "ant": draw_ant(c, o, xc, sc, t, hi)
        elif o[0] == "you":
            s_fig = 1.75 * sc / 204
            if s_fig > 0.015:
                figure(c, sx(o[4] + 0.25, xc, sc), GY, stand(), s=s_fig, facing=-1, body=(232, 216, 192), rim=(GOLD, 0.5 if hi else 0.2))
            else:
                c.drawLine(sx(o[4] + 0.25, xc, sc), GY, sx(o[4] + 0.25, xc, sc), GY - 1.75 * sc, P((232, 216, 192), stroke=2))
        elif o[0] == "giraffe": draw_giraffe(c, o, xc, sc, t, hi)
        elif o[0] == "shark": draw_shark(c, o, xc, sc, t, hi)
        else: draw_whale(c, o, xc, sc, t, hi)


def current(t):
    return max(i for i, s in enumerate(STOPS) if t >= s) if t >= 0 else 0


def frame(c, t):
    xc, sc = cam(t)
    dx, dy = shake(t, LAND, 22, 0.45)
    c.save(); c.translate(dx, dy)
    background(c, t, xc, sc)
    cur = current(t)
    o = OBJ[cur]
    c.drawCircle(sx(o[4] + o[5] / 2, xc, sc), GY - 200, 260, P(GOLD, 0.05 + 0.10 * pulse(t, 1, 7), blur=100))
    if t < beats(4) + 0.4:   # hero for the hook: the giant's ghost in the sky ("how many of you = 1 blue whale?")
        ga = 1 - seg(t, beats(4) - 0.3, beats(4) + 0.4)
        m = 24.0; hm = (GY - 790) / m
        c.saveLayerAlpha(None, int(110 * ga))
        body, Q = fish_path(150 + 12 * math.sin(t * 1.3), 29.9, hm, 4.1, m, "whale")
        H_ = 4.1
        fl = poly([Q(0.86, 0.1 * H_), Q(0.99, 0.9 * H_), Q(1.0, 0.75 * H_), Q(0.95, 0.0), Q(1.0, -0.6 * H_), Q(0.99, -0.75 * H_), Q(0.86, -0.1 * H_)])
        pec = poly([Q(0.24, -0.3 * H_), Q(0.36, -0.75 * H_), Q(0.33, -0.36 * H_)])
        for pth in (fl, pec, body):
            c.drawPath(pth, P((150, 190, 240))); c.drawPath(pth, P((230, 240, 255), stroke=4))
        c.restore()
        pz = 1 + 0.12 * pulse(t, 1, 8)
        c.save(); c.translate(540, 820); c.scale(pz, pz)
        text(c, "?", 0, 36, F_CAP, 120, GOLD, 0.9 * ga, stroke=16)
        c.restore()
    draw_all(c, t, xc, sc, cur if t < OVER else -1)
    if t < OVER + 0.3 and t < LOOP:
        a = seg(t, STOPS[cur] + 0.08, STOPS[cur] + 0.3) * (1 - seg(t, OVER, OVER + 0.3))
        label(c, t, cur, xc, sc, a)
    if t > OVER + 0.4 and t < LOOP and not CLEAN:      # overview: tags + the search word, big
        a = seg(t, OVER + 0.4, OVER + 0.8) * (1 - seg(t, END - 0.3, END))
        for i, ob in enumerate(OBJ[2:], start=2):
            hh = ob[6] + (2.6 if ob[0] == "whale" else 1.9 if ob[0] == "shark" else 0)
            text(c, ob[7], clamp(sx(ob[4] + ob[5] / 2, xc, sc), 100, 840), sy(hh, sc) - 18, F_SANS, 32, GOLD if i == 4 else (230, 232, 245), a, stroke=7)
        text(c, "ANIMALS", 540, 760, F_CAP, 88, (255, 255, 255), a, stroke=16)
        text(c, "TO SCALE", 540, 852, F_CAP, 88, GOLD, a, stroke=16)
        b = seg(t, TIMES_T, TIMES_T + 0.3) * (1 - seg(t, END - 0.3, END))
        if b > 0:
            pz = punch(t, TIMES_T, 0.3)
            c.save(); c.translate(540, 990); c.scale(pz, pz)
            rich(c, "Blue whale = *17 of you*", 0, 0, 60, b, maxw=800)
            c.restore()
    if LAND <= t < LAND + 0.9:
        burst(c, t, LAND, clamp(sx(OBJ[-1][4] + OBJ[-1][5] / 2, xc, sc), 230, 850), 980, 30)
    c.restore()
    if LAND <= t < LAND + 0.16:
        c.drawRect(skia.Rect.MakeWH(W, H), P((255, 240, 210), 0.45 * (1 - (t - LAND) / 0.16)))
    grain(c, t, 0.02)
    if not CLEAN: end_card(c, t, END, "Blue whale: *29.9 m* =", "17 of you, or *5,980 ants*.", "Biggest animal you've seen?", y=1080,
             alpha=1 - seg(t, LOOP - 0.2, LOOP + 0.2))


def events():
    ev = []
    for i in range(1, len(OBJ)):
        ts, land = STOPS[i], LAND_T[i]
        if i == len(OBJ) - 1:
            ev += [sfx(land - 2.0, "riser-2s-strong", -3), sfx(land - 1.2, "data-countup-medium", -8), sfx(land, "cinematic-drum-big", -1),
                   sfx(land, "data-number-land", -2), sfx(land + 0.15, "shimmer-medium-bright", -8)]
        else:
            ev += [sfx(ts + 0.1, "whoosh-slow-medium" if i == 1 else "whoosh-fast-medium", -6),
                   sfx(land - 0.5, "data-countup-short", -12), sfx(land, "data-number-land", -5), sfx(land, f"tone-step-{i}", -12)]
    ev += [sfx(OVER + 0.2, "whoosh-slow-medium", -6), sfx(OVER + 0.6, "shimmer-long-sparkle", -9), sfx(TIMES_T, "pop-large-in", -6),
           sfx(END, "whoosh-medium-soft", -8), sfx(LOOP + 0.3, "whoosh-fast-medium", -6),
           music("lofi", BPM, build=REVEAL, drop=LAND, outro=END, seed=5)]
    return ev


def step(t): return current(t) + 1


if __name__ == "__main__":
    if sys.argv[1] == "still":
        preview(frame, 5, *HOOK, FOLLOW, [float(a) for a in sys.argv[2:]] or [0.05, 0.5, 2.0, 2.6, 3.6, 5.3, 6.5, 8.0, 9.5, 10.95, 11.6, 12.4, 13.3, 15.4, 16.6, T_END - 0.05],
                os.path.join(HERE, "check_bn5"), sticky=STICKY, hook_end=beats(4), step_fn=step, steps=len(OBJ))
    elif sys.argv[1] == "cover":
        import dlib
        CLEAN = True
        lines = [(ln, 190) for ln in " ".join(sys.argv[2:]).split("|")]
        dlib.cover(frame, OVER + beats(2.2), lines, os.path.join(HERE, "Cover_BN5.jpg"), 5)
    else:
        finish_data("BN5_AnimalsScale", frame, T_END, events(), REVEAL, 5, *HOOK, FOLLOW, sticky=STICKY, hook_end=beats(4),
                    step_fn=step, steps=len(OBJ))
