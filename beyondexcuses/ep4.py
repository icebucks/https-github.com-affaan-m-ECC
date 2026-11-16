"""Folge 4: AUSREDEN vs. DISZIPLIN – Regen, Laufbahn, Tage vergehen, am Ende Sonne + Regenbogen."""
import sys, math
import numpy as np
from lib import *

T_END = 19.0
G = 1200
S = 0.9
BENCH_X = 230
T0, T_LAPS, T_STOP = 1.5, 12.0, 13.3
A_V, B_V = 450.0, 29.5
DAYS = [1, 7, 30, 60, 100]
EXCUSES = ["Zu nass.", "Zu kalt.", "Zu müde.", "Montag dann.", "Morgen."]


def dist(t):
    k = clamp(t - T0, 0, T_LAPS - T0); return A_V * k + B_V * k * k / 2


def runner(t):
    if t < T0:
        k = seg(t, 0.8, 1.3)
        return dict(x=430, p=mix(stand(), dict(lean=30, head=-10, arm_f=-20, elb_f=-60, arm_b=30, elb_b=-60, leg_f=40, leg_b=-30, knee_f=60, knee_b=10), k), lap=1)
    if t < T_LAPS:
        d = dist(t); raw = 580 + d
        return dict(x=-150 + raw % 1380, p=run(t * (11 + 0.5 * (t - T0))), lap=min(5, int(raw // 1380) + 1), running=True)
    if t < T_STOP:
        u = seg(t, T_LAPS, T_STOP)
        x = lerp(-150, 640, 1 - (1 - (t - T_LAPS) / (T_STOP - T_LAPS)) ** 2)
        return dict(x=x, p=run(t * 14) if u < 0.9 else stand(), lap=5, running=True)
    return dict(x=640, p=mix(stand(), cheer(t), seg(t, T_STOP, T_STOP + 0.5)), lap=5)


def rain_amt(t): return 1 - seg(t, 8.0, 12.2)


def draw_rain(c, t, amt):
    if amt <= 0: return
    rng = np.random.default_rng(9)
    n = int(260 * amt)
    xs = rng.uniform(-200, W + 200, 260); sp = rng.uniform(1700, 2300, 260); off = rng.uniform(0, 3000, 260)
    p = P((200, 215, 240), 0.55 * amt, stroke=3)
    for i in range(n):
        y = (off[i] + t * sp[i]) % (G + 300) - 200
        x = xs[i] - (y + 200) * 0.18
        c.drawLine(x, y, x - 8, y + 42, p)
    # splashes on ground
    for i in range(int(40 * amt)):
        x = rng.uniform(0, W); ph = (t * 3 + rng.uniform(0, 1)) % 1.0
        c.drawOval(skia.Rect.MakeXYWH(x - 20 * ph, G + 18 + (i % 5) * 22 - 4 * ph, 40 * ph, 8 * ph), P((220, 230, 250), 0.5 * (1 - ph) * amt, stroke=2))


def clouds(c, t, amt, col):
    if amt <= 0: return
    rng = np.random.default_rng(3)
    for i in range(9):
        x = rng.uniform(-200, W + 200) + t * 12 * (1 + i % 3) + (1 - amt) * (300 if i % 2 else -300)
        y = rng.uniform(-60, 420)
        for k in range(4):
            c.drawCircle(x + k * 90 - 130, y + 30 * math.sin(k * 1.7 + i), 120 + 30 * math.sin(k + i), P(col, 0.85 * amt))


def rainbow(c, a):
    if a <= 0: return
    cols = [(255, 90, 90), (255, 170, 80), (255, 230, 100), (120, 220, 120), (90, 170, 255), (150, 110, 230)]
    for k, col in enumerate(cols):
        r = 700 - k * 26
        c.drawArc(skia.Rect.MakeLTRB(540 - r, G + 200 - r, 540 + r, G + 200 + r), 180, 180, False, P(col, 0.45 * a, stroke=26))


def world(c, t):
    r = rain_amt(t); u = 1 - r
    sky(c, t, lerpc((40, 46, 62), (90, 160, 225), u), lerpc((70, 78, 96), (160, 205, 240), u), lerpc((110, 118, 134), (250, 230, 190), u), G)
    sun(c, 860, lerp(700, 360, seg(t, 10.5, 14)), seg(t, 10.5, 13), r=74)
    rainbow(c, seg(t, 12.5, 14.5))
    clouds(c, t, r * 0.9 + 0.1 * (1 - seg(t, 11, 14)), lerpc((54, 60, 76), (200, 210, 225), u))
    if r > 0.6 and 2.0 < t < 2.25 or 5.2 < t < 5.35:  # lightning flash
        c.drawRect(skia.Rect.MakeLTRB(-300, -500, W + 300, H + 300), P((230, 235, 255), 0.35))
    # city skyline silhouette
    sk = lerpc((50, 56, 72), (120, 150, 180), u)
    rng = np.random.default_rng(12); x = -40
    while x < W + 40:
        w = rng.uniform(60, 130); h = rng.uniform(80, 260)
        c.drawRect(skia.Rect.MakeXYWH(x, G - h, w, h), P(sk))
        for wy in range(int(G - h + 20), G - 20, 34):
            for wx in range(int(x + 12), int(x + w - 12), 26):
                if rng.random() < 0.35: c.drawRect(skia.Rect.MakeXYWH(wx, wy, 10, 14), P((255, 220, 140), 0.55 * r))
        x += w + rng.uniform(4, 20)
    ground(c, G, lerpc((60, 66, 78), (120, 150, 110), u), lerpc((24, 26, 32), (50, 70, 50), u), lerpc((140, 150, 170), (230, 240, 210), u))
    # running track band
    tr = lerpc((120, 60, 56), (196, 92, 74), u)
    c.drawRect(skia.Rect.MakeLTRB(-300, G, W + 300, G + 70), P(tr))
    for y in (G + 22, G + 46):
        c.drawLine(-300, y, W + 300, y, P((255, 255, 255), 0.5, stroke=3))
    c.drawLine(-300, G + 70, W + 300, G + 70, P(INK, 0.6, stroke=4))
    # lamp post
    lx = 900
    c.drawLine(lx, G, lx, G - 360, P(INK, stroke=14)); c.drawLine(lx, G, lx, G - 360, P((70, 74, 86), stroke=8))
    c.drawLine(lx, G - 360, lx - 50, G - 360, P(INK, stroke=10))
    c.drawCircle(lx - 50, G - 340, 16, P((255, 226, 150), 0.6 + 0.4 * r))
    c.drawCircle(lx - 50, G - 330, 120, P((255, 220, 140), 0.25 * r, blur=40))
    # bench
    c.drawLine(BENCH_X - 90, G - 40, BENCH_X + 90, G - 40, P(INK, stroke=22)); c.drawLine(BENCH_X - 90, G - 40, BENCH_X + 90, G - 40, P((120, 84, 58), stroke=14))
    for dx in (-70, 70): c.drawLine(BENCH_X + dx, G - 40, BENCH_X + dx, G, P(INK, stroke=10))
    c.drawLine(BENCH_X - 90, G - 110, BENCH_X + 90, G - 110, P(INK, stroke=20)); c.drawLine(BENCH_X - 90, G - 110, BENCH_X + 90, G - 110, P((120, 84, 58), stroke=12))
    return r


def frame(c, t):
    c.save(); c.translate(540, G); c.scale(1.15, 1.15); c.translate(-540, -G)
    r = world(c, t)
    body = lerpc((226, 230, 238), (250, 248, 242), 1 - r)
    # AUSREDEN on the bench under an umbrella
    sitp = sit(t); sitp.update(arm_f=150, elb_f=-55, head=-6 + 4 * math.sin(t * 1.3))
    late = seg(t, 14.0, 14.6)  # closes umbrella at the end, shrugs
    if late > 0: sitp = mix(sitp, dict(sit(t), arm_f=30, elb_f=40, head=10), late)
    ja = figure(c, BENCH_X - 10, G - 42 - 38 * S, sitp, s=S, facing=1, body=lerpc(body, (200, 200, 210), 0.3), mode="hip")
    label(c, "AUSREDEN", ja["head"][0], ja["head"][1] - (232 if late < 0.5 else 50), GREY, 0.85)
    if late < 0.5:
        hx, hy = ja["hand_f"]
        cx, cy = hx - 10, hy - 95
        c.drawLine(hx, hy + 10, cx, cy, P(INK, stroke=6))
        canopy = skia.Path(); canopy.moveTo(cx - 120, cy)
        canopy.quadTo(cx - 110, cy - 110, cx, cy - 115); canopy.quadTo(cx + 110, cy - 110, cx + 120, cy)
        for k in range(4, -1, -1): canopy.quadTo(cx - 120 + k * 60 + 30, cy - 22, cx - 120 + k * 60, cy)
        canopy.close()
        c.drawPath(canopy, P((70, 120, 200))); c.drawPath(canopy, P(INK, stroke=6))
    # DISZIPLIN
    m = runner(t)
    jd = figure(c, m["x"], G, m["p"], s=S, facing=1, body=body)
    label(c, "DISZIPLIN", jd["head"][0], jd["head"][1] - 50, AMBER, 0.95)
    # day counter
    day = DAYS[m["lap"] - 1]
    text(c, f"TAG {day}", 540, 640, F_CAP, 70, (255, 255, 255), 1.0, stroke=12)
    # excuses as speech bubbles, one per lap
    for i, ex in enumerate(EXCUSES):
        t0 = T0 + 0.3 + i * 2.05
        if t0 < t < t0 + 1.8:
            a = seg(t, t0, t0 + 0.15) * (1 - seg(t, t0 + 1.5, t0 + 1.8))
            bubble(c, 360, ja["head"][1] - 315, ex, a, "speech", tail=(270, ja["head"][1] - 170), size=32)
    if 14.4 < t < 16.0:
        a = seg(t, 14.4, 14.6) * (1 - seg(t, 15.7, 16.0))
        bubble(c, 330, ja["head"][1] - 160, "Morgen fang ich an.", a, "speech", tail=(ja["head"][0] + 20, ja["head"][1] - 30), size=32)
    draw_rain(c, t, r)
    c.restore()
    vignette(c, 0.45)
    end_text(c, t, 16.0, "Es wird nie", "den perfekten Tag geben.", "Fang trotzdem an.", y=1450)
    if t > T_END - 0.5: c.drawRect(skia.Rect.MakeWH(W, H), P((0, 0, 0), (t - (T_END - 0.5)) / 0.5))


def events():
    ev = [["rain", 0.0, 12.6], ["thunder", 2.0], ["thunder", 5.2], ["sunrise", 10.5], ["summit", T_STOP],
          ["text", 16.0], ["text2", 16.8], ["pop", 14.4]]
    for i in range(5): ev.append(["pop", T0 + 0.3 + i * 2.05])
    last = None
    for f in range(int(T_STOP * FPS)):
        t = f / FPS; m = runner(t)
        if m.get("running"):
            k = math.floor(t * (11 + 0.5 * (t - T0)) / math.pi)
            if last is not None and k != last and 0 < m["x"] < W: ev.append(["step", t, False])
            last = k
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still": stills(frame, [1.2, 3.0, 7.0, 11.0, 14.8, 17.5], "/home/claude/mind/ep4")
    else: finish_v2("Folge4_Ausreden", frame, T_END, events(), 12.0, 4, "Welche Ausrede nutzt du?", 1.0, 17.4)
