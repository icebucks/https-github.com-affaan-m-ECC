"""Episode 22 (TikTok: Part 19): WAITER vs BUILDER – promised by the Part 18 cliffhanger ("the one who waits for a sign").
An empty lot with a "COMING SOON" sign, morning light.
Waiter (grey, on a bench): "Someone should build something here." – "Maybe next month." – after the skip: "Still waiting for a sign."
Builder (amber): picks up one brick after another and lays a wall. "3 MONTHS LATER" the wall is a little shop; at the turn the
"OPEN" sign lights up: "It started with one brick." """
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 19                     # TikTok part number (internal episode 22)
G = 1300
S = 1.3
SKIP0, SKIP1 = 6.2, 8.4        # "3 months later"
TURN = 9.4                     # OPEN sign lights up
W_BODY = (196, 202, 216)
B_BODY = (255, 226, 178)
BENCH_X = 250
WX = 380                       # waiter hip x
BX = 720                       # builder stands here
PILE = (800, G)                # brick pile (right of the builder)
SHOP = (500, 690)              # little shop after the skip
BW, BH = 48, 28                # brick size
CYCLE = 1.1
TALK = [(0.9, "w", "Someone should build here."), (2.4, "b", "Why not me?"), (4.4, "w", "Maybe next month."),
        (SKIP1 + 0.3, "w", "Still waiting for a sign."), (TURN + 0.9, "b", "It started with one brick.")]
HOOK = "He waited for a sign.\nShe laid the first brick."
FOCUS = (540, 1180)
COVER = False
CTA = "Part 20 next:\nthe one who checks his phone"


def hip_of(x, p, f):
    J = pose_points(p, S, f)
    low = max(J["foot_f"][1], J["foot_b"][1])
    return x, G - low - 6 * S, J


def free_hands(x, p, f):
    hx, hy, J = hip_of(x, p, f)
    return {s: (hx + J[f"hand_{s}"][0], hy + J[f"hand_{s}"][1]) for s in ("f", "b")}


def blend(a, b, k):
    return {s: (lerp(a[s][0], b[s][0], k), lerp(a[s][1], b[s][1], k)) for s in a}


LEAN = dict(lean=22, head=8, arm_f=40, elb_f=20, arm_b=30, elb_b=20, leg_f=10, leg_b=-10)


# ------------------------------------------------------------------ bricks
def phase(t): return ((t - 0.5) % CYCLE) / CYCLE


def n_laid(t):
    if t >= SKIP0: return 99
    if t < 0.5: return 0
    return int((t - 0.5) / CYCLE) + (1 if phase(t) >= 0.7 else 0)


def brick_slot(i):
    row, col = divmod(i, 3)
    return BX - 64 - (col + 1) * BW + (BW / 2) * (row % 2), G - (row + 1) * BH


def carrying(t):
    return 0.5 <= t < SKIP0 - 0.4 and 0.2 <= phase(t) < 0.7


# ------------------------------------------------------------------ characters
def waiter(t):
    p = dict(sit(t), lean=-6, head=-8, arm_f=-20, elb_f=30, arm_b=-26, elb_b=30)          # leans back, relaxed
    if 4.0 < t < 5.6: p = mix(p, dict(p, arm_f=70, elb_f=110, head=-14), seg(t, 4.0, 4.3) * (1 - seg(t, 5.2, 5.6)))   # checks his watch
    if t > SKIP0: p = dict(sit(t), lean=24, head=24, arm_f=40, elb_f=120, arm_b=34, elb_b=120)   # chin in hands, bored
    if t > TURN + 1.6: p = mix(p, dict(p, head=-10, lean=6), seg(t, TURN + 1.6, TURN + 2.1))  # finally looks at the shop
    return dict(x=WX, y=G - 52, p=p, f=1)


PICK = dict(crouch(), arm_f=50, elb_f=10, arm_b=40, elb_b=10, head=-10)
HOLD = dict(stand(), lean=6, arm_f=55, elb_f=70, arm_b=45, elb_b=70)


def builder(t):
    if t >= SKIP0:                                                          # proud next to her shop
        p = hands_on_hips()
        if t >= TURN + 0.3: p = mix(p, cheer(t), seg(t, TURN + 0.3, TURN + 0.8) * (1 - seg(t, TURN + 2.0, TURN + 2.6)))
        return dict(x=SHOP[1] + 80, p=p, f=-1)
    if t < 0.5: return dict(x=BX, p=stand(), f=1)
    ph = phase(t)
    if ph < 0.2:   f, p = 1.0, mix(stand(), PICK, seg(ph, 0.0, 0.18))                       # bends to the pile
    elif ph < 0.45: f, p = 1 - 2 * seg(ph, 0.25, 0.42), mix(PICK, HOLD, seg(ph, 0.2, 0.32))  # stands up, turns with the brick
    elif ph < 0.7: f, p = -1.0, mix(HOLD, PICK, seg(ph, 0.47, 0.66))                        # bends down to the wall
    else:          f, p = -1 + 2 * seg(ph, 0.8, 0.97), mix(PICK, stand(), seg(ph, 0.7, 0.82))
    return dict(x=BX, p=p, f=f)


# ------------------------------------------------------------------ world
def brick(c, x, y, a=1.0):
    c.drawRect(skia.Rect.MakeXYWH(x + 1, y + 1, BW - 2, BH - 2), P((186, 92, 64), a))
    c.drawRect(skia.Rect.MakeXYWH(x + 1, y + 1, BW - 2, BH - 2), P(INK, a, stroke=2))


def shop(c, t, a):
    if a <= 0: return
    x0, x1, top = SHOP[0], SHOP[1], G - 300
    c.saveLayerAlpha(None, int(255 * a))
    for row in range(int((G - top) // BH)):
        off = (BW / 2) * (row % 2)
        for col in range(-1, int((x1 - x0) // BW) + 1):
            bx = x0 + off + col * BW
            if bx < x0 - 2 or bx + BW > x1 + 2: continue
            brick(c, bx, G - (row + 1) * BH)
    lit = seg(t, TURN, TURN + 0.3)
    win = skia.Rect.MakeLTRB(x0 + 30, G - 230, x1 - 30, G - 70)
    c.drawRect(win, P(lerpc((60, 60, 80), (255, 214, 140), lit)))
    c.drawRect(win, P(INK, stroke=5))
    if lit > 0: c.drawRect(win, P((255, 200, 120), 0.4 * lit, blur=30))
    # striped awning
    for i in range(8):
        sx = x0 - 20 + i * (x1 - x0 + 40) / 8
        c.drawPath(poly([(sx, top - 10), (sx + (x1 - x0 + 40) / 8, top - 10), (sx + (x1 - x0 + 40) / 8, top + 40), (sx, top + 40)]),
                   P(AMBER if i % 2 == 0 else (250, 246, 236)))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 20, top - 10, x1 + 20, top + 40), P(INK, stroke=4))
    # OPEN sign
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((x0 + x1) / 2 - 80, top - 90, 160, 64), 14, 14)
    c.drawRRect(rr, P((30, 30, 40))); c.drawRRect(rr, P(INK, stroke=4))
    col = lerpc((90, 90, 100), (255, 120, 90), lit)
    if lit > 0: c.drawRRect(rr, P((255, 110, 80), 0.45 * lit, blur=24))
    text(c, "OPEN", (x0 + x1) / 2, top - 44, F_CAP, 40, col, 1.0)
    c.restore()


def world(c, t):
    later = seg(t, SKIP0, SKIP0 + 0.6)
    eve = seg(t, SKIP1 - 0.4, TURN)
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, G)], [C(lerpc((150, 186, 226), (60, 60, 110), eve)), C(lerpc((236, 222, 200), (246, 150, 110), eve))])
    c.drawRect(skia.Rect.MakeLTRB(-400, -200, W + 400, G), skia.Paint(Shader=sh))
    sun(c, 860 - 200 * eve, 560 + 340 * eve, 0.9, r=60)
    # neighbour houses
    for hx, hw, hh, col in ((-140, 300, 420, (170, 150, 140)), (930, 320, 480, (150, 140, 150))):
        c.drawRect(skia.Rect.MakeLTRB(hx, G - hh, hx + hw, G), P(lerpc(col, (90, 80, 100), eve * 0.6)))
        c.drawRect(skia.Rect.MakeLTRB(hx, G - hh, hx + hw, G), P(INK, stroke=4))
        for wy in range(G - hh + 50, G - 60, 110):
            for wx in range(hx + 40, hx + hw - 60, 110):
                c.drawRect(skia.Rect.MakeXYWH(wx, wy, 54, 64), P(lerpc((120, 150, 190), (255, 214, 140), eve)))
    haze(c, G - 60, lerpc((230, 220, 210), (250, 170, 130), eve), 0.25)
    # ground: dirt lot + sidewalk
    c.drawRect(skia.Rect.MakeLTRB(-400, G, W + 400, H + 200), P((120, 98, 78)))
    c.drawRect(skia.Rect.MakeLTRB(-400, G, W + 400, G + 26), P((168, 160, 150)))
    tufts(c, G + 4, (110, 130, 70), seed=5, n=20, a=0.7)
    # COMING SOON sign (gets weathered after the skip)
    c.save(); c.translate(150, G - 250); c.rotate(-7 * later)
    c.drawLine(-60, 40, -60, 250, P((90, 70, 54), stroke=10)); c.drawLine(60, 40, 60, 250, P((90, 70, 54), stroke=10))
    rr = skia.Rect.MakeXYWH(-110, -60, 220, 110)
    c.drawRect(rr, P(lerpc((240, 236, 226), (200, 190, 170), later))); c.drawRect(rr, P(INK, stroke=5))
    text(c, "COMING", 0, -14, F_CAP, 38, (200, 70, 50), 1.0)
    text(c, "SOON", 0, 32, F_CAP, 38, (200, 70, 50), 1.0)
    c.restore()
    # bench
    c.drawRect(skia.Rect.MakeLTRB(BENCH_X + 70, G - 56, BENCH_X + 230, G - 44), P((130, 90, 60)))
    c.drawRect(skia.Rect.MakeLTRB(BENCH_X + 70, G - 56, BENCH_X + 230, G - 44), P(INK, stroke=3))
    for lx in (BENCH_X + 84, BENCH_X + 216): c.drawLine(lx, G - 44, lx, G, P(INK, stroke=6))
    # wall / shop
    if t < SKIP0 + 0.6:
        a = 1 - later
        for i in range(min(n_laid(t), 40)):
            brick(c, *brick_slot(i), a=a)
        # brick pile
        for i in range(5):
            row = 0 if i < 3 else 1
            brick(c, PILE[0] - 20 + (i % 3) * BW - (BW / 2) * row - (BW if row else 0) + (BW if i == 4 else 0), PILE[1] - BH * (1 + row), a=a)
    shop(c, t, later)
    return later


def frame(c, t):
    sway = 1 + 0.015 * math.sin(t * 0.8) + 0.05 * seg(t, TURN + 1.2, 13.6)
    c.save(); c.translate(540 + 6 * math.sin(t * 0.6), 1150); c.scale(1.15 * sway, 1.15 * sway); c.translate(-520, -(G - 200))
    world(c, t)
    lo = (1, -0.6)
    heads = {}
    w = waiter(t)
    jw = figure(c, w["x"], w["y"], w["p"], s=S, facing=w["f"], body=W_BODY, rim=((210, 220, 255), 0.5), light=lo, mode="hip")
    heads["w"] = jw["head"]
    b = builder(t)
    jb = figure(c, b["x"], G, b["p"], s=S, facing=b["f"], body=B_BODY, rim=((255, 220, 170), 0.6), light=lo)
    heads["b"] = jb["head"]
    if carrying(t):                                                      # the brick sits in her hands
        hx = (jb["hand_f"][0] + jb["hand_b"][0]) / 2; hy = (jb["hand_f"][1] + jb["hand_b"][1]) / 2
        brick(c, hx - BW / 2, hy - BH / 2 - 6)
    if TURN < t < TURN + 1.2:                                              # sparkle around the OPEN sign
        k = seg(t, TURN, TURN + 1.2)
        for i in range(10):
            ang = i / 10 * 2 * math.pi; r_ = 60 + 100 * k
            c.drawCircle((SHOP[0] + SHOP[1]) / 2 + r_ * math.cos(ang), G - 344 + r_ * math.sin(ang) * 0.6, 6 * (1 - k) + 1, P((255, 220, 120), 1 - k))
    plate_label(c, "WAITER", heads["w"][0], heads["w"][1] - 80, GREY, 0.9)
    plate_label(c, "BUILDER", heads["b"][0], heads["b"][1] - 80, AMBER, 0.95)
    for ts, who, txt in ([] if COVER else TALK):
        if ts < t < ts + 1.6:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.3, ts + 1.6))
            hd = heads[who]
            bx = clamp(hd[0] - 40, 200, 420) if who == "w" else clamp(hd[0] - 150, 300, 560)
            by = hd[1] - (160 if who == "w" else 270)
            bubble(c, bx, by, txt, a, "speech", tail=(hd[0], hd[1] - 50), size=30, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    vignette(c, 0.3)
    if SKIP0 - 0.1 < t < SKIP0 + 1.8:
        a = seg(t, SKIP0 - 0.1, SKIP0 + 0.2) * (1 - seg(t, SKIP0 + 1.4, SKIP0 + 1.8))
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(320, 610, 440, 64), 32, 32)
        c.drawRRect(rr, P((20, 20, 30), 0.85 * a)); c.drawRRect(rr, P(AMBER, a, stroke=3))
        text(c, "3 MONTHS LATER", 540, 654, F_SANS, 30, AMBER, a)
    grain(c, t, 0.03)
    end_text(c, t, 13.6, "He waited for a sign.", "She laid one brick a day.", "Be the sign. Start building.", y=1430)


def events():
    ev = []
    for ts, _, _ in TALK: ev.append(["pop", ts])
    for i in range(5): ev.append(["thud", 0.5 + (i + 0.7) * CYCLE])
    ev += [["slide", SKIP0], ["sunrise", SKIP1], ["land", TURN], ["summit", TURN + 0.5], ["text", 13.6], ["text2", 14.4]]
    return ev


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 0.9, 1.5, 2.4, 3.3, 4.6, 6.6, 8.8, 9.8, 10.6, 12.0, 14.4, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore()
            series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)
        stills(opening, ts, "check/ep22")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs[:40]))
    else:
        finish_v2("Folge22_Builder", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
