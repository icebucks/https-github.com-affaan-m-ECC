"""Episode 23 (TikTok: Part 20): DISTRACTED vs FOCUSED – promised by the Part 19 cliffhanger ("the one who checks his phone").
A library at night, two desks, two open books, a wall clock. A page counter floats above each desk.
Distracted (grey): picks up his phone – "Just one quick check." – "Haha, one more video…" – after the skip: "Wait… 2 hours?!" PAGE 1.
Focused (amber): puts her phone in the drawer – "Phone away. Focus." – turns page after page; "2 HOURS LATER" she closes the
finished book as the lamp glows: "Chapter done." """
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 20                     # TikTok part number (internal episode 23)
G = 1300
S = 1.3
SKIP0, SKIP1 = 6.2, 8.4        # "2 hours later"
TURN = 9.4                     # she closes the finished book
D_BODY = (196, 202, 216)
F_BODY = (255, 226, 178)
SEAT = 56
DESK_H = 118
D_X, F_X = 250, 610            # chair / hip x
D_DESK, F_DESK = (300, 470), (660, 830)
TALK = [(0.9, "d", "Just one quick check."), (2.2, "f", "Phone away. Focus."), (4.0, "d", "Haha, one more video..."),
        (SKIP1 + 0.2, "d", "Wait... 2 hours?!"), (TURN + 0.9, "f", "Chapter done.")]
HOOK = "Same book. Same night.\nOnly one turned the page."
FOCUS = (540, 1180)
COVER = False
CTA = "Part 21 next:\nthe one who buys everything"


def f_pages(t):
    if t < 2.8: return 1
    if t < SKIP0: return 1 + int((t - 2.8) / 0.7)
    if t < SKIP1: return int(lerp(1 + int((SKIP0 - 2.8) / 0.7), 212, seg(t, SKIP0, SKIP1)))
    return 212


def flip_k(t):
    """0..1 while a page is turning (her book)"""
    if 2.8 <= t < SKIP0: return ((t - 2.8) % 0.7) / 0.7 if ((t - 2.8) % 0.7) < 0.35 else None
    return None


# ------------------------------------------------------------------ characters
def distracted(t):
    base = sit(t)
    phone_up = dict(base, lean=-4, head=14, arm_f=62, elb_f=120, arm_b=30, elb_b=60)       # phone at his face
    if t < 0.6: p = dict(base, arm_f=70, elb_f=40, arm_b=60, elb_b=40, head=10)            # hands on the book
    else: p = mix(dict(base, arm_f=70, elb_f=40, arm_b=60, elb_b=40, head=10), phone_up, seg(t, 0.6, 0.9))
    if 3.8 < t < 5.4: p = dict(p, lean=-10 + 4 * math.sin(t * 14), head=8)                 # laughs at a video
    if SKIP1 < t < SKIP1 + 1.4: p = mix(p, dict(p, head=-6, lean=0, arm_f=40, elb_f=90), seg(t, SKIP1, SKIP1 + 0.3))   # looks at the clock
    if t > TURN + 1.2: p = mix(p, dict(p, head=0), seg(t, TURN + 1.2, TURN + 1.6))
    return dict(x=D_X, y=G - SEAT, p=p, f=1)


def focused(t):
    base = sit(t)
    read = dict(base, lean=14, head=18, arm_f=72, elb_f=36, arm_b=62, elb_b=40)
    p = read
    if 1.6 < t < 2.8:                                                                      # phone into the drawer
        k = seg(t, 1.6, 1.9) * (1 - seg(t, 2.4, 2.8))
        p = mix(read, dict(base, lean=4, head=6, arm_f=40, elb_f=20, arm_b=62, elb_b=40), k)
    fk = flip_k(t)
    if fk is not None: p = dict(p, arm_f=72 + 26 * math.sin(math.pi * fk), elb_f=36 - 20 * math.sin(math.pi * fk))
    if t > TURN:                                                                           # closes the book, stretches
        p = mix(read, dict(cheer(t), leg_f=base["leg_f"], leg_b=base["leg_b"], knee_f=base["knee_f"], knee_b=base["knee_b"]),
                seg(t, TURN + 0.2, TURN + 0.6) * (1 - seg(t, TURN + 2.0, TURN + 2.6)))
    return dict(x=F_X, y=G - SEAT, p=p, f=1)


# ------------------------------------------------------------------ world
def chair(c, x):
    c.drawRect(skia.Rect.MakeLTRB(x - 40, G - SEAT, x + 40, G - SEAT + 12), P((110, 76, 54)))
    c.drawRect(skia.Rect.MakeLTRB(x - 40, G - SEAT, x + 40, G - SEAT + 12), P(INK, stroke=3))
    c.drawLine(x - 38, G - SEAT, x - 44, G - SEAT - 120, P((110, 76, 54), stroke=10))
    for lx in (x - 32, x + 32): c.drawLine(lx, G - SEAT + 12, lx, G, P(INK, stroke=6))


def desk(c, x0, x1, drawer_open=0.0):
    top = G - DESK_H
    c.drawRect(skia.Rect.MakeLTRB(x0 - 20, top, x1 + 20, top + 18), P((140, 96, 64)))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 20, top, x1 + 20, top + 18), P(INK, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(x1 - 70, top + 18, x1 + 10, top + 58), P((128, 88, 60)))
    c.drawRect(skia.Rect.MakeLTRB(x1 - 70, top + 18, x1 + 10, top + 58), P(INK, stroke=3))
    c.drawLine(x1 - 46, top + 38, x1 - 14, top + 38, P(INK, stroke=4))
    for lx in (x0 - 8, x1 + 8): c.drawLine(lx, top + 18, lx, G, P(INK, stroke=8))


def book(c, x, y, flip=None, closed=0.0, glow=0.0):
    if closed > 0.5:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 46, y - 22, 92, 22), 4, 4), P((170, 60, 50)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 46, y - 22, 92, 22), 4, 4), P(INK, stroke=3))
        if glow > 0: c.drawCircle(x, y - 20, 80, P((255, 214, 140), 0.35 * glow, blur=30))
        return
    c.drawPath(poly([(x - 70, y), (x, y - 6), (x + 70, y), (x + 66, y - 16), (x, y - 22), (x - 66, y - 16)]), P((246, 240, 226)))
    c.drawPath(poly([(x - 70, y), (x, y - 6), (x + 70, y), (x + 66, y - 16), (x, y - 22), (x - 66, y - 16)]), P(INK, stroke=3))
    if flip is not None:                                                   # a page lifting from right to left
        a = math.pi * flip
        px = x + 66 * math.cos(a); py = y - 20 - 40 * math.sin(a)
        c.drawPath(poly([(x, y - 22), (px, py), (px, py + 10), (x, y - 8)]), P((255, 250, 236)))
        c.drawPath(poly([(x, y - 22), (px, py), (px, py + 10), (x, y - 8)]), P(INK, stroke=2))


def counter(c, x, y, s, col, a=1.0):
    w_ = skia.Font(F_SANS, 30).measureText(s) + 40
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w_ / 2, y - 26, w_, 52), 26, 26)
    c.drawRRect(rr, P((20, 20, 30), 0.85 * a)); c.drawRRect(rr, P(col, a, stroke=3))
    text(c, s, x, y + 11, F_SANS, 30, col, a)


def world(c, t):
    later = seg(t, SKIP0, SKIP0 + 0.6)
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, G)], [C((44, 40, 58)), C((86, 66, 70))])
    c.drawRect(skia.Rect.MakeLTRB(-400, -200, W + 400, G), skia.Paint(Shader=sh))
    # bookshelves
    rng = np.random.default_rng(9)
    for sx in (-120, 870):
        c.drawRect(skia.Rect.MakeLTRB(sx, G - 820, sx + 260, G), P((90, 62, 46)))
        for sy in range(G - 800, G - 40, 130):
            c.drawRect(skia.Rect.MakeLTRB(sx + 10, sy + 110, sx + 250, sy + 120), P((60, 40, 30)))
            bx = sx + 14
            while bx < sx + 240:
                bw = int(rng.integers(14, 26)); bh = int(rng.integers(70, 108))
                col = [(150, 70, 60), (70, 100, 130), (170, 140, 80), (90, 120, 80), (120, 90, 130)][int(rng.integers(0, 5))]
                c.drawRect(skia.Rect.MakeLTRB(bx, sy + 110 - bh, bx + bw, sy + 110), P(col, 0.9))
                bx += bw + 2
    # window with moon
    c.drawRect(skia.Rect.MakeLTRB(300, 620, 520, 900), P((30, 34, 70)))
    moon(c, 470 - 60 * later, 690 + 40 * later, 0.9)
    c.drawRect(skia.Rect.MakeLTRB(300, 620, 520, 900), P((80, 56, 46), stroke=12))
    c.drawLine(410, 620, 410, 900, P((80, 56, 46), stroke=8))
    # wall clock: 10:00 -> 12:00 during the skip
    cx, cy, r = 700, 760, 48
    c.drawCircle(cx, cy, r, P((240, 232, 220))); c.drawCircle(cx, cy, r, P(INK, stroke=5))
    hrs = 10 + 2 * seg(t, SKIP0, SKIP1) + 0.05 * t / T_END
    am = math.radians(hrs * 360 - 90); ah = math.radians(hrs * 30 - 90)
    c.drawLine(cx, cy, cx + 36 * math.cos(am), cy + 36 * math.sin(am), P(INK, stroke=4))
    c.drawLine(cx, cy, cx + 24 * math.cos(ah), cy + 24 * math.sin(ah), P(INK, stroke=6))
    # floor
    c.drawRect(skia.Rect.MakeLTRB(-400, G, W + 400, H + 200), P((70, 48, 40)))
    for k in range(-400, W + 400, 90): c.drawLine(k, G, k - 60, H, P((52, 36, 30), 0.6, stroke=3))
    # desk lamps
    for lx, on in ((D_DESK[0] + 10, 0.6), (F_DESK[0] + 10, 0.8 + 0.4 * seg(t, TURN, TURN + 0.4))):
        top = G - DESK_H
        c.drawLine(lx, top, lx + 20, top - 110, P((60, 60, 70), stroke=6))
        c.drawPath(poly([(lx + 2, top - 100), (lx + 60, top - 130), (lx + 70, top - 96), (lx + 20, top - 86)]), P((40, 80, 70)))
        c.drawCircle(lx + 60, top - 60, 150, P((255, 214, 140), 0.12 * on, blur=50))
    chair(c, D_X); chair(c, F_X)
    desk(c, *D_DESK); desk(c, *F_DESK)
    top = G - DESK_H
    book(c, (D_DESK[0] + D_DESK[1]) / 2 + 20, top)
    book(c, (F_DESK[0] + F_DESK[1]) / 2 + 20, top, flip=flip_k(t), closed=seg(t, TURN, TURN + 0.2), glow=seg(t, TURN, TURN + 0.4))
    # her phone: on the desk, then slides into the drawer
    k = seg(t, 1.8, 2.3)
    if k < 1:
        px = lerp(F_DESK[0] + 10, F_DESK[1] - 30, k); py = lerp(top - 6, top + 40, seg(t, 2.1, 2.3))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px - 16, py - 8, 32, 8), 2, 2), P((30, 30, 40)))
    # finished pages stack grows beside her book
    n = f_pages(t)
    if n > 1:
        h = min(30, n / 7)
        c.drawRect(skia.Rect.MakeXYWH(F_DESK[1] - 30, top - h, 50, h), P((250, 246, 232)))
        c.drawRect(skia.Rect.MakeXYWH(F_DESK[1] - 30, top - h, 50, h), P(INK, stroke=2))
    return later


def frame(c, t):
    sway = 1 + 0.015 * math.sin(t * 0.8) + 0.05 * seg(t, TURN + 1.2, 13.6)
    c.save(); c.translate(540 + 6 * math.sin(t * 0.6), 1150); c.scale(1.3 * sway, 1.3 * sway); c.translate(-560, -(G - 160))
    world(c, t)
    lo = (1, -0.6)
    heads = {}
    d = distracted(t)
    jd = figure(c, d["x"], d["y"], d["p"], s=S, facing=d["f"], body=D_BODY, rim=((210, 220, 255), 0.5), light=lo, mode="hip")
    heads["d"] = jd["head"]
    if t > 0.75:                                                           # his phone, glowing blue on his face
        hx, hy = jd["hand_f"]
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(hx - 6, hy - 30, 14, 36), 3, 3), P((30, 30, 40)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(hx - 4, hy - 27, 10, 28), 2, 2), P((120, 190, 255)))
        c.drawCircle(hx, hy - 20, 70, P((110, 170, 255), 0.25, blur=26))
    fo = focused(t)
    jf = figure(c, fo["x"], fo["y"], fo["p"], s=S, facing=fo["f"], body=F_BODY, rim=((255, 220, 170), 0.6), light=lo, mode="hip")
    heads["f"] = jf["head"]
    plate_label(c, "DISTRACTED", heads["d"][0], heads["d"][1] - 80, GREY, 0.9)
    plate_label(c, "FOCUSED", heads["f"][0], heads["f"][1] - 80, AMBER, 0.95)
    top = G - DESK_H
    counter(c, (D_DESK[0] + D_DESK[1]) / 2 + 20, top - 230, "PAGE 1", GREY)
    n = f_pages(t)
    counter(c, (F_DESK[0] + F_DESK[1]) / 2 - 30, top - 230, "DONE ✓" if t >= TURN else f"PAGE {n}", AMBER)
    for ts, who, txt in ([] if COVER else TALK):
        if ts < t < ts + 1.6:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.3, ts + 1.6))
            hd = heads[who]
            bx = clamp(hd[0] + 10, 400, 440) if who == "d" else clamp(hd[0] - 40, 440, 600)
            bubble(c, bx, hd[1] - (330 if who == "d" else 250), txt, a, "speech", tail=(hd[0], hd[1] - 110), size=30, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    vignette(c, 0.32)
    if SKIP0 - 0.1 < t < SKIP0 + 1.8:
        a = seg(t, SKIP0 - 0.1, SKIP0 + 0.2) * (1 - seg(t, SKIP0 + 1.4, SKIP0 + 1.8))
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(320, 610, 440, 64), 32, 32)
        c.drawRRect(rr, P((20, 20, 30), 0.85 * a)); c.drawRRect(rr, P(AMBER, a, stroke=3))
        text(c, "2 HOURS LATER", 540, 654, F_SANS, 30, AMBER, a)
    grain(c, t, 0.03)
    end_text(c, t, 13.6, "He checked his phone 87 times.", "She put it away once.", "Guard your focus.", y=1430)


def events():
    ev = []
    for ts, _, _ in TALK: ev.append(["pop", ts])
    ev += [["slide", 2.0], ["slide", SKIP0], ["thud", TURN], ["sunrise", TURN - 0.2], ["summit", TURN + 0.5], ["text", 13.6], ["text2", 14.4]]
    return ev


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 0.9, 2.0, 2.6, 3.4, 4.4, 6.6, 8.8, 9.8, 10.6, 12.0, 14.4, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore()
            series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)
        stills(opening, ts, "check/ep23")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs[:40]))
    else:
        finish_v2("Folge23_Focused", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
