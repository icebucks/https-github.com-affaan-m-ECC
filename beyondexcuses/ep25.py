"""Episode 25 (TikTok: Part 22): HOARDER OF IDEAS vs SHIPPER – promised by the Part 21 cliffhanger ("the one with 100 unfinished ideas").
A garage at night, a wall that fills up with sticky notes. Counters above them: IDEAS · DONE.
Hoarder (grey): starts a robot, a bike, a drone, … – "Ooh, a robot!", "Wait – better idea!" – "1 MONTH LATER": IDEAS 100 · DONE 0.
Shipper (amber): builds ONE desk lamp at her workbench – "One thing. Until it's done." – at the turn the lamp lights up and
her parcel gets the SHIPPED stamp: IDEAS 1 · DONE 1. """
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 22                     # TikTok part number (internal episode 25)
G = 1300
S = 1.3
SKIP0, SKIP1 = 6.0, 8.0        # "1 month later"
TURN = 9.8                     # lamp lights up + SHIPPED
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
ITEMS = [60, 170, 280]        # robot, bike, drone (x on the floor)
SX = 620                       # shipper stands right of her bench
BENCH = (430, 580)
BENCH_H = 120
LAMP = (475, G - BENCH_H)
BOX = (548, G - BENCH_H)
STARTS = [0.0, 1.4, 3.2, 4.8]  # he starts a new idea at these times
TALK = [(0.8, "h", "Ooh, a robot!"), (2.2, "s", "One thing. Until it's done."), (3.4, "h", "Wait - better idea!"),
        (SKIP1 + 0.3, "h", "I'll finish them... someday."), (TURN + 0.9, "s", "Done. Shipped.")]
HOOK = "100 ideas. 0 finished.\nShe finished just one."
FOCUS = (540, 1180)
COVER = False
CTA = "Part 23 next:\nthe one who saves $1 a day"


def ideas(t):
    if t >= SKIP0: return 100
    return sum(1 for s in STARTS if t >= s)


def h_target(t):
    """item he is working on"""
    if t >= SKIP0: return ITEMS[1]
    i = ideas(t) - 1
    return ITEMS[[0, 1, 2, 0][i]] + (0 if i < 3 else 40)


def h_x(t):
    if t >= SKIP0: return ITEMS[1] + 50
    for k, s in enumerate(STARTS[1:], 1):                                 # walk 0.5 s to the next item
        if s - 0.5 <= t < s:
            a = ITEMS[[0, 1, 2, 0][k - 1]] + (0 if k - 1 < 3 else 40); b = ITEMS[[0, 1, 2, 0][k]] + (0 if k < 3 else 40)
            return lerp(a + 50, b + 50, seg(t, s - 0.5, s))
    return h_target(t) + 50


# ------------------------------------------------------------------ characters
def hoarder(t):
    x = h_x(t)
    walking = any(s - 0.5 <= t < s for s in STARTS[1:]) and t < SKIP0
    if walking:
        prev = h_x(t - 0.05)
        return dict(x=x, p=walk(t * 9), f=1 if x >= prev else -1)
    if t >= SKIP0:                                                        # sits on a crate between half-finished things
        p = dict(sit(t), lean=24, head=24, arm_f=40, elb_f=120, arm_b=34, elb_b=120)
        if t > TURN + 1.2: p = mix(p, dict(p, head=-6, lean=4), seg(t, TURN + 1.2, TURN + 1.6))   # looks at her lamp
        return dict(x=x, p=p, f=1, hip=True)
    p = dict(crouch(), arm_f=60 + 25 * math.sin(t * 11), elb_f=30, arm_b=50, elb_b=30, head=-10)   # tinkers on the floor item
    return dict(x=x, p=p, f=-1)


def shipper(t):
    work = 0.6 < t < SKIP0 - 0.2 or SKIP1 < t < TURN
    p = dict(stand(), lean=16, head=14, arm_f=70 + (14 * math.sin(t * 8) if work else 0), elb_f=40, arm_b=60, elb_b=50)
    if TURN + 0.2 < t < TURN + 2.2: p = mix(p, cheer(t), seg(t, TURN + 0.2, TURN + 0.6) * (1 - seg(t, TURN + 1.6, TURN + 2.2)))
    return dict(x=SX, p=p, f=-1)


# ------------------------------------------------------------------ world
def robot(c, x, a=1.0):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 30, G - 70, 60, 70), 8, 8), P((150, 160, 175), a))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 30, G - 70, 60, 70), 8, 8), P(INK, a, stroke=3))
    for k in range(3): c.drawLine(x - 18 + k * 18, G - 70, x - 26 + k * 22, G - 92, P((200, 80, 70), a, stroke=2))   # loose wires, no head


def bike(c, x, a=1.0):
    c.drawCircle(x - 30, G - 26, 24, P(INK, a, stroke=5))
    c.drawPath(poly([(x - 30, G - 26), (x, G - 60), (x + 30, G - 26), (x - 6, G - 26)], close=True), P((60, 120, 180), a, stroke=6))   # one wheel missing


def drone(c, x, a=1.0):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 24, G - 34, 48, 24), 6, 6), P((80, 80, 90), a))
    for dx in (-44, 44): c.drawLine(x, G - 26, x + dx, G - 40, P(INK, a, stroke=4))
    c.drawOval(skia.Rect.MakeXYWH(x - 64, G - 46, 40, 10), P((120, 200, 230), a))          # only 1 of 2 propellers


def lamp(c, t):
    x, y = LAMP
    arm = seg(t, 1.0, SKIP0 - 0.4)                                        # the arm grows before the skip
    on = seg(t, TURN, TURN + 0.25)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 30, y - 14, 60, 14), 5, 5), P((60, 60, 70)))
    if arm > 0:
        ax, ay = x + 36 * arm, y - 14 - 110 * arm
        c.drawLine(x, y - 14, ax, ay, P((70, 70, 80), stroke=7))
        if t > SKIP1 + 0.4:                                               # shade goes on after the skip
            c.drawPath(poly([(ax - 10, ay - 6), (ax + 46, ay + 18), (ax + 30, ay + 40), (ax - 20, ay + 12)]), P(AMBER))
            c.drawPath(poly([(ax - 10, ay - 6), (ax + 46, ay + 18), (ax + 30, ay + 40), (ax - 20, ay + 12)]), P(INK, stroke=3))
            if on > 0:
                c.drawPath(poly([(ax + 6, ay + 30), (ax + 38, ay + 30), (ax + 80, y), (ax - 30, y)]), P((255, 230, 150), 0.35 * on))
                c.drawCircle(ax + 18, ay + 30, 70, P((255, 220, 140), 0.45 * on, blur=30))


def parcel(c, t):
    if t < TURN + 0.5: return
    x, y = BOX
    c.drawRect(skia.Rect.MakeXYWH(x - 30, y - 48, 60, 48), P((190, 150, 100))); c.drawRect(skia.Rect.MakeXYWH(x - 30, y - 48, 60, 48), P(INK, stroke=3))
    k = seg(t, TURN + 0.7, TURN + 0.9)
    if k > 0:
        c.save(); c.translate(x, y - 70); c.rotate(-12); sc = 1 + 0.6 * (1 - k); c.scale(sc, sc)
        c.drawRect(skia.Rect.MakeXYWH(-62, -21, 124, 42), P((250, 240, 230), 0.9)); c.drawRect(skia.Rect.MakeXYWH(-62, -21, 124, 42), P((220, 60, 50), stroke=4))
        text(c, "SHIPPED", 0, 12, F_CAP, 32, (220, 60, 50), 1.0)
        c.restore()


def notes(c, t):
    n = 3 + ideas(t) * 3 if t < SKIP0 else 30
    rng = np.random.default_rng(5)
    for i in range(n):
        x = 20 + rng.uniform(0, 330); y = G - 520 + rng.uniform(0, 220)
        col = [(255, 230, 120), (255, 170, 190), (150, 220, 255), (180, 240, 160)][i % 4]
        c.save(); c.translate(x, y); c.rotate(rng.uniform(-12, 12))
        c.drawRect(skia.Rect.MakeXYWH(-13, -13, 26, 26), P(col, 0.9)); c.restore()


def counter(c, x, y, s, col, a=1.0):
    w_ = skia.Font(F_SANS, 30).measureText(s) + 40
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w_ / 2, y - 26, w_, 52), 26, 26)
    c.drawRRect(rr, P((20, 20, 30), 0.85 * a)); c.drawRRect(rr, P(col, a, stroke=3))
    text(c, s, x, y + 11, F_SANS, 30, col, a)


def world(c, t):
    later = seg(t, SKIP0, SKIP0 + 0.6)
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, G)], [C((86, 80, 96)), C((138, 118, 108))])
    c.drawRect(skia.Rect.MakeLTRB(-400, -200, W + 400, G), skia.Paint(Shader=sh))
    # pegboard + tools on the right, garage door on the left
    c.drawRect(skia.Rect.MakeLTRB(420, G - 560, 760, G - 300), P((170, 138, 104)))
    for gx in range(435, 760, 30):
        for gy in range(G - 545, G - 310, 30): c.drawCircle(gx, gy, 3, P((110, 86, 64)))
    c.drawLine(470, G - 500, 470, G - 410, P((90, 90, 100), stroke=8)); c.drawCircle(700, G - 450, 30, P((90, 90, 100), stroke=6))
    for k in range(6): c.drawLine(-200, G - 640 + k * 70, 520, G - 640 + k * 70, P((40, 38, 46), 0.6, stroke=4))
    # hanging bulb
    c.drawLine(360, 0, 360, G - 640, P((40, 30, 30), stroke=3)); c.drawCircle(360, G - 630, 14, P((255, 220, 150)))
    c.drawCircle(360, G - 630, 300, P((255, 200, 130), 0.12, blur=80))
    notes(c, t)
    c.drawRect(skia.Rect.MakeLTRB(-400, G, W + 400, H + 200), P((110, 104, 100)))
    for k in range(-400, W + 400, 120): c.drawLine(k, G, k - 60, H, P((90, 84, 80), 0.5, stroke=3))
    # his half-finished things (more of them after the skip)
    robot(c, ITEMS[0]); bike(c, ITEMS[1]); drone(c, ITEMS[2])
    if later > 0:
        for x, fn in ((0, drone), (110, robot), (230, bike), (330, robot)): fn(c, x, later)
        c.drawRect(skia.Rect.MakeXYWH(ITEMS[1] + 20, G - 40, 60, 40), P((150, 110, 70)))    # crate he sits on
    # her bench
    x0, x1 = BENCH; top = G - BENCH_H
    c.drawRect(skia.Rect.MakeLTRB(x0, top, x1, top + 16), P((150, 104, 70))); c.drawRect(skia.Rect.MakeLTRB(x0, top, x1, top + 16), P(INK, stroke=3))
    for px in (x0 + 10, x1 - 10): c.drawLine(px, top + 16, px, G, P((110, 76, 52), stroke=10))
    lamp(c, t); parcel(c, t)


def frame(c, t):
    sway = 1 + 0.015 * math.sin(t * 0.8) + 0.05 * seg(t, TURN + 1.2, 13.6)
    c.save(); c.translate(540 + 6 * math.sin(t * 0.6), 1150); c.scale(1.4 * sway, 1.4 * sway); c.translate(-375, -(G - 150))
    world(c, t)
    lo = (1, -0.6)
    heads = {}
    h = hoarder(t)
    jh = figure(c, h["x"], G - 44 if h.get("hip") else G, h["p"], s=S, facing=h["f"], body=H_BODY, rim=((210, 220, 255), 0.5),
                light=lo, mode="hip" if h.get("hip") else "feet")
    heads["h"] = jh["head"]
    sp = shipper(t)
    js = figure(c, sp["x"], G, sp["p"], s=S, facing=sp["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo)
    heads["s"] = js["head"]
    plate_label(c, "IDEA HOARDER", heads["h"][0], heads["h"][1] - 80, GREY, 0.9)
    plate_label(c, "SHIPPER", heads["s"][0] - 30, heads["s"][1] - 80, AMBER, 0.95)
    counter(c, 170, G - 560, f"IDEAS {ideas(t)} · DONE 0", GREY)
    counter(c, 515, G - 560, f"IDEAS 1 · DONE {1 if t >= TURN else 0}", AMBER)
    for ts, who, txt in ([] if COVER else TALK):
        if ts < t < ts + 1.6:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.3, ts + 1.6))
            hd = heads[who]
            bx = clamp(hd[0] + 20, 190, 330) if who == "h" else clamp(hd[0] - 120, 380, 470)
            bubble(c, bx, hd[1] - 190, txt, a, "speech", tail=(hd[0], hd[1] - 60), size=30, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    vignette(c, 0.32)
    if SKIP0 - 0.1 < t < SKIP0 + 1.8:
        a = seg(t, SKIP0 - 0.1, SKIP0 + 0.2) * (1 - seg(t, SKIP0 + 1.4, SKIP0 + 1.8))
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(320, 610, 440, 64), 32, 32)
        c.drawRRect(rr, P((20, 20, 30), 0.85 * a)); c.drawRRect(rr, P(AMBER, a, stroke=3))
        text(c, "1 MONTH LATER", 540, 654, F_SANS, 30, AMBER, a)
    grain(c, t, 0.03)
    end_text(c, t, 13.6, "He started 100 things.", "She finished one.", "Finish what you start.", y=1430)


def events():
    ev = []
    for ts, _, _ in TALK: ev.append(["pop", ts])
    for s in STARTS[1:]: ev.append(["step", s - 0.4, 0])
    ev += [["slide", SKIP0], ["sunrise", TURN - 0.1], ["land", TURN + 0.7], ["summit", TURN + 0.4], ["text", 13.6], ["text2", 14.4]]
    return ev


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 0.9, 2.3, 3.5, 4.6, 5.6, 6.6, 8.6, 10.0, 10.8, 12.0, 14.4, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore()
            series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)
        stills(opening, ts, "check/ep25")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs[:40]))
    else:
        finish_v2("Folge25_Shipper", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
