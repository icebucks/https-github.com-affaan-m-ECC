"""Episode 9: SCROLLER vs. LEARNER – city rooftop at night until sunrise.
Scroller sits in the blue phone glow all night. Learner reads by a lantern; every finished book becomes a step.
At sunrise Learner climbs his book stairs above the city – Scroller hasn't moved."""
import sys, math
import numpy as np
from lib import *

T_END = 17.0
G = 1240
S = 1.0
XL, XS = 270, 700                     # Learner reading spot / Scroller on his crate
COLS = [(360 + i * 44, 2.4 + i * 1.55) for i in range(6)]   # (x, time the column appears)
BH = 26                                # book height
TURN = 11.9
BOOKCOLS = [(200, 90, 80), (80, 130, 200), (90, 170, 120), (230, 180, 80), (150, 100, 190), (220, 120, 60)]
SCROLL_TALK = [(1.6, "Just 5 more minutes…"), (4.8, "lol"), (7.6, "One more video…")]


def night(t): return 1 - seg(t, TURN - 1.6, TURN + 1.0)   # 1 = deep night, 0 = morning


def stair_top(x):
    """height of the book stairs at x (0 if no column)"""
    for i, (cx, _) in enumerate(COLS):
        if cx - 22 <= x <= cx + 22: return (i + 1) * BH
    return 0


def learner(t):
    if t < TURN:
        # reads; short pause to place each finished book
        for cx, tc in COLS:
            if tc - 0.45 < t < tc + 0.15:
                return dict(x=XL, p=dict(stand(), lean=20, arm_f=80, elb_f=-10, arm_b=60, elb_b=-10), f=1, y=G, place=(cx, tc))
        return dict(x=XL, p=sit(t), f=1, y=G, read=True)
    # climbs the stairs (one column per step), then cheers on top
    k = seg(t, TURN, TURN + 1.8)
    x = lerp(XL + 60, COLS[-1][0], k)
    y = G - stair_top(x)
    if k < 1: return dict(x=x, p=walk(t * 9, lean=10), f=1, y=y)
    return dict(x=COLS[-1][0], p=cheer(t), f=1, y=G - 6 * BH)


def scroller(t):
    if t < TURN + 1.2:
        bob = math.sin(t * 1.3) * 3
        return dict(x=XS, p=dict(sit(t), lean=30 + bob, head=35, arm_f=50, elb_f=-70, arm_b=40, elb_b=-60), f=-1)
    k = seg(t, TURN + 1.2, TURN + 1.8)   # looks up – too late
    return dict(x=XS, p=mix(dict(sit(t), lean=30, head=35, arm_f=50, elb_f=-70, arm_b=40, elb_b=-60),
                            dict(sit(t), lean=-4, head=-25, arm_f=30, elb_f=-60, arm_b=20, elb_b=-50), k), f=-1)


# ------------------------------------------------------------------ world
def city(c, t, n):
    rng = np.random.default_rng(3)
    x = -320
    while x < W + 300:
        w = rng.uniform(70, 150); h = rng.uniform(160, 420)
        base = G - 40
        col = lerpc((44, 52, 86), (20, 22, 40), n)
        c.drawRect(skia.Rect.MakeXYWH(x, base - h, w, h + 60), P(col))
        c.drawRect(skia.Rect.MakeXYWH(x, base - h, w, h + 60), P(INK, 0.6, stroke=3))
        for wy in range(int(base - h + 18), int(base - 10), 30):
            for wx in range(int(x + 12), int(x + w - 12), 24):
                if rng.random() < 0.35:
                    on = n * (0.5 + 0.5 * math.sin(t * 0.6 + wx * 0.1 + wy))
                    c.drawRect(skia.Rect.MakeXYWH(wx, wy, 10, 14), P((255, 214, 130), 0.25 + 0.6 * on))
        x += w + rng.uniform(4, 20)


def world(c, t):
    n = night(t)
    sky(c, t, lerpc((120, 165, 230), (10, 14, 38), n), lerpc((255, 190, 140), (24, 30, 70), n), lerpc((255, 220, 160), (48, 50, 100), n), G,
        stars=n)
    moon(c, 820, lerp(1150, 560, n), clamp(n * 1.4))
    sun(c, 820, lerp(1260, 900, 1 - n), clamp((1 - n) * 1.5), r=74)
    city(c, t, n)
    haze(c, G - 40, lerpc((255, 200, 150), (30, 30, 70), n), 0.4, 220)
    # rooftop
    c.drawRect(skia.Rect.MakeLTRB(-300, G, W + 300, H + 300), P(lerpc((120, 110, 120), (34, 34, 48), n)))
    c.drawRect(skia.Rect.MakeLTRB(-300, G, W + 300, G + 20), P(lerpc((160, 150, 160), (60, 60, 80), n)))
    c.drawLine(-300, G, W + 300, G, P(INK, stroke=5))
    # vents / antenna for silhouette interest
    c.drawRect(skia.Rect.MakeXYWH(930, G - 90, 70, 90), P(lerpc((140, 130, 140), (44, 44, 60), n)))
    c.drawRect(skia.Rect.MakeXYWH(930, G - 90, 70, 90), P(INK, stroke=5))
    c.drawLine(120, G, 120, G - 260, P(INK, stroke=6)); c.drawLine(90, G - 230, 150, G - 230, P(INK, stroke=5))
    return n


def lantern(c, x, n):
    c.drawCircle(x, G - 40, 260, P((255, 190, 100), 0.18 + 0.12 * n, blur=60))
    c.drawRect(skia.Rect.MakeXYWH(x - 14, G - 60, 28, 40), P((255, 214, 140)))
    c.drawRect(skia.Rect.MakeXYWH(x - 14, G - 60, 28, 40), P(INK, stroke=5))
    c.drawLine(x - 18, G - 62, x + 18, G - 62, P(INK, stroke=6))


def book(c, x, y, col, w=44, h=BH, ang=0, a=1.0):
    c.save(); c.translate(x, y); c.rotate(ang)
    r = skia.Rect.MakeXYWH(-w / 2, -h, w, h)
    c.drawRect(r, P(col, a)); c.drawRect(r, P(INK, a, stroke=5))
    c.drawLine(-w / 2 + 6, -h + 6, w / 2 - 6, -h + 6, P((250, 245, 230), 0.8 * a, stroke=3))
    c.restore()


def stairs(c, t):
    for i, (cx, tc) in enumerate(COLS):
        if t < tc: continue
        for k in range(i + 1):
            drop = 0 if k < i else (1 - ease((t - tc) / 0.3)) * 60
            book(c, cx, G - k * BH - drop, BOOKCOLS[(i + k) % 6])


def phone(c, J, n):
    hx, hy = J["hand_f"]
    c.drawCircle(hx, hy, 240, P((90, 160, 255), 0.22 * n + 0.05, blur=60))
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(hx - 13, hy - 22, 26, 42), 6, 6)
    c.drawRRect(r, P(INK)); c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(hx - 9, hy - 18, 18, 34), 4, 4), P((170, 215, 255)))


def battery(c, x, y, t):
    lvl = clamp(1 - t / (TURN + 1.5))
    col = (120, 220, 120) if lvl > 0.3 else (255, 90, 80)
    c.drawRect(skia.Rect.MakeXYWH(x - 24, y - 12, 44, 22), P(INK, stroke=4))
    c.drawRect(skia.Rect.MakeXYWH(x + 20, y - 5, 5, 8), P(INK))
    c.drawRect(skia.Rect.MakeXYWH(x - 21, y - 9, 38 * max(0.04, lvl), 16), P(col))
    text(c, f"{max(1, int(lvl * 100))}%", x + 60, y + 9, F_SANS, 24, col, 1.0, align="left", stroke=4)


def frame(c, t):
    c.save(); c.translate(540, G); c.scale(1.45, 1.45); c.translate(-540, -G)
    n = world(c, t)
    body = lerpc((250, 248, 244), (200, 205, 228), n)
    lantern(c, XL - 70, n)
    stairs(c, t)
    # Scroller
    s = smooth(scroller, t)
    crate = skia.Rect.MakeXYWH(XS - 40, G - 62, 80, 62)
    c.drawRect(crate, P((150, 110, 70))); c.drawRect(crate, P(INK, stroke=5))
    shadow(c, XS, G, S)
    js = figure(c, XS, G - 62, s["p"], s=S, facing=s["f"], body=body, mode="hip", rim=((120, 180, 255), 0.6 * n + 0.1), light=(-1, 0.4))
    phone(c, js, n)
    if not (TURN + 1.5 < t < TURN + 3.5): plate_label(c, "SCROLLER", js["head"][0], js["head"][1] - 52, GREY, 0.9)
    if not (TURN + 1.5 < t < TURN + 3.5): battery(c, js["head"][0] - 10, js["head"][1] - 110, t)
    # Learner
    l = smooth(learner, t)
    shadow(c, l["x"], l["y"], S)
    if t < TURN + 0.2:  # Bücherstapel als Sitz
        for k in range(2): book(c, XL + 6, G - k * 20, BOOKCOLS[(k + 3) % 6], w=58, h=20)
    if l.get("read"):
        jl = figure(c, l["x"], G - 40, l["p"], s=S, facing=1, body=body, mode="hip", rim=((255, 200, 120), 0.55), light=(-1, 0))
        book(c, jl["hand_f"][0] + 6, jl["hand_f"][1] + 8, BOOKCOLS[sum(1 for _, tc in COLS if t > tc) % 6], w=40, h=30, ang=-20)
    else:
        jl = figure(c, l["x"], l["y"], l["p"], s=S, facing=1, body=body, rim=((255, 200, 120), 0.55), light=(-1 if t < TURN else 1, -0.6))
        if l.get("place"):
            cx, tc = l["place"]; k = ease((t - (tc - 0.45)) / 0.45)
            book(c, lerp(jl["hand_f"][0], cx, k), lerp(jl["hand_f"][1], G - COLS.index((cx, tc)) * BH - 40, k), BOOKCOLS[COLS.index((cx, tc)) % 6])
    if t < TURN - 0.5:
        c.drawCircle(XL - 10, G - 30, 4, P((0, 0, 0), 0))  # (Platzhalter für Lesepose)
    plate_label(c, "LEARNER", jl["head"][0], jl["head"][1] - 52, AMBER, 0.95)
    # bubbles
    for ts, txt in SCROLL_TALK:
        if ts < t < ts + 1.9:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.6, ts + 1.9))
            bubble(c, min(js["head"][0] - 40, 650), js["head"][1] - 230, txt, a, "think", tail=(js["head"][0] - 30, js["head"][1] - 130), size=32,
                   pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    if TURN + 1.6 < t < TURN + 3.4:
        a = seg(t, TURN + 1.6, TURN + 1.8) * (1 - seg(t, TURN + 3.1, TURN + 3.4))
        bubble(c, min(js["head"][0], 660), js["head"][1] - 125, "It's morning?!", a, "speech", tail=(js["head"][0], js["head"][1] - 30), size=32)
    c.restore()
    vignette(c, 0.45)
    grain(c, t, 0.035)
    end_text(c, t, 14.4, "Same night.", "Same hours.", "One of them built stairs.", y=1430)


def events():
    ev = []
    for ts, _ in SCROLL_TALK: ev.append(["pop", ts])
    for cx, tc in COLS: ev.append(["land", tc])
    for k in range(6): ev.append(["step", TURN + 0.15 + k * 0.3, False])
    ev += [["sunrise", TURN - 1.4], ["summit", TURN + 1.8], ["pop", TURN + 1.6], ["text", 14.4], ["text2", 15.2]]
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still":
        stills(frame, [0.4, 3.3, 7.8, 11.0, 13.8, 15.8], "check/ep9")
    else:
        finish_v2("Folge9_Scroller", frame, T_END, events(), TURN, 9, "Did you scroll all night?", 0.3, 16.0)
