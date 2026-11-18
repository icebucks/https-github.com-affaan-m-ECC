"""Episode 14 (TikTok: Part 11): PEOPLE PLEASER, Part 2 – the bags get heavier. From a viewer comment on #7
("if he carries it till the end he'll endure more than the one with boundaries").
Autumn hill at sunset (sequel to #7's autumn forest, new light and place: the summit). The pleaser drags four bags that
are not his up the hill, the others stroll ahead empty-handed and leave. He makes it – and collapses. The one with
boundaries arrives with energy left and, by choice, helps him up to see the sunset."""
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 11                     # TikTok part number (internal episode 14)
G = 1240
SC = 1.4
DY = 60
S = 1.0
TURN = 10.9                    # he reaches the top and collapses
BAGCOLS = [(90, 140, 200), (200, 80, 80), (110, 170, 100), (170, 120, 200)]
OTHERS = [("BOSS", 0), ("COWORKER", 1), ("FRIEND", 2), ("FAMILY", 3)]
TALK = [(1.0, "Sure, I'll carry it!"), (4.6, "No problem…"), (8.0, "Almost… there…"), (TURN + 0.5, "I made it… I think.")]
PP_BODY = (196, 202, 216)
BD_BODY = (255, 226, 178)
OTHER_BODY = (176, 186, 204)
HOOK = "4 bags. None of them his.\nWatch what's left at the top."
FOCUS = (230, 1150)            # opening close-up: the pleaser under his bags
CTA = "Part 12 tomorrow:\nthe one who talks, the one who walks"


def ground(x): return G - 0.42 * clamp(x - 250, 0, 330)          # hill rising to a plateau from x 660
def dusk(t): return seg(t, 6.0, 15.0)


# ------------------------------------------------------------------ characters
def pleaser(t):
    if t < TURN:
        x = lerp(240, 600, ease(clamp(t / TURN)) * 0.25 + clamp(t / TURN) * 0.75)
        p = walk(t * 6.0, lean=30, stride=16, arm=8)
        p.update(arm_f=26, elb_f=46, arm_b=18, elb_b=50, head=-8)        # arms forward, gripping the straps
        return dict(x=x, y=ground(x), p=p, f=1)
    if t < TURN + 0.5:                                                    # drops the bags, sinks down
        return dict(x=600, y=ground(600), p=mix(dict(stand(), lean=30), crouch(), seg(t, TURN, TURN + 0.4)), f=1)
    if t < TURN + 2.0:                                                    # sits, exhausted
        return dict(x=600, y=ground(600), p=dict(sit(t), lean=24, head=26, arm_f=10, elb_f=30, arm_b=6, elb_b=30), f=1, sit=True)
    k = seg(t, TURN + 2.0, TURN + 2.6)                                    # takes her hand, stands up
    o = dict(x=600, y=ground(600), p=mix(dict(sit(t), lean=24, head=10), dict(stand(), head=-8, lean=2 * math.sin(t * 1.6)), k), f=1, sit=k < 0.5)
    if 0.15 < k < 0.98: o["reach"] = {"f": (lerp(632, 636, k), ground(600) - lerp(110, 130, k))}
    return o


def boundaries(t):
    if t < TURN - 1.6:                                                    # walks up at her own pace
        x = lerp(40, 520, clamp(t / (TURN - 1.6)))
        return dict(x=x, y=ground(x), p=walk(t * 8, lean=8), f=1)
    if t < TURN + 1.7:                                                    # waits at the top, watching the sunset
        return dict(x=520, y=ground(520), p=dict(stand(), head=-6, lean=-2), f=1)
    k = seg(t, TURN + 1.7, TURN + 2.1)                                     # walks over, holds out her hand – by choice
    x = lerp(520, 660, k)
    o = dict(x=x, y=ground(x), p=walk(t * 8) if k < 1 else dict(offer(), lean=6 + 2 * math.sin(t * 1.6)), f=-1 if k >= 1 else 1)
    kk = seg(t, TURN + 2.0, TURN + 2.6)
    if k >= 1 and kk > 0.15:
        o["reach"] = {"f": (lerp(632, 636, kk), ground(600) - lerp(110, 130, kk))}
    return o


def other(i, t):
    """the four who handed him their bags: stroll up ahead, empty-handed, and leave"""
    t0 = 0.2 + 0.6 * i
    x = lerp(330 + 60 * i, 1150, clamp((t - t0) / 8.0))
    return dict(x=x, y=ground(x), p=walk(t * 8 + i, lean=2), f=1)


# ------------------------------------------------------------------ world
def tree(c, x, y, sc, col, seed):
    rng = np.random.default_rng(seed)
    c.drawLine(x, y, x, y - 120 * sc, P((70, 48, 36), stroke=14 * sc))
    for k in range(5):
        c.drawCircle(x + rng.uniform(-40, 40) * sc, y - (130 + rng.uniform(0, 60)) * sc, rng.uniform(34, 52) * sc, P(col))


def world(c, t):
    u = dusk(t)
    sky(c, t, lerpc((236, 150, 90), (90, 70, 120), u), lerpc((250, 186, 110), (220, 110, 90), u), lerpc((255, 214, 150), (255, 160, 100), u), 1000)
    # the sun sinks toward the hill
    sy = lerp(820, 980, u)
    c.drawCircle(680, sy, 70, P((255, 236, 190), 0.95)); c.drawCircle(680, sy, 160, P((255, 200, 120), 0.25, blur=40))
    for i in range(7):   # birds heading home across the sunset (keeps the last seconds alive)
        k = (t - 9.0 - 0.15 * i) / 8.0
        if 0 < k < 1:
            bx = lerp(-120, 900, k) - 26 * (i % 3); by = 860 - 30 * k + 14 * (i % 2) + 6 * math.sin(t * 9 + i)
            flap = 6 * math.sin(t * 12 + i)
            c.drawPath(poly([(bx - 12, by - flap), (bx, by), (bx + 12, by - flap)], close=False), P((70, 50, 70), 0.8, stroke=3))
    # far hills
    c.drawPath(poly([(-300, 1060), (100, 1000), (400, 1040), (700, 980), (1000, 1030), (W + 300, 1000), (W + 300, G), (-300, G)]),
               P(lerpc((176, 110, 90), (110, 70, 100), u)))
    for i, (x, sc) in enumerate(((-60, 0.9), (120, 1.0), (920, 0.95))):
        tree(c, x, ground(x) + 10, sc, lerpc((214, 120, 60), (150, 70, 60), u), i + 3)
    # the hill with the path
    pts = [(-300, G)] + [(x, ground(x)) for x in range(-300, W + 301, 30)] + [(W + 300, H + 300), (-300, H + 300)]
    c.drawPath(poly(pts), P(lerpc((150, 104, 64), (96, 66, 60), u)))
    c.drawPath(poly([(x, ground(x)) for x in range(-300, W + 301, 30)], close=False), P(INK, stroke=5))
    # summit marker
    c.drawLine(712, ground(712), 712, ground(712) - 120, P(INK, stroke=8)); c.drawLine(712, ground(712), 712, ground(712) - 120, P((200, 200, 210), stroke=4))
    c.drawPath(poly([(712, ground(712) - 120), (762, ground(712) - 104), (712, ground(712) - 88)]), P((220, 80, 70)))
    # falling leaves
    rng = np.random.default_rng(5)
    for i in range(40):
        k = (rng.uniform(0, 1) + t * rng.uniform(0.07, 0.16)) % 1.0
        x = rng.uniform(-100, W + 100) + 40 * math.sin(t * 1.3 + i)
        c.drawOval(skia.Rect.MakeXYWH(x, lerp(700, G, k), 12, 7), P(lerpc((230, 120, 50), (200, 90, 60), u), 0.8))
    return u


def bag(c, x, y, ang, col, a=1.0):
    c.save(); c.translate(x, y); c.rotate(ang)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-22, -26, 44, 52), 10, 10)
    c.drawRRect(r, P(col, a)); c.drawRRect(r, P(INK, a, stroke=4))
    c.drawLine(-14, -8, 14, -8, P(INK, 0.5 * a, stroke=3))
    c.restore()


def frame(c, t):
    c.save(); c.translate(540, G + DY); c.scale(SC, SC); c.translate(-540, -G)
    u = world(c, t)
    lo = (1, -0.4)
    # the others, empty-handed
    for name, i in OTHERS:
        o = smooth(lambda tt: other(i, tt), t)
        jo = figure(c, o["x"], o["y"], o["p"], s=0.82, facing=o["f"], body=OTHER_BODY, light=lo)
        if i == 1: head1 = jo["head"]
    if t < 3.2:   # one label for the group: they handed him their bags
        plate_label(c, "EVERYONE ELSE", min(head1[0] + 30, 560), head1[1] - 60, GREY, 0.75 * (1 - seg(t, 2.6, 3.2)))
    pp = smooth(pleaser, t); bd = smooth(boundaries, t)
    shadow(c, pp["x"], pp["y"], S, 0.3); shadow(c, bd["x"], bd["y"], S, 0.3)
    jb = figure(c, bd["x"], bd["y"], bd["p"], s=S, facing=bd["f"], body=BD_BODY, rim=((255, 214, 150), 0.6), light=lo, reach=bd.get("reach"))
    # her own small backpack only
    bag(c, jb["sh"][0] - 16 * bd["f"], jb["sh"][1] + 26, -8 * bd["f"], (230, 170, 80))
    jp = figure(c, pp["x"], pp["y"], pp["p"], s=S, facing=pp["f"], body=PP_BODY, rim=((190, 210, 255), 0.5), light=lo, reach=pp.get("reach"))
    # four bags that are not his: a tower on his back, then they drop at the top
    for i, col in enumerate(BAGCOLS):
        if t < TURN:
            bx = jp["sh"][0] - 26 - i * 6; by = jp["sh"][1] + 20 - i * 46
            bag(c, bx, by, -14 + 5 * math.sin(t * 3 + i), col)
        else:
            k = ease(clamp((t - TURN - 0.05 * i) / 0.35))
            bx = lerp(570 - i * 6, 530 - i * 34, k); by = lerp(ground(570) - 120 - i * 46, ground(540) - 26, k)
            bag(c, bx, by, lerp(-14, 20 * (i % 2) - 10, k), col)
    # sweat drops while he climbs
    if t < TURN:
        k = (t * 1.6) % 1.0
        c.drawCircle(jp["head"][0] + 24, jp["head"][1] + 10 + 30 * k, 5, P((170, 210, 240), 0.8 * (1 - k)))
    close = seg(t, TURN + 1.5, TURN + 2.0)                 # when they stand together: labels on two levels
    plate_label(c, "PEOPLE PLEASER", jp["head"][0] - 30 * close, jp["head"][1] - 52 - (0 if t > TURN else 150) - 40 * close, GREY, 0.9)
    plate_label(c, "BOUNDARIES", jb["head"][0] + 30 * close, jb["head"][1] - 52, AMBER, 0.95 * seg(jb["head"][0], 190, 240))   # hidden until she is in frame
    for ts, txt in TALK:
        if ts < t < ts + 1.9:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.6, ts + 1.9))
            hy = jp["head"][1] - (300 if t < TURN else 170)
            bubble(c, clamp(jp["head"][0] + 40, 260, 640), hy, txt, a, "speech", tail=(jp["head"][0] + 10, jp["head"][1] - 60), size=32,
                   pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), P((255, 150, 90), 0.05 * u))
    vignette(c, 0.4)
    grain(c, t, 0.035)
    end_text(c, t, 13.6, "He carried everything.", "She chose what to carry.", "Put some bags down.", y=1430)


def events():
    ev = []
    for ts, _ in TALK: ev.append(["pop", ts])
    for k in range(int(TURN / 0.52)): ev.append(["step", 0.3 + k * 0.52, False])
    ev += [["land", TURN + 0.1], ["slide", TURN + 0.25], ["summit", TURN + 2.4], ["sunrise", TURN + 1.6], ["text", 13.6], ["text2", 14.4]]
    return ev


def overlay(c, t):
    series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 0.6, 2.0, 4.6, 6.4, 8.4, 10.4, 11.4, 12.6, 13.4, 15.2, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore(); overlay(c, t)
        stills(opening, ts, "check/ep14")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs))
    else:
        finish_v2("Folge14_PleaserPart2", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
