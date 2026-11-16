"""Folge 3: EGO vs. DEMUT – zwei in einer Wüstengrube, ein Fremder wirft ein Seil."""
import sys, math
import numpy as np
from lib import *

T_END = 18.8
G = 980          # desert surface
FLOOR = 1430     # pit floor
PL, PR = 250, 830          # pit top edges
FL, FR = 310, 770          # pit floor edges
S = 0.9
ROPE1, ROPE2 = 700, 450


def eve(t): return ease((t - 6.0) / 9.0)   # day -> dusk/night


def helper(t):
    if t < 1.5: return dict(x=1250, p=stand(), f=-1)
    if t < 3.0: return dict(x=lerp(1250, 760, seg(t, 1.5, 3.0)), p=walk(t * 9), f=-1, walk=True)
    if t < 8.4:
        k = seg(t, 3.0, 3.4); return dict(x=760, p=mix(stand(), dict(lean=40, head=10, arm_f=70, elb_f=20, arm_b=60, elb_b=10, leg_f=40, leg_b=-20, knee_f=70, knee_b=10), k), f=-1)
    if t < 9.2: return dict(x=lerp(760, 520, seg(t, 8.4, 9.2)), p=walk(t * 9), f=-1, walk=True)
    if t < 11.6: return dict(x=520, p=dict(lean=40, head=10, arm_f=70, elb_f=20, arm_b=60, elb_b=10, leg_f=40, leg_b=-20, knee_f=70, knee_b=10), f=-1)
    if t < 12.2: return dict(x=520, p=stand(), f=1)
    return dict(x=lerp(520, 1300, seg(t, 12.2, 15.5)), p=walk(t * 8), f=1, walk=True)


def rope(t):
    """returns (x, top_y, bottom_y) or None"""
    if 3.2 < t < 8.4:
        return (ROPE1, G - 40, lerp(G - 40, 1330, seg(t, 3.2, 3.9)) if t < 7.5 else lerp(1330, G - 40, seg(t, 7.5, 8.2)))
    if 9.2 < t < 11.6:
        b = lerp(G - 40, 1330, seg(t, 9.2, 9.8)) if t < 10.9 else lerp(1330, G - 40, seg(t, 10.9, 11.6))
        return (ROPE2, G - 40, b)
    return None


def demut(t):
    if t < 4.0: return dict(x=640, y=FLOOR, p=stand() if t < 1.0 else mix(stand(), dict(lean=-6, head=-30), seg(t, 1.0, 1.4)), f=1)
    if t < 4.5: return dict(x=lerp(640, ROPE1 - 6, seg(t, 4.0, 4.5)), y=FLOOR, p=walk(t * 9), f=1)
    if t < 7.4:
        u = seg(t, 4.5, 7.4)
        return dict(x=ROPE1 - 6, y=lerp(FLOOR - 120, G - 60, u), p=climb_rope(t * 7), f=1, hip=True)
    if t < 8.1:  # climbs over the edge
        u = seg(t, 7.4, 8.1)
        return dict(x=lerp(ROPE1 - 6, 820, u), y=G, p=mix(crouch(), stand(), u), f=1)
    if t < 9.0: return dict(x=820, y=G, p=stand(), f=-1)
    if t < 9.6: return dict(x=lerp(820, 600, seg(t, 9.0, 9.6)), y=G, p=walk(t * 9), f=-1)
    if t < 11.8:
        k = math.sin(t * 5) * 10  # waving him up
        return dict(x=600, y=G, p=dict(lean=20, head=10, arm_f=110 + k, elb_f=10, arm_b=20, elb_b=10, leg_f=6, leg_b=-6), f=-1)
    if t < 12.2: return dict(x=600, y=G, p=stand(), f=1)
    return dict(x=lerp(600, 1350, seg(t, 12.2, 15.6)), y=G, p=walk(t * 8), f=1)


def ego(t):
    if t < 1.0: return dict(x=400, y=FLOOR, p=stand(), f=1)
    if t < 9.8: return dict(x=400, y=FLOOR, p=arms_crossed(head=-20 if t > 3.5 else 0), f=1)
    if t < 10.4:  # slaps the rope away
        k = math.sin(seg(t, 9.8, 10.4) * math.pi)
        return dict(x=400, y=FLOOR, p=dict(lean=-6, head=-15, arm_f=40 + 120 * k, elb_f=-20, arm_b=30, elb_b=-110, leg_f=8, leg_b=-8), f=1)
    if t < 11.6: return dict(x=400, y=FLOOR, p=arms_crossed(head=-25), f=1)
    if t < 12.1: return dict(x=lerp(400, 330, seg(t, 11.6, 12.1)), y=FLOOR, p=walk(-t * 9), f=-1)
    if t < 14.4:  # tries to climb the wall alone, slides down twice
        ph = (t - 12.1) / 1.15; k = ph % 1.0
        up = math.sin(min(k, 0.6) / 0.6 * math.pi / 2) if k < 0.6 else 1 - (k - 0.6) / 0.4
        y = lerp(FLOOR - 70, FLOOR - 190, up)
        return dict(x=325, y=y, p=climb_rope(t * 9), f=-1, hip=True, rot=12)
    k = seg(t, 14.4, 15.0)
    hug = dict(lean=35, head=25, arm_f=95, elb_f=40, arm_b=85, elb_b=40, leg_f=125, knee_f=125, leg_b=118, knee_b=120)
    return dict(x=420, y=FLOOR - 16, p=mix(stand(), hug, k), f=1, hip=k > 0.5) if k > 0.5 else dict(x=420, y=FLOOR, p=mix(stand(), hug, k), f=1)


def world(c, t):
    u = eve(t)
    sky(c, t, lerpc((80, 140, 210), (16, 18, 44), u), lerpc((150, 196, 230), (120, 60, 80), u), lerpc((240, 220, 180), (250, 140, 80), u), G, stars=seg(t, 13, 16))
    sun(c, lerp(300, 880, seg(t, 0, 15)), lerp(320, 960, seg(t, 3, 15.5)), 1.0, r=72)
    # dunes
    hills(c, G, lerpc((226, 190, 140), (150, 80, 70), u), amp=26, off=0.6, height=120)
    hills(c, G, lerpc((214, 172, 120), (120, 64, 60), u), amp=20, off=2.6, height=60)
    sand = lerpc((228, 190, 136), (140, 82, 66), u)
    ground(c, G, sand, lerpc((180, 140, 96), (60, 34, 34), u), lerpc((255, 240, 210), (255, 180, 130), u))
    # pit
    pit_outline = poly([(PL, G), (PR, G), (FR, FLOOR + 30), (FL, FLOOR + 30)])
    c.drawPath(pit_outline, P(INK, stroke=10))
    inner = lerpc((176, 136, 92), (70, 40, 40), u)
    sh = skia.GradientShader.MakeLinear([(0, G), (0, FLOOR)], [C(lerpc(inner, (60, 40, 30), 0.35)), C(inner)])
    c.drawPath(pit_outline, skia.Paint(Shader=sh, AntiAlias=True))
    c.drawRect(skia.Rect.MakeLTRB(FL, FLOOR, FR, FLOOR + 28), P(lerpc(inner, (255, 255, 255), 0.08)))
    # sand streaks on walls
    for k in range(6):
        y = G + 60 + k * 70
        for side in (0, 1):
            x0 = lerp(PL, FL, (y - G) / (FLOOR - G)) if side == 0 else lerp(PR, FR, (y - G) / (FLOOR - G))
            dx = 1 if side == 0 else -1
            c.drawPath(poly([(x0 + dx * 10, y), (x0 + dx * 70, y + 10)], close=False), P(INK, 0.18, stroke=4))
    # shadow inside pit grows
    c.drawPath(pit_outline, P((10, 6, 20), 0.15 + 0.45 * u))
    return u


def frame(c, t):
    u = world(c, t)
    body = lerpc((248, 248, 244), (255, 226, 205), u)
    r = rope(t)
    if r:
        x, a, b = r
        sway = math.sin(t * 3) * 6 * (1 if t < 10 else 3 * (1 - seg(t, 10.0, 11.0)) + 1)
        rp = skia.Path(); rp.moveTo(x, a); rp.quadTo(x + sway, (a + b) / 2, x + sway * 1.6, b)
        c.drawPath(rp, P(INK, stroke=9)); c.drawPath(rp, P((200, 160, 100), stroke=5))
    for name, fn, col, lab in (("HILFE", helper, GREY, "HILFE"),):
        h = fn(t)
        jh = figure(c, h["x"], G, h["p"], s=S * 0.95, facing=h["f"], body=lerpc(body, (210, 214, 224), 0.4))
        label(c, lab, jh["head"][0], jh["head"][1] - 48, col, 0.8)
    d = demut(t)
    jd = figure(c, d["x"], d["y"], d["p"], s=S, facing=d["f"], body=body, mode="hip" if d.get("hip") else "feet")
    label(c, "DEMUT", jd["head"][0], jd["head"][1] - 48, AMBER, 0.95)
    e = ego(t)
    ecol = lerpc(body, (190, 186, 196), seg(t, 12, 15.5))
    je = figure(c, e["x"], e["y"], e["p"], s=S, facing=e["f"], rot=e.get("rot", 0), body=ecol, mode="hip" if e.get("hip") else "feet")
    label(c, "EGO", je["head"][0], je["head"][1] - 48, RED, 0.95)
    # dialogue
    if 4.0 < t < 6.4: bubble(c, 820, G - 330, "Halt dich fest!", seg(t, 4.0, 4.2) * (1 - seg(t, 6.0, 6.4)), "speech", tail=(780, G - 200), size=30)
    if 9.0 < t < 11.4:
        bubble(c, 640, G - 330, "Komm, nimm das Seil!", seg(t, 9.0, 9.2) * (1 - seg(t, 11.0, 11.4)), "speech", tail=(610, G - 200), size=30)
    if 9.5 < t < 12.4:
        bubble(c, 330, FLOOR - 330, "Ich brauche niemanden.", seg(t, 9.5, 9.7) * (1 - seg(t, 12.0, 12.4)), "speech", tail=(390, FLOOR - 200), size=30)
    vignette(c)
    end_text(c, t, 15.6, "Hilfe annehmen", "ist keine Schwäche.", "Stolz hält dich unten.", y=1540)
    if t > T_END - 0.5: c.drawRect(skia.Rect.MakeWH(W, H), P((0, 0, 0), (t - (T_END - 0.5)) / 0.5))


def events():
    ev = [["rope", 3.2], ["rope", 9.2], ["rope", 10.0], ["rope", 10.9], ["pop", 4.0], ["pop", 9.0], ["pop", 9.5],
          ["slide", 12.8], ["slide", 13.95], ["summit", 8.1], ["text", 15.6], ["text2", 16.4]]
    for k in range(int(4.5 * 7 / math.pi), int(7.4 * 7 / math.pi)):
        ev.append(["rope", k * math.pi / 7]) if k % 2 == 0 else None
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still": stills(frame, [1.2, 5.5, 8.6, 10.1, 13.0, 17.0], "/home/claude/mind/ep3")
    else: finish_v2("Folge3_Ego", frame, T_END, events(), 8.1, 3, "Würdest du das Seil nehmen?", 1.0, 17.0)
