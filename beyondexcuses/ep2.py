"""Folge 2: OVERTHINKER vs. MACHER – Fluss mit Trittsteinen, Sonnenuntergang -> Nacht."""
import sys, math
import numpy as np
from lib import *

T_END = 18.6
G = 1250              # bank height
WATER = 1268
S = 0.95
STONES = [400, 492, 584, 680]
BANK_L, BANK_R = 330, 770
JUMPS = [(300, 400, 1.9), (400, 492, 2.7), (492, 584, 4.5), (584, 680, 5.3), (680, 820, 6.1)]
JD = 0.45
FIRE = (930, G)
BUBBLES = [(2.2, "Was, wenn ich ausrutsche?", 300, 930), (3.6, "Ist das Wasser tief?", 200, 830),
           (5.0, "Was denken die anderen?", 320, 730), (6.4, "Vielleicht morgen…", 190, 640),
           (7.8, "Was, wenn…", 360, 560), (8.8, "Und wenn…?", 170, 480), (9.6, "Bin ich bereit?", 330, 400),
           (10.4, "Zu riskant.", 200, 320), (11.1, "Was, wenn…", 380, 250)]


def night(t): return ease((t - 3.0) / 9.0)


def macher(t):
    if t < 1.5: return dict(x=130, y=G, p=stand(), f=1)
    if t < JUMPS[0][2]:
        u = seg(t, 1.5, JUMPS[0][2]); return dict(x=lerp(130, 300, u), y=G, p=walk(t * 9), f=1, walk=True)
    for i, (a, b, t0) in enumerate(JUMPS):
        if t0 - 0.25 <= t < t0:
            return dict(x=a, y=G, p=crouch(), f=1)
        if t0 <= t < t0 + JD:
            u = (t - t0) / JD
            return dict(x=lerp(a, b, u), y=G - 120 * math.sin(math.pi * u), p=airborne(), f=1)
        nxt = JUMPS[i + 1][2] if i + 1 < len(JUMPS) else 99
        if t0 + JD <= t < nxt - 0.25:
            if i == 1 and t < 4.3:  # wobble on stone 2
                w = math.sin((t - t0) * 14) * 18 * (1 - seg(t, 3.2, 4.3))
                p = dict(lean=w * 0.7, head=-w * 0.5, arm_f=100 + w * 2, elb_f=10, arm_b=-100 + w * 2, elb_b=10, leg_f=6, leg_b=-6)
                return dict(x=b, y=G, p=p, f=1, rot=w * 0.3)
            if i == len(JUMPS) - 1:
                break
            return dict(x=b, y=G, p=stand(), f=1)
    if t < 8.3:
        u = seg(t, 6.8, 8.3); return dict(x=lerp(820, 860, u), y=G, p=walk(t * 9) if t > 6.8 else stand(), f=1, walk=t > 6.8)
    k = seg(t, 8.3, 8.9)
    p = mix(stand(), sit(t), k)
    p["arm_f"] = lerp(p["arm_f"], 70, k); p["elb_f"] = lerp(p["elb_f"], -20, k)  # hands to the fire
    return dict(x=860, y=G - 34 * k, p=p, f=1, hipmode=k > 0.5)


def overthinker(t):
    if t < 1.5: return dict(x=240, p=stand(), f=1)
    if t < 7.0: return dict(x=240, p=think(t), f=1)
    if t < 11.0:  # pacing
        ph = (t - 7.0) / 4.0
        x = 240 - 70 * math.sin(math.pi * ph)
        f = -1 if ph < 0.5 else 1
        return dict(x=x, p=walk(t * 8, lean=4, stride=16), f=f, walk=True)
    if t < 12.3:  # steps to the edge, hesitates
        u = seg(t, 11.0, 11.8); return dict(x=lerp(240, 300, u), p=walk(t * 8) if t < 11.8 else think(t), f=1, walk=t < 11.8)
    if t < 13.3:
        u = seg(t, 12.3, 13.1); return dict(x=lerp(300, 230, u), p=walk(-t * 8, stride=14), f=1, walk=True)
    k = seg(t, 13.3, 14.0)
    hug = dict(lean=35, head=25, arm_f=95, elb_f=40, arm_b=85, elb_b=40, leg_f=125, knee_f=125, leg_b=118, knee_b=120)
    return dict(x=230, p=mix(stand(), hug, k), f=1, sitk=k)


def draw_fire(c, t, glow):
    x, y = FIRE
    c.drawCircle(x, y - 40, 260, P((255, 150, 60), 0.22 * glow, blur=90))
    for dx in (-30, 30):
        lg = poly([(x - 48, y - 4 + (dx > 0) * -10), (x + 48, y - 18 + (dx > 0) * 14)], close=False)
        c.drawPath(lg, P(INK, stroke=22)); c.drawPath(lg, P((120, 76, 50), stroke=14))
    rng = np.random.default_rng(int(t * 12))
    for k, (col, sc) in enumerate((((255, 120, 40), 1.0), ((255, 190, 70), 0.68), ((255, 240, 180), 0.38))):
        h = (70 + rng.uniform(-8, 8)) * sc; w = 34 * sc
        fl = skia.Path(); fl.moveTo(x - w, y - 14); fl.quadTo(x - w * 0.9, y - 14 - h * 0.6, x + rng.uniform(-6, 6), y - 14 - h)
        fl.quadTo(x + w * 0.9, y - 14 - h * 0.6, x + w, y - 14); fl.close()
        if k == 0: c.drawPath(fl, P(INK, stroke=6))
        c.drawPath(fl, P(col))
    # log seat
    seat = poly([(820, G - 30), (900, G - 30)], close=False)
    c.drawPath(seat, P(INK, stroke=30)); c.drawPath(seat, P((110, 72, 48), stroke=22))


def world(c, t):
    u = night(t)
    sky(c, t, lerpc((60, 40, 80), (8, 12, 30), u), lerpc((220, 110, 90), (24, 36, 74), u), lerpc((255, 180, 110), (44, 66, 110), u), G, stars=u)
    sun(c, 820, lerp(1050, 1330, seg(t, 0, 5)), 1 - seg(t, 2, 5.5), r=70)
    moon(c, 840, lerp(560, 330, seg(t, 6, 14)), seg(t, 6, 9))
    hills(c, G, lerpc((150, 80, 90), (22, 32, 62), u), off=2.0)
    hills(c, G, lerpc((110, 60, 75), (16, 24, 48), u), amp=30, off=4.0, height=70)
    g1 = lerpc((110, 80, 70), (26, 38, 60), u); g2 = lerpc((40, 26, 30), (10, 14, 24), u)
    ground(c, G, g1, g2, lerpc((255, 190, 140), (90, 120, 170), u))
    # river cut into the ground
    wc1 = lerpc((210, 120, 100), (30, 52, 96), u); wc2 = lerpc((90, 50, 70), (8, 14, 30), u)
    sh = skia.GradientShader.MakeLinear([(0, WATER), (0, 1560)], [C(wc1), C(wc2)])
    river = poly([(BANK_L, G), (BANK_R, G), (BANK_R - 30, 1560), (BANK_L + 30, 1560)])
    c.drawPath(poly([(BANK_L - 12, G), (BANK_R + 12, G), (BANK_R - 22, 1560), (BANK_L + 22, 1560)]), P(INK))
    c.drawPath(river, P(lerpc((60, 40, 50), (12, 18, 34), u)))
    c.drawRect(skia.Rect.MakeLTRB(BANK_L + 6, WATER, BANK_R - 6, 1560), skia.Paint(Shader=sh))
    for k in range(7):
        y = WATER + 14 + k * 38; ph = t * 1.6 + k
        wp = skia.Path(); wp.moveTo(BANK_L + 20, y)
        for x in range(BANK_L + 20, BANK_R - 19, 20): wp.lineTo(x, y + 4 * math.sin(x * 0.05 + ph))
        c.drawPath(wp, P((255, 255, 255), 0.18 - k * 0.02, stroke=3))
    # stones
    for x in STONES:
        st = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 36, G - 6, 72, 34), 16, 16)
        c.drawRRect(st, P(lerpc((140, 120, 120), (80, 90, 110), u))); c.drawRRect(st, P(INK, stroke=5))
    draw_fire(c, t, 0.5 + 0.5 * u)
    return u


def frame(c, t):
    u = world(c, t)
    body = lerpc((255, 240, 228), (238, 240, 246), u)
    m = macher(t)
    warm = lerpc(body, (255, 214, 170), seg(t, 8.3, 9.5))
    if m.get("hipmode"):
        jm = figure(c, m["x"], m["y"], m["p"], s=S, facing=m["f"], body=warm, mode="hip")
    else:
        jm = figure(c, m["x"], m["y"], m["p"], s=S, facing=m["f"], rot=m.get("rot", 0), body=warm)
    label(c, "MACHER", jm["head"][0], jm["head"][1] - 50, AMBER, 0.95)
    o = overthinker(t)
    dark = lerpc(body, (170, 176, 196), seg(t, 12, 15))
    if o.get("sitk", 0) > 0.5:
        jo = figure(c, o["x"], G - 18 * S, o["p"], s=S, facing=o["f"], body=dark, mode="hip")
    else:
        jo = figure(c, o["x"], G, o["p"], s=S, facing=o["f"], body=dark)
    label(c, "OVERTHINKER", jo["head"][0], jo["head"][1] - 50, GREY, 0.85)
    # thought bubbles pile up
    hx, hy = jo["head"]
    for t0, s, bx, by in BUBBLES:
        if t > t0:
            pop = ease((t - t0) / 0.18); a = pop * (1 - 0.35 * seg(t, 12, 15))
            jitter = math.sin(t * 3 + bx) * 4
            c.save(); c.translate(bx + jitter, by); c.scale(0.6 + 0.4 * pop, 0.6 + 0.4 * pop)
            bubble(c, 0, 0, s, a, "think", tail=(hx - bx, hy - 30 - by) if by > 700 else None, size=28)
            c.restore()
    vignette(c)
    end_text(c, t, 15.3, "Du musst nicht", "alles durchdenken.", "Nur den nächsten Schritt.")
    if t > T_END - 0.5: c.drawRect(skia.Rect.MakeWH(W, H), P((0, 0, 0), (t - (T_END - 0.5)) / 0.5))


def events():
    ev = []
    for a, b, t0 in JUMPS: ev += [["jump", t0], ["land", t0 + JD]]
    ev += [["pop", t0] for t0, *_ in BUBBLES]
    last = None
    for f in range(int(T_END * FPS)):
        t = f / FPS
        for who in (macher(t), overthinker(t)):
            pass
    ev += [["summit", 8.6], ["text", 15.3], ["text2", 16.1]]
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still": stills(frame, [1.0, 3.5, 6.3, 9.0, 13.0, 16.8], "/home/claude/mind/ep2")
    else: finish_v2("Folge2_Overthinker", frame, T_END, events(), 8.6, 2, "Denkst du auch zu viel nach?", 1.2, 16.7)
