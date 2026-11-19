"""Episode 17 (TikTok: Part 14): COMPARER vs OWN PATH – promised by the Part 13 cliffhanger ("the one who keeps looking sideways").
A race on two lanes drawn in the wet sand of a beach at sunrise (pink sky, low sun over the sea – new place + light).
The camera runs with them. The comparer looks over at her lane 3 times in 10 seconds ("She's ahead?!", "How?!", "Faster than me?!")
and runs straight into the sandcastle in his own lane. She only looks ahead and breaks the finish tape."""
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 14                     # TikTok part number (internal episode 17)
G = 1240                       # her lane (back)
G2 = G + 46                    # his lane (front)
SC = 1.4
DY = 30
S = 1.0
TURN = 9.6                     # he trips over the sandcastle
LOOKS = [1.9, 4.5, 7.1]        # the 3 sideways looks
TALK = [(LOOKS[0] + 0.1, "c", "She's ahead?!"), (LOOKS[1] + 0.1, "c", "How?!"), (LOOKS[2] + 0.1, "c", "Faster than me?!"),
        (TURN + 1.6, "o", "Your lane. Your race.")]
C_BODY = (196, 202, 216)
O_BODY = (255, 226, 178)
HOOK = "Looked sideways 3 times.\nWatch what's in his lane."
FOCUS = (560, 980)
CTA = "Part 15 tomorrow:\nthe one who hits snooze"
V = 140.0                      # world scroll speed (px/s) – the camera runs with them
CASTLE_W = 450 + V * TURN      # sandcastle position in world coords (reached at TURN)
FINISH_W = 520 + V * (TURN + 1.3)   # exactly where she is when she breaks the tape


def cam(t):
    """camera offset: scrolls with the runners, stops when she reaches the finish"""
    return V * min(t, TURN + 1.3)


def looking(t):
    return max((seg(t, a, a + 0.25) * (1 - seg(t, a + 1.0, a + 1.3)) for a in LOOKS), default=0.0)


# ------------------------------------------------------------------ characters (screen-relative x; world x = x + cam)
def comparer(t):
    if t < TURN - 0.05:
        lk = looking(t)
        p = run(t * 11)
        p.update(head=lerp(-10, -30, lk), lean=lerp(16, 6, lk))      # head turns up/back toward her lane
        x = 420 - 22 * sum(seg(t, a, a + 1.3) for a in LOOKS if t > a)  # every look costs him ground
        return dict(x=x, y=G2, p=p, f=1)
    xs = 420 - 66
    if t < TURN + 0.55:                                               # trips and goes down
        k = seg(t, TURN - 0.05, TURN + 0.55)
        return dict(x=xs + 30 * k, y=G2, p=mix(run(t * 11), dict(crouch(), lean=60, head=-10, arm_f=80, elb_f=20, arm_b=60, elb_b=20), k), f=1, rot=70 * k)
    k = seg(t, TURN + 1.6, TURN + 2.4)                                # sits up in the sand, looks at the castle
    return dict(x=xs + 30, y=G2, p=mix(dict(crouch(), lean=60, head=-10, arm_f=80, elb_f=20, arm_b=60, elb_b=20), dict(crouch(), lean=8, head=-12, arm_f=20, elb_f=40, arm_b=-10, elb_b=30), k),
                f=1, rot=70 * (1 - k))


def own(t):
    if t < TURN + 1.3:
        p = run(t * 11 + 1.3); p.update(head=-6)                      # eyes only ahead
        return dict(x=480 + 40 * seg(t, 0.0, 3.0), y=G, p=p, f=1)
    k = seg(t, TURN + 1.3, TURN + 1.9)
    return dict(x=520 + 80 * k, y=G, p=mix(run(t * 11 + 1.3), cheer(t), k), f=1)


# ------------------------------------------------------------------ world
def world(c, t):
    u = seg(t, 0, 14)                                                 # sun climbs, pink → golden
    sky(c, t, lerpc((120, 90, 160), (110, 150, 220), u), lerpc((250, 150, 170), (255, 190, 160), u), lerpc((255, 200, 160), (255, 230, 180), u), 1060)
    sy = lerp(1050, 960, u)
    c.drawCircle(690, sy, 220, P((255, 210, 170), 0.35, blur=60)); c.drawCircle(690, sy, 66, P((255, 226, 190), 0.9))
    sea = poly([(-300, 1060), (W + 300, 1060), (W + 300, G - 40), (-300, G - 40)])
    c.drawPath(sea, P(lerpc((110, 120, 190), (90, 160, 210), u)))
    for i in range(14):                                               # glitter on the sea
        x = (i * 97 + t * 30) % 700 - 100; y = 1080 + (i * 37) % 100      # left part only (right = TikTok buttons)
        c.drawLine(x, y, x + 34, y, P((255, 220, 200), 0.4, stroke=3))
    # foam line + wet sand + dry sand
    ox = cam(t)
    foam = [(-300 + k * 30, G - 40 + 6 * math.sin(k * 0.7 + t * 2)) for k in range(50)]
    c.drawPath(poly([(-300, G - 40)] + foam + [(W + 300, G - 20), (-300, G - 20)]), P((236, 214, 200), 0.9))
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 24, W + 300, H + 300), P(lerpc((200, 160, 150), (226, 196, 160), u)))
    c.drawRect(skia.Rect.MakeLTRB(-300, G + 70, W + 300, H + 300), P(lerpc((214, 180, 160), (236, 212, 170), u)))
    # lane lines drawn in the sand + distance flags (scroll with the camera)
    for y in (G - 16, G + 22, G2 + 34):
        c.drawLine(-300, y, W + 300, y, P((150, 110, 90), 0.45, stroke=4))      # lines drawn into the sand
    for k in range(-2, 40):
        wx = k * 260; x = wx - ox
        if -200 < x < 1300:
            c.drawLine(x, G - 16, x, G - 70, P(INK, stroke=4)); c.drawPath(poly([(x, G - 70), (x + 34, G - 62), (x, G - 54)]), P((60, 160, 200)))
    # palms passing in the back
    for k in range(-1, 12):
        x = k * 520 + 200 - ox * 0.6
        if -200 < x < 1300:
            c.drawPath(poly([(x - 6, G - 40), (x + 6, G - 40), (x + 18, G - 260), (x + 6, G - 260)]), P((110, 80, 70)))
            for j in range(5):
                a = math.radians(-160 + j * 32 + 4 * math.sin(t * 1.3 + j))
                c.drawPath(poly([(x + 12, G - 262), (x + 12 + 110 * math.cos(a), G - 262 + 60 * math.sin(a) + 30), (x + 12 + 30 * math.cos(a), G - 254)]), P((70, 130, 90)))
    # the sandcastle in HIS lane
    x = CASTLE_W - ox
    if -200 < x < 1300:
        broke = seg(t, TURN, TURN + 0.4)
        c.drawPath(poly([(x - 46, G2 + 8), (x + 46, G2 + 8), (x + 34, G2 - 40 + 30 * broke), (x - 34, G2 - 40 + 30 * broke)]), P((220, 180, 120)))
        if broke < 0.5:
            c.drawPath(poly([(x - 16, G2 - 40), (x + 16, G2 - 40), (x + 10, G2 - 74), (x - 10, G2 - 74)]), P((214, 172, 112)))
            c.drawLine(x, G2 - 74, x, G2 - 104, P(INK, stroke=3)); c.drawPath(poly([(x, G2 - 104), (x + 22, G2 - 97), (x, G2 - 90)]), P((230, 80, 70)))
        for i in range(10):                                            # sand flies
            if TURN <= t < TURN + 0.8:
                k = (t - TURN) / 0.8; a = -0.3 - i * 0.25
                c.drawCircle(x + math.cos(a) * 140 * k, G2 - 20 + math.sin(a) * 140 * k + 160 * k * k, 6 * (1 - k) + 2, P((220, 180, 120), 1 - k))
    # finish tape + post
    x = FINISH_W - ox
    if -200 < x < 1300:
        snap = seg(t, TURN + 1.3, TURN + 1.6)
        for yy in (G - 100, G2 + 30):
            c.drawLine(x, yy, x, yy - 110 if yy == G2 + 30 else yy - 10, P(INK, stroke=6))
        c.drawLine(x, G - 170, x, G + 30, P((240, 240, 240), stroke=8)); c.drawLine(x, G - 170, x, G + 30, P(INK, stroke=3))
        if snap < 1:
            c.drawLine(x, G - 120, x, G - 40, P((230, 60, 60), stroke=6))
        else:
            c.drawLine(x, G - 120, x + 60, G - 60, P((230, 60, 60), stroke=6))
    c.drawRect(skia.Rect.MakeLTRB(-300, -500, W + 300, H + 300), P((255, 160, 140), 0.05 * (1 - u)))


def frame(c, t):
    sway = 1 + 0.018 * math.sin(t * 0.9) + 0.06 * seg(t, 13.6, T_END)
    c.save(); c.translate(540 + 8 * math.sin(t * 0.6), G + DY); c.scale(SC * sway, SC * sway); c.translate(-540, -G)
    world(c, t)
    lo = (1, -0.5)
    ow = smooth(own, t)
    shadow(c, ow["x"], ow["y"], S, 0.25)
    jo = figure(c, ow["x"], ow["y"], ow["p"], s=S, facing=ow["f"], body=O_BODY, rim=((255, 220, 190), 0.6), light=lo)
    co = smooth(comparer, t)
    shadow(c, co["x"], co["y"], S, 0.3)
    jc = figure(c, co["x"], co["y"] - (36 if co.get("sit") else 0), co["p"], s=S, facing=co["f"], body=C_BODY, rim=((210, 220, 255), 0.5), light=lo, rot=co.get("rot", 0.0))
    # his sideways glance: a dotted sight line to her lane
    lk = looking(t)
    if lk > 0.05 and t < TURN:
        hx, hy = jc["head"]; tx, ty = jo["head"]
        for k in range(1, 7):
            q = k / 7
            c.drawCircle(lerp(hx, tx, q) + 6, lerp(hy, ty, q) - 10, 4, P((255, 255, 255), 0.7 * lk))
    plate_label(c, "COMPARER", jc["head"][0] - 60 * seg(t, TURN, TURN + 0.5), jc["head"][1] + 130, GREY, 0.9)
    plate_label(c, "OWN PATH", jo["head"][0] + 40, jo["head"][1] - 52, AMBER, 0.95)
    for ts, who, txt in TALK:
        if ts < t < ts + 1.5:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.2, ts + 1.5))
            hd = jc["head"] if who == "c" else jo["head"]
            bx = clamp(hd[0] + (60 if who == "c" else 40), 260, 620)
            bubble(c, bx, hd[1] - 120 - (40 if who == "c" else 0), txt, a, "speech", tail=(hd[0], hd[1] - 50), size=30, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    vignette(c, 0.3)
    grain(c, t, 0.03)
    end_text(c, t, 13.6, "He watched her lane.", "She ran her own.", "Eyes on your lane.", y=1430)


def events():
    ev = []
    for ts, _, _ in TALK: ev.append(["pop", ts])
    for k in range(int(TURN / 0.36)): ev.append(["step", 0.2 + k * 0.36, False])
    ev += [["thud", TURN + 0.3], ["slide", TURN + 0.35], ["summit", TURN + 1.35], ["sunrise", TURN + 1.3], ["text", 13.6], ["text2", 14.4]]
    return ev


def overlay(c, t):
    series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 0.6, 2.3, 4.9, 7.5, 9.0, 9.7, 10.2, 11.0, 11.6, 12.6, 14.4, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore(); overlay(c, t)
        stills(opening, ts, "check/ep17")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs))
    else:
        finish_v2("Folge17_OwnPath", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
