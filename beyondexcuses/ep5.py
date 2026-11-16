"""Folge 5: NEID vs. ZUFRIEDENHEIT – zwei Gärten, ein Zaun. Morgen -> goldener Abend."""
import sys, math
import numpy as np
from lib import *

T_END = 18.8
G = 1200
S = 0.92
FENCE = 540
LEFT = [70, 160, 250, 340, 430]
RIGHT = [650, 740, 830, 920, 1010]
NEIDG = (150, 225, 140)
BUBBLES = [(2.6, "Warum er?", 280, 820), (4.6, "Unfair.", 170, 720), (6.6, "Das will ich auch.", 300, 620),
           (8.6, "Seiner ist besser.", 200, 520), (10.4, "Wieso nicht ich?", 320, 420)]


def day(t): return ease((t - 4.0) / 11.0)   # morning -> golden evening


def plant(c, x, h, health, bloom, t, seed, u):
    """h: height px, health 1 green/upright -> 0 brown/drooping, bloom 0..1 flower size"""
    rng = np.random.default_rng(seed)
    droop = (1 - health) * 70
    stem = lerpc((70, 150, 70), (130, 100, 60), 1 - health)
    sway = math.sin(t * 1.5 + seed) * 3 * health
    tip = (x + sway + droop * 0.9, G - h + droop * 0.6)
    p = skia.Path(); p.moveTo(x, G); p.quadTo(x + sway, G - h * 0.6, *tip)
    c.drawPath(p, P(INK, stroke=10)); c.drawPath(p, P(stem, stroke=5))
    for k in (0.35, 0.6):
        ly = G - h * k; lx = x + sway * k
        for d in (-1, 1):
            lf = skia.Path(); lf.moveTo(lx, ly)
            lf.quadTo(lx + d * 26, ly - 18 + droop * 0.4, lx + d * 40, ly + droop * 0.5)
            lf.quadTo(lx + d * 20, ly + 4, lx, ly)
            c.drawPath(lf, P(lerpc((90, 180, 80), (150, 120, 70), 1 - health))); c.drawPath(lf, P(INK, stroke=3))
    if bloom > 0.05:
        col = [(255, 120, 140), (255, 200, 80), (160, 140, 255), (255, 150, 90), (255, 255, 255)][seed % 5]
        col = lerpc(col, (140, 110, 80), 1 - health)
        r = 9 + 15 * bloom
        for k in range(6):
            a = k / 6 * 6.283 + seed
            px, py = tip[0] + math.cos(a) * r * 0.9, tip[1] + math.sin(a) * r * 0.9
            c.drawCircle(px, py, r * 0.62, P(INK)); c.drawCircle(px, py, r * 0.62 - 3, P(col))
        c.drawCircle(*tip, r * 0.5, P(INK)); c.drawCircle(*tip, r * 0.5 - 3, P((255, 220, 90)))


def neid(t):
    if t < 1.5: return dict(x=430, p=stand(), f=1)
    if t < 12.6:
        b = math.sin(t * 1.2) * 3
        return dict(x=455, p=dict(lean=22 + b, head=-6, arm_f=78, elb_f=-14, arm_b=70, elb_b=-8, leg_f=6, leg_b=-8), f=1)
    if t < 13.4:  # turns around to his own garden
        return dict(x=455, p=stand(), f=-1)
    k = seg(t, 13.4, 14.4)
    return dict(x=455, p=mix(dict(stand(), head=20), slump(), k), f=-1)


def zufrieden(t):
    """walks between his plants watering; then crouches to smell a flower; then sits"""
    route = [(1.0, 630), (3.0, 630), (4.0, 720), (6.0, 720), (7.0, 810), (9.0, 810), (10.0, 880), (11.6, 880)]
    if t < route[0][0]: return dict(x=640, p=stand(), f=1, can=True)
    for (t0, x0), (t1, x1) in zip(route, route[1:]):
        if t0 <= t < t1:
            if x0 == x1:  # watering
                p = dict(lean=10, head=12, arm_f=62, elb_f=-10, arm_b=-10, elb_b=10, leg_f=4, leg_b=-4)
                return dict(x=x0, p=p, f=1, can=True, pour=True)
            u = (t - t0) / (t1 - t0)
            return dict(x=lerp(x0, x1, u), p=walk(t * 8), f=1, can=True)
    if t < 13.0:
        return dict(x=880, p=mix(stand(), crouch(), seg(t, 11.6, 12.3)), f=-1)
    k = seg(t, 13.0, 13.8)
    sitg = dict(lean=8, head=-22, arm_f=70, elb_f=25, arm_b=60, elb_b=25, leg_f=120, knee_f=110, leg_b=112, knee_b=105)
    return dict(x=830, p=mix(crouch(), sitg, k), f=1, sit=k > 0.5)


def world(c, t):
    u = day(t)
    sky(c, t, lerpc((120, 180, 235), (110, 90, 150), u), lerpc((180, 220, 245), (250, 160, 110), u), lerpc((235, 245, 230), (255, 210, 140), u), G)
    sun(c, lerp(200, 860, seg(t, 0, 16)), lerp(520, 900, seg(t, 4, 16)), 1.0, r=70)
    hills(c, G, lerpc((140, 190, 130), (170, 120, 100), u), amp=30, off=1.2, height=110)
    hills(c, G, lerpc((110, 170, 110), (140, 100, 90), u), amp=22, off=3.1, height=55)
    # two gardens: left browns over time, right gets greener
    dead = seg(t, 3, 14)
    gl = lerpc(lerpc((96, 150, 80), (150, 110, 60), dead), (120, 80, 60), u * 0.3)
    gr = lerpc(lerpc((96, 150, 80), (80, 170, 80), seg(t, 2, 10)), (150, 120, 70), u * 0.3)
    c.drawRect(skia.Rect.MakeLTRB(-300, G, FENCE, H + 300), P(gl))
    c.drawRect(skia.Rect.MakeLTRB(FENCE, G, W + 300, H + 300), P(gr))
    c.drawRect(skia.Rect.MakeLTRB(-300, G + 60, W + 300, H + 300), P((0, 0, 0), 0.25))
    c.drawLine(-300, G, W + 300, G, P(INK, stroke=4))
    # plants
    for i, x in enumerate(LEFT):
        health = 1 - seg(t, 2.5 + i * 0.6, 12 + i * 0.4)
        plant(c, x, lerp(150, 110, 1 - health), health, lerp(0.8, 0.3, 1 - health), t, i, u)
    for i, x in enumerate(RIGHT):
        grow = seg(t, 1.5 + i * 1.6, 5.5 + i * 1.8)
        plant(c, x, lerp(50, 190, grow), 1, grow, t, i + 7, u)
    # fence
    wood = lerpc((235, 230, 215), (240, 200, 160), u)
    for x in range(FENCE - 6, FENCE + 7, 1): pass
    c.drawLine(FENCE - 70, G - 85, FENCE + 70, G - 85, P(INK, stroke=16)); c.drawLine(FENCE - 70, G - 85, FENCE + 70, G - 85, P(wood, stroke=9))
    c.drawLine(FENCE - 70, G - 40, FENCE + 70, G - 40, P(INK, stroke=16)); c.drawLine(FENCE - 70, G - 40, FENCE + 70, G - 40, P(wood, stroke=9))
    for x in (FENCE - 52, FENCE, FENCE + 52):
        pk = poly([(x - 14, G), (x - 14, G - 120), (x, G - 138), (x + 14, G - 120), (x + 14, G)])
        c.drawPath(pk, P(wood)); c.drawPath(pk, P(INK, stroke=5))
    return u


def frame(c, t):
    c.save(); c.translate(540, G); c.scale(1.12, 1.12); c.translate(-540, -G)
    u = world(c, t)
    body = lerpc((248, 248, 244), (255, 236, 220), u)
    z = zufrieden(t)
    if z.get("sit"):
        jz = figure(c, z["x"], G - 20 * S, z["p"], s=S, facing=z["f"], body=body, mode="hip")
    else:
        jz = figure(c, z["x"], G, z["p"], s=S, facing=z["f"], body=body)
    label(c, "ZUFRIEDENHEIT", jz["head"][0], jz["head"][1] - 50, AMBER, 0.95)
    if z.get("can"):
        hx, hy = jz["hand_f"]
        can = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(hx - 18, hy - 6, 50, 36), 8, 8)
        c.drawRRect(can, P((90, 150, 210))); c.drawRRect(can, P(INK, stroke=4))
        c.drawLine(hx + 30, hy + 4, hx + 62, hy - 14, P(INK, stroke=8)); c.drawLine(hx + 30, hy + 4, hx + 62, hy - 14, P((90, 150, 210), stroke=4))
        if z.get("pour"):
            for k in range(7):
                ph = (t * 2.2 + k / 7) % 1.0
                c.drawCircle(hx + 64 + ph * 30, hy - 12 + ph * ph * 150, 4, P((140, 200, 255), 0.9 * (1 - ph)))
    n = neid(t)
    nb = lerpc(body, NEIDG, seg(t, 2.0, 12.0) * 0.75)
    jn = figure(c, n["x"], G, n["p"], s=S, facing=n["f"], body=nb)
    label(c, "NEID", jn["head"][0], jn["head"][1] - 50, NEIDG, 0.95)
    hx, hy = jn["head"]
    for t0, s, bx, by in BUBBLES:
        if t > t0:
            pop = ease((t - t0) / 0.18)
            a = pop * (1 - seg(t, 12.6, 13.2))
            c.save(); c.translate(bx, by); c.scale(0.6 + 0.4 * pop, 0.6 + 0.4 * pop)
            bubble(c, 0, 0, s, a, "think", tail=(hx - bx, hy - 40 - by) if by > 800 else None, size=28, col=(232, 250, 228))
            c.restore()
    if 13.6 < t < 15.4:
        bubble(c, 250, 860, "Mein Garten…?", seg(t, 13.6, 13.8) * (1 - seg(t, 15.1, 15.4)), "think", tail=(hx, hy - 40), size=30)
    c.restore()
    vignette(c, 0.45)
    end_text(c, t, 15.6, "Wer nur über den Zaun schaut,", "gießt nie den eigenen Garten.", "Kümmer dich um deins.", y=1460)
    if t > T_END - 0.5: c.drawRect(skia.Rect.MakeWH(W, H), P((0, 0, 0), (t - (T_END - 0.5)) / 0.5))


def events():
    ev = [["pop", b[0]] for b in BUBBLES] + [["pop", 13.6], ["summit", 12.3], ["text", 15.6], ["text2", 16.4]]
    for t0 in (1.0, 4.0, 7.0, 10.0):
        ev.append(["splash", t0 + 0.4])
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still": stills(frame, [1.2, 3.5, 7.0, 10.5, 14.2, 17.5], "/home/claude/mind/ep5")
    else: finish_v2("Folge5_Neid", frame, T_END, events(), 10.0, 5, "Schaust du auch ständig rüber?", 1.0, 17.0)
