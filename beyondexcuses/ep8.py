"""Episode 8: IMPATIENCE vs. PATIENCE – spring meadow, time-lapse of days and nights.
Both plant a seed. Impatience digs his up every morning to check. Patience waters and waits – his tree blooms."""
import sys, math
import numpy as np
from lib import *

T_END = 17.2
G = 1240                 # ground line
S = 1.0                  # figure scale
XP, XI = 380, 720        # Patience / Impatience
LAPSE = (2.4, 11.4)      # time-lapse window: three day/night cycles
TURN = 11.8
DIGS = [(3.3, "Still nothing?"), (6.3, "Why so slow?"), (9.3, "This doesn't work.")]


def day_phase(t):
    """0 = noon … 0.5 = midnight; three cycles during the lapse, warm morning before/after"""
    if t < LAPSE[0]: return 0.85
    if t > LAPSE[1]: return 0.85 + 0.15 * seg(t, LAPSE[1], LAPSE[1] + 1.2)
    k = (t - LAPSE[0]) / (LAPSE[1] - LAPSE[0])
    return (0.85 + 3 * k) % 1.0


def light(t):
    """daylight 0..1"""
    ph = day_phase(t)
    return clamp(0.5 + 0.62 * math.cos(2 * math.pi * ph))


def growth(t): return ease((t - 2.6) / (TURN - 2.6))


def bloom(t): return seg(t, TURN, TURN + 0.9)


# ------------------------------------------------------------------ figures
def patience(t):
    if t < 1.6: return dict(p=mix(stand(), crouch(), seg(t, 0.0, 0.5)), f=1, x=XP)
    if t < 2.5: return dict(p=dict(stand(), lean=14, arm_f=70, elb_f=-20), f=1, x=XP, can=1)
    if t < TURN:
        # sits beside the plant; short watering every "morning"
        for d, _ in DIGS:
            if d - 0.4 < t < d + 0.5: return dict(p=dict(stand(), lean=14, arm_f=70, elb_f=-20), f=1, x=XP, can=1)
        return dict(p=sit(t), f=1, x=XP - 80, sit=True)
    return dict(p=cheer(t), f=1, x=XP - 70)


def impatience(t):
    if t < 1.6: return dict(p=mix(stand(), crouch(), seg(t, 0.0, 0.5)), f=-1, x=XI)
    for k, (d, _) in enumerate(DIGS):
        if d - 0.2 < t < d + 1.1:  # digs the seed up again
            dig = math.sin((t - d) * 14) * 12
            return dict(p=dict(crouch(), arm_f=-10 + dig, arm_b=-25 - dig), f=-1, x=XI, dig=k)
    if t < DIGS[-1][0] + 1.1: return dict(p=dict(stand(), head=8), f=-1, x=XI)
    if t < TURN + 0.4: return dict(p=arms_crossed(head=6), f=-1, x=XI)
    k = seg(t, TURN + 0.4, TURN + 1.2)
    return dict(p=mix(arms_crossed(), dict(slump(), head=-20), k), f=-1, x=XI)


# ------------------------------------------------------------------ world
def sky_cols(dl):
    night = ((14, 18, 44), (30, 34, 78), (60, 60, 110))
    day = ((110, 175, 235), (175, 215, 245), (255, 236, 200))
    dusk = ((70, 80, 150), (240, 150, 120), (255, 200, 140))
    u = dl
    if u < 0.5:
        k = u / 0.5; return tuple(lerpc(n, d, k) for n, d in zip(night, dusk))
    k = (u - 0.5) / 0.5; return tuple(lerpc(d, y, k) for d, y in zip(dusk, day))


def tree(c, x, t):
    g = growth(t); b = bloom(t)
    if g <= 0.01: return
    h = 40 + 330 * g
    tw = 6 + 16 * g
    c.drawLine(x, G, x, G - h, P(INK, stroke=tw + 7)); c.drawLine(x, G, x, G - h, P((120, 84, 58), stroke=tw))
    if g > 0.25:
        for side, yy in ((-1, 0.55), (1, 0.7), (-1, 0.82)):
            bx, by = x + side * 70 * g, G - h * yy - 50 * g
            c.drawLine(x, G - h * (yy - 0.12), bx, by, P(INK, stroke=tw * 0.6 + 6))
            c.drawLine(x, G - h * (yy - 0.12), bx, by, P((120, 84, 58), stroke=tw * 0.6))
    # foliage: from two leaves to a full crown
    if g < 0.25:
        for side in (-1, 1):
            c.save(); c.translate(x, G - h + 6); c.rotate(-35 * side)
            leaf = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(0 if side > 0 else -34, -10, 34, 20), 10, 10)
            c.drawRRect(leaf, P(INK, stroke=6)); c.drawRRect(leaf, P((120, 200, 110))); c.restore()
        return
    rng = np.random.default_rng(5)
    crown = [(x + rng.uniform(-1, 1) * 120 * g, G - h - rng.uniform(-40, 80) * g, (50 + rng.uniform(0, 40)) * g) for _ in range(8)]
    for cx, cy, r in crown: c.drawCircle(cx, cy, r + 4, P(INK))
    for i, (cx, cy, r) in enumerate(crown):
        c.drawCircle(cx, cy, r, P(lerpc((110, 190, 100), (150, 215, 120), (i % 3) / 2)))
    if b > 0:  # blossoms burst open
        for i in range(60):
            cx, cy, r = crown[i % 8]; a = i * 2.4
            px, py = cx + math.cos(a) * r * 0.75 * ((i * 37) % 10) / 10, cy + math.sin(a) * r * 0.75 * ((i * 53) % 10) / 10
            rr = 9 * b * (0.7 + 0.3 * math.sin(i))
            c.drawCircle(px, py, rr, P((255, 200, 220), 0.95))
            c.drawCircle(px, py, rr * 0.35, P((255, 235, 150)))


def mound(c, x, k_holes=0, dug=0.0):
    """dirt patch; more holes and scattered dirt for Impatience"""
    c.drawOval(skia.Rect.MakeXYWH(x - 70, G - 12, 140, 26), P((92, 64, 44)))
    c.drawOval(skia.Rect.MakeXYWH(x - 70, G - 12, 140, 26), P(INK, stroke=4))
    for i in range(k_holes):
        hx = x - 40 + i * 40
        c.drawOval(skia.Rect.MakeXYWH(hx - 16, G - 6, 32, 12), P((40, 28, 22)))
    if dug > 0:
        for i in range(10):
            a = i * 0.63; r = 40 + 90 * dug
            c.drawCircle(x + math.cos(a) * r * 0.9, G - 10 - abs(math.sin(a)) * 60 * math.sin(math.pi * dug), 6, P((92, 64, 44)))


def world(c, t):
    dl = light(t)
    top, mid, hor = sky_cols(dl)
    if t > LAPSE[1]:  # golden morning after the lapse
        k = seg(t, LAPSE[1], TURN + 0.8)
        top, mid, hor = lerpc(top, (120, 170, 230), k), lerpc(mid, (255, 205, 150), k), lerpc(hor, (255, 225, 160), k)
    sky(c, t, top, mid, hor, G, stars=clamp(1 - dl * 2))
    ph = day_phase(t)
    # sun and moon travel in an arc (time-lapse)
    sa = 2 * math.pi * (ph - 0.25)
    sx, sy = 540 + 520 * math.cos(sa + math.pi / 2) * -1, G - 200 - 620 * math.cos(2 * math.pi * ph)
    sun(c, sx, sy, clamp(dl * 1.6), r=70)
    moon(c, 1080 - sx, G - 200 + 620 * math.cos(2 * math.pi * ph), clamp(1 - dl * 1.8))
    hills(c, G, lerpc((40, 60, 80), (120, 170, 120), dl), amp=30, off=0.5, a=0.95, height=170)
    haze(c, G, lerpc((40, 50, 90), (255, 235, 210), dl), 0.35)
    hills(c, G, lerpc((30, 50, 50), (90, 150, 90), dl), amp=24, off=2.4, a=1.0, height=80)
    ground(c, G, lerpc((40, 70, 50), (110, 175, 95), dl), lerpc((14, 24, 20), (40, 80, 45), dl), lerpc((60, 80, 70), (200, 240, 170), dl))
    tufts(c, G, lerpc((20, 40, 30), (70, 130, 70), dl), seed=4, n=34)
    return dl


def petals(c, t):
    if t < TURN: return
    rng = np.random.default_rng(12)
    for i in range(40):
        x0 = rng.uniform(80, 700); sp = rng.uniform(60, 120); ph = rng.uniform(0, 6.3); st = rng.uniform(0, 2.5)
        tt = t - TURN - st
        if tt < 0: continue
        y = G - 420 + tt * sp
        if y > G + 30: continue
        x = x0 + tt * 40 + math.sin(tt * 2 + ph) * 30
        c.save(); c.translate(x, y); c.rotate(math.degrees(tt * 3 + ph))
        c.drawOval(skia.Rect.MakeXYWH(-8, -5, 16, 10), P((255, 205, 225), 0.9)); c.restore()


def watering(c, J, t):
    hx, hy = J["hand_f"]
    can = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(hx - 6, hy - 6, 46, 34), 8, 8)
    c.drawRRect(can, P(INK, stroke=6)); c.drawRRect(can, P((90, 150, 210)))
    c.drawLine(hx + 38, hy + 2, hx + 66, hy - 12, P(INK, stroke=9)); c.drawLine(hx + 38, hy + 2, hx + 66, hy - 12, P((90, 150, 210), stroke=4))
    for i in range(6):  # droplets
        k = (t * 3 + i / 6) % 1
        c.drawCircle(hx + 66 + k * 40, hy - 12 + k * k * 160, 4, P((150, 200, 255), 0.9 * (1 - k)))


def frame(c, t):
    c.save(); c.translate(540, G); c.scale(1.45, 1.45); c.translate(-540, -G)
    dl = world(c, t)
    rim_col = lerpc((150, 170, 255), (255, 210, 140), dl)
    body = lerpc((205, 210, 230), (250, 250, 246), dl)
    # Patience: plant + tree
    mound(c, XP + 60)
    tree(c, XP + 60, t)
    p = patience(t)
    shadow(c, p["x"], G, S)
    jp = figure(c, p["x"], G - (0 if not p.get("sit") else 0), p["p"], s=S, facing=p["f"], body=body, rim=(rim_col, 0.55),
                mode="feet")
    if p.get("can"): watering(c, jp, t)
    plate_label(c, "PATIENCE", jp["head"][0], jp["head"][1] - 52, AMBER, 0.95)
    # Impatience: keeps digging
    im = impatience(t)
    holes = sum(1 for d, _ in DIGS if t > d + 1.0)
    dug = 0.0
    for d, _ in DIGS:
        if d < t < d + 0.6: dug = (t - d) / 0.6
    mound(c, XI - 40, holes, dug)
    shadow(c, im["x"], G, S)
    ji = figure(c, im["x"], G, im["p"], s=S, facing=im["f"], body=body, rim=(rim_col, 0.45))
    plate_label(c, "IMPATIENCE", ji["head"][0], ji["head"][1] - 52, GREY, 0.9)
    for d, txt in DIGS:
        if d + 0.1 < t < d + 1.5:
            a = seg(t, d + 0.1, d + 0.25) * (1 - seg(t, d + 1.25, d + 1.5))
            bubble(c, min(ji["head"][0] - 40, 640), ji["head"][1] - 150, txt, a, "speech", tail=(ji["head"][0], ji["head"][1] - 40),
                   size=34, pop=1 + 0.15 * (1 - seg(t, d + 0.1, d + 0.3)))
    if TURN + 0.5 < t < TURN + 2.2:
        a = seg(t, TURN + 0.5, TURN + 0.7) * (1 - seg(t, TURN + 1.9, TURN + 2.2))
        bubble(c, min(ji["head"][0] - 40, 640), ji["head"][1] - 150, "…wait, what?", a, "think", tail=(ji["head"][0], ji["head"][1] - 40), size=34)
    petals(c, t)
    c.restore()
    if bloom(t) > 0:  # warm light burst at the turn
        c.drawRect(skia.Rect.MakeWH(W, H), P((255, 220, 160), 0.18 * math.sin(math.pi * clamp((t - TURN) / 1.2))))
    vignette(c, 0.42)
    grain(c, t, 0.035)
    end_text(c, t, 14.4, "Nothing grows", "if you keep digging it up.", "Plant. Wait. Trust.", y=1430)


def events():
    ev = [["thud", 0.5], ["thud", 0.55], ["splash", 1.9]]
    for d, _ in DIGS:
        ev += [["slide", d], ["pop", d + 0.1], ["splash", d - 0.3]]
    ev += [["pop", TURN + 0.5], ["sunrise", TURN - 1.6], ["summit", TURN], ["text", 14.4], ["text2", 15.2]]
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still":
        stills(frame, [0.4, 3.6, 6.6, 9.6, 12.4, 15.0], "check/ep8")
    else:
        finish_v2("Folge8_Patience", frame, T_END, events(), TURN, 8, "Do you want results NOW?", 0.3, 16.0)
