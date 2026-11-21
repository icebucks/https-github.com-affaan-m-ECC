"""Episode 24 (TikTok: Part 21): CONSUMER vs CREATOR – promised by the Part 20 cliffhanger ("the one who buys everything").
A weekend market, string lights, a "SALE" stall on the left. A wallet counter floats above each of them.
Consumer (grey): buys bag after bag at the SALE stall ("Ooh, 50% off!", "I deserve this.") – $500 → $40.
Creator (amber): builds her own little stall ("I'll make my own stall."), "2 WEEKS LATER" it is full of handmade mugs.
Turn: he walks over with all his bags – "Ooh, I need this!" – and his last $40 lands in HER jar: $0 vs $400. """
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 21                     # TikTok part number (internal episode 24)
G = 1300
S = 1.3
SKIP0, SKIP1 = 6.0, 8.0        # "2 weeks later"
TURN = 9.8                     # his money lands in her jar
C_BODY = (196, 202, 216)
R_BODY = (255, 226, 178)
SALE = (70, 250)               # SALE stall x range (left)
STALL = (600, 800)             # her stall x range (right)
RX = 700                       # creator stands behind her table
TABLE_H = 112
BUYS = [0.9, 2.1, 3.3, 4.5]    # his purchases before the skip
JAR = (770, G - TABLE_H)
TALK = [(1.0, "c", "Ooh, 50% off!"), (2.5, "r", "I'll make my own stall."), (4.2, "c", "I deserve this."),
        (SKIP1 + 0.5, "c", "Ooh, I need this!"), (TURN + 0.8, "r", "Thanks for buying!")]
HOOK = "Same market. Same weekend.\nOnly one went home richer."
FOCUS = (540, 1180)
COVER = False
CTA = "Part 22 next:\nthe one with 100 unfinished ideas"


def bags(t):
    if t >= SKIP0: return 6
    return sum(1 for b in BUYS if t >= b + 0.3)


def wallet(t):
    if t >= TURN: return 0
    if t >= SKIP0: return 40
    return [500, 380, 290, 150, 90][bags(t)]


def earned(t):
    if t >= TURN + 0.2: return 400
    if t >= SKIP0: return 360
    return 0


def build_k(t): return seg(t, 0.6, 5.6)          # her stall goes up


def cons_x(t):
    if t < SKIP1: return 280
    return lerp(280, 470, seg(t, SKIP1, SKIP1 + 1.2))


# ------------------------------------------------------------------ characters
def consumer(t):
    x = cons_x(t)
    if SKIP1 <= t < SKIP1 + 1.2:                                          # walks over to her stall, loaded with bags
        return dict(x=x, p=walk(t * 8, lean=4, stride=18, arm=10), f=1)
    if t < SKIP1:
        f = -1                                                            # faces the SALE stall
        p = stand()
        for b in BUYS:                                                    # hand out with the card, then back
            k = seg(t, b - 0.3, b) * (1 - seg(t, b + 0.4, b + 0.7))
            p = mix(p, dict(offer(), head=-4), k)
        if 4.0 < t < 5.6: p = mix(p, dict(p, head=-14, lean=-4), seg(t, 4.0, 4.3) * (1 - seg(t, 5.2, 5.6)))   # proud
        if t >= SKIP0: p = dict(stand(), lean=8, head=6)                  # tired, heavy bags
        return dict(x=x, p=p, f=f)
    p = stand()                                                           # at her stall: pays with his last money
    k = seg(t, TURN - 0.5, TURN - 0.2) * (1 - seg(t, TURN + 0.4, TURN + 0.8))
    p = mix(p, dict(offer(), head=-4), k)
    if t > TURN + 2.0: p = mix(p, dict(stand(), head=10, lean=6), seg(t, TURN + 2.0, TURN + 2.4))   # looks at his empty wallet
    return dict(x=x, p=p, f=1)


def creator(t):
    if t < SKIP0:                                                         # builds: hammering
        k = build_k(t)
        if 0.6 < t < 5.6:
            sw = 0.5 + 0.5 * math.sin(t * 9)
            p = dict(stand(), lean=10, head=10, arm_f=lerp(60, 140, sw), elb_f=lerp(80, 20, sw))
        else:
            p = stand()
        return dict(x=RX, p=p, f=-1, hammer=0.6 < t < 5.6)
    p = stand()
    if TURN + 0.2 < t < TURN + 2.2: p = mix(p, cheer(t), seg(t, TURN + 0.2, TURN + 0.6) * (1 - seg(t, TURN + 1.6, TURN + 2.2)))
    elif t > SKIP1: p = mix(p, offer(), seg(t, SKIP1 + 0.8, SKIP1 + 1.2) * (1 - seg(t, TURN - 0.2, TURN + 0.2)))   # offers a mug
    return dict(x=RX, p=p, f=-1, hammer=False)


# ------------------------------------------------------------------ world
def mug(c, x, y, col, a=1.0):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 12, y - 26, 24, 26), 4, 4), P(col, a))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 12, y - 26, 24, 26), 4, 4), P(INK, a, stroke=2))
    c.drawCircle(x + 15, y - 14, 7, P(INK, a, stroke=3))


def bag(c, x, y, col):
    c.drawRect(skia.Rect.MakeXYWH(x - 15, y, 30, 34), P(col)); c.drawRect(skia.Rect.MakeXYWH(x - 15, y, 30, 34), P(INK, stroke=2))
    c.drawArc(skia.Rect.MakeXYWH(x - 9, y - 10, 18, 20), 180, 180, False, P(INK, stroke=3))


def counter(c, x, y, s, col, a=1.0):
    w_ = skia.Font(F_SANS, 34).measureText(s) + 44
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w_ / 2, y - 28, w_, 56), 28, 28)
    c.drawRRect(rr, P((20, 20, 30), 0.85 * a)); c.drawRRect(rr, P(col, a, stroke=3))
    text(c, s, x, y + 12, F_SANS, 34, col, a)


def sale_stall(c):
    x0, x1 = SALE
    top = G - TABLE_H
    c.drawRect(skia.Rect.MakeLTRB(x0 - 10, top, x1 + 10, top + 16), P((150, 100, 70))); c.drawRect(skia.Rect.MakeLTRB(x0 - 10, top, x1 + 10, top + 16), P(INK, stroke=3))
    c.drawRect(skia.Rect.MakeLTRB(x0, top + 16, x1, G), P((190, 60, 60))); c.drawRect(skia.Rect.MakeLTRB(x0, top + 16, x1, G), P(INK, stroke=3))
    for px in (x0, x1): c.drawLine(px, top, px, top - 230, P((90, 70, 54), stroke=8))
    for i in range(6):                                                    # striped awning
        sx = x0 - 20 + i * (x1 - x0 + 40) / 6
        c.drawRect(skia.Rect.MakeXYWH(sx, top - 260, (x1 - x0 + 40) / 6, 44), P((230, 70, 70) if i % 2 == 0 else (250, 246, 236)))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 20, top - 260, x1 + 20, top - 216), P(INK, stroke=3))
    text(c, "SALE 50%", (x0 + x1) / 2, top + 72, F_CAP, 34, (255, 240, 200), 1.0)
    for i in range(5): bag(c, x0 + 20 + i * 36, top - 34, [(120, 170, 220), (230, 180, 80), (160, 120, 200), (120, 200, 150), (240, 140, 120)][i])


def her_stall(c, t):
    k = 1.0 if t >= SKIP0 else build_k(t)
    x0, x1 = STALL
    top = G - TABLE_H
    if k > 0.15:
        for px in (x0 + 10, x1 - 10): c.drawLine(px, top + 10, px, G, P((120, 84, 56), stroke=10))
    if k > 0.35:
        c.drawRect(skia.Rect.MakeLTRB(x0 - 10, top, x1 + 10, top + 18), P((170, 120, 80))); c.drawRect(skia.Rect.MakeLTRB(x0 - 10, top, x1 + 10, top + 18), P(INK, stroke=3))
        cl = seg(k, 0.35, 0.5)                                            # front cloth hides her legs
        c.drawRect(skia.Rect.MakeLTRB(x0, top + 18, x1, lerp(top + 18, G, cl)), P((70, 110, 90)))
        c.drawRect(skia.Rect.MakeLTRB(x0, top + 18, x1, lerp(top + 18, G, cl)), P(INK, stroke=3))
    if k > 0.55:
        for px in (x0, x1): c.drawLine(px, top, px, top - 230, P((120, 84, 56), stroke=8))
    if k > 0.75:
        for i in range(6):
            sx = x0 - 20 + i * (x1 - x0 + 40) / 6
            c.drawRect(skia.Rect.MakeXYWH(sx, top - 260, (x1 - x0 + 40) / 6, 44), P(AMBER if i % 2 == 0 else (250, 246, 236)))
        c.drawRect(skia.Rect.MakeLTRB(x0 - 20, top - 260, x1 + 20, top - 216), P(INK, stroke=3))
    if k > 0.9:
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((x0 + x1) / 2 - 100, top - 206, 200, 46), 8, 8)
        c.drawRRect(rr, P((60, 44, 34))); c.drawRRect(rr, P(INK, stroke=3))
        text(c, "HANDMADE", (x0 + x1) / 2, top - 172, F_CAP, 28, AMBER, 1.0)
    n = int(2 + 5 * seg(t, SKIP0, SKIP0 + 0.6)) if t >= SKIP0 else (1 if k > 0.95 else 0)
    for i in range(n): mug(c, x0 + 22 + i * 30, top, [(240, 180, 90), (120, 180, 220), (230, 120, 110), (150, 200, 140)][i % 4])
    if t >= SKIP0 or k > 0.95:                                            # money jar
        jx, jy = JAR
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(jx - 22, jy - 52, 44, 52), 8, 8), P((200, 230, 240), 0.7))
        fill = 0.1 + 0.7 * seg(t, SKIP0, SKIP0 + 0.6) + 0.2 * seg(t, TURN, TURN + 0.3)
        c.drawRect(skia.Rect.MakeXYWH(jx - 18, jy - 4 - 44 * fill, 36, 44 * fill), P((90, 170, 90)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(jx - 22, jy - 52, 44, 52), 8, 8), P(INK, stroke=3))


def world(c, t):
    eve = seg(t, SKIP0, SKIP1)
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, G)], [C(lerpc((150, 190, 230), (90, 80, 140), eve)), C(lerpc((240, 226, 200), (250, 170, 120), eve))])
    c.drawRect(skia.Rect.MakeLTRB(-400, -200, W + 400, G), skia.Paint(Shader=sh))
    sun(c, 300 + 300 * eve, 640 + 260 * eve, 0.85, r=56)
    for hx, hw, hh, col in ((-160, 260, 520, (180, 150, 130)), (870, 300, 560, (160, 140, 160))):
        c.drawRect(skia.Rect.MakeLTRB(hx, G - hh, hx + hw, G), P(lerpc(col, (100, 86, 110), eve * 0.6)))
        c.drawRect(skia.Rect.MakeLTRB(hx, G - hh, hx + hw, G), P(INK, stroke=4))
    # string lights across the market
    for i in range(18):
        x = -40 + i * 66; y = 760 + 40 * math.sin(i / 17 * math.pi)
        on = 0.35 + 0.65 * eve
        c.drawCircle(x, y, 7, P((255, 214, 140), on)); c.drawCircle(x, y, 22, P((255, 214, 140), 0.3 * on, blur=10))
    c.drawPath(poly([(-40 + i * 66, 760 + 40 * math.sin(i / 17 * math.pi) - 6) for i in range(18)], close=False), P((60, 50, 50), stroke=2))
    haze(c, G - 40, lerpc((230, 220, 210), (250, 170, 130), eve), 0.25)
    c.drawRect(skia.Rect.MakeLTRB(-400, G, W + 400, H + 200), P((150, 140, 128)))
    for k in range(-400, W + 400, 80): c.drawLine(k, G, k - 50, H, P((120, 110, 100), 0.5, stroke=3))
    sale_stall(c)


def frame(c, t):
    sway = 1 + 0.015 * math.sin(t * 0.8) + 0.05 * seg(t, TURN + 1.2, 13.6)
    c.save(); c.translate(540 + 6 * math.sin(t * 0.6), 1150); c.scale(1.22 * sway, 1.22 * sway); c.translate(-505, -(G - 170))
    world(c, t)
    lo = (1, -0.6)
    heads = {}
    r = creator(t)
    jr = figure(c, r["x"], G, r["p"], s=S, facing=r["f"], body=R_BODY, rim=((255, 220, 170), 0.6), light=lo)
    heads["r"] = jr["head"]
    if r["hammer"]:
        hx, hy = jr["hand_f"]
        c.drawLine(hx, hy, hx - 10, hy - 34, P((120, 84, 56), stroke=6)); c.drawRect(skia.Rect.MakeXYWH(hx - 26, hy - 44, 32, 14), P((90, 90, 100)))
    her_stall(c, t)                                                       # the table hides her legs
    cs = consumer(t)
    jc = figure(c, cs["x"], G, cs["p"], s=S, facing=cs["f"], body=C_BODY, rim=((210, 220, 255), 0.5), light=lo)
    heads["c"] = jc["head"]
    cols = [(120, 170, 220), (230, 180, 80), (160, 120, 200), (120, 200, 150), (240, 140, 120), (200, 200, 120)]
    hb = jc["hand_b"]
    for i in range(bags(t)):                                              # the bags pile up on his arm
        bag(c, hb[0] - 18 + (i % 3) * 18, hb[1] - 6 + (i // 3) * 26, cols[i])
    if TURN - 0.25 < t < TURN + 0.1:                                       # his last coins fly into her jar
        k = seg(t, TURN - 0.25, TURN + 0.1)
        hx, hy = jc["hand_f"]
        for i in range(3):
            x = lerp(hx, JAR[0], k) + i * 6; y = lerp(hy, JAR[1] - 50, k) - 90 * math.sin(math.pi * k)
            c.drawCircle(x, y, 9, P((240, 200, 80))); c.drawCircle(x, y, 9, P(INK, stroke=2))
    plate_label(c, "CONSUMER", heads["c"][0], heads["c"][1] - 80, GREY, 0.9)
    plate_label(c, "CREATOR", heads["r"][0], min(heads["r"][1] - 80, G - TABLE_H - 300) if (t >= SKIP0 or build_k(t) > 0.75) else heads["r"][1] - 80, AMBER, 0.95)
    ca = seg(t, 1.3, 1.6)                                                 # counters appear after the hook
    counter(c, cons_x(t) - 20, G - 560, f"${wallet(t)}", (255, 120, 110) if wallet(t) < 100 else GREY, ca)
    counter(c, RX - 10, G - 560, f"${earned(t)}", AMBER, ca)
    for ts, who, txt in ([] if COVER else TALK):
        if ts < t < ts + 1.6:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.3, ts + 1.6))
            hd = heads[who]
            bx = clamp(hd[0] - 30, 230, 420) if who == "c" else clamp(hd[0] - 110, 430, 560)
            bubble(c, bx, hd[1] - 215, txt, a, "speech", tail=(hd[0], hd[1] - 60), size=30, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    vignette(c, 0.3)
    if SKIP0 - 0.1 < t < SKIP0 + 1.8:
        a = seg(t, SKIP0 - 0.1, SKIP0 + 0.2) * (1 - seg(t, SKIP0 + 1.4, SKIP0 + 1.8))
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(320, 610, 440, 64), 32, 32)
        c.drawRRect(rr, P((20, 20, 30), 0.85 * a)); c.drawRRect(rr, P(AMBER, a, stroke=3))
        text(c, "2 WEEKS LATER", 540, 654, F_SANS, 30, AMBER, a)
    grain(c, t, 0.03)
    end_text(c, t, 13.6, "He bought what others made.", "She made what others buy.", "Create more than you consume.", y=1430)


def events():
    ev = []
    for ts, _, _ in TALK: ev.append(["pop", ts])
    for b in BUYS: ev.append(["thud", b])
    ev += [["slide", SKIP0], ["sunrise", SKIP1], ["land", TURN], ["summit", TURN + 0.4], ["text", 13.6], ["text2", 14.4]]
    return ev


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 1.0, 2.6, 3.6, 4.4, 5.6, 6.6, 8.8, 9.9, 10.8, 12.0, 14.4, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore()
            series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)
        stills(opening, ts, "check/ep24")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs[:40]))
    else:
        finish_v2("Folge24_Creator", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
