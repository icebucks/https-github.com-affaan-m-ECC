"""Episode 29 v2 (TikTok: Part 26): SODA vs WATER – promised by Part 25 ("soda every day vs water every day"). Retention-Standard v2.
A kitchen. Frame 0 (climax first): PSSHT – he cracks a soda, it sprays; she pours a glass of water.
Time-lapse DAY 1 → DAY 30: his cans tower up, his ENERGY bar sinks; her bottles line up, her bar fills.
TURN 6.4 s: his bar hits 0 – he slumps onto the counter (thud, zzz); her bar is full – she jumps.
Second turn: she slides a glass of water over; he drinks.
Loop: he cracks a WATER bottle at the end – same hiss as frame 0."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 26                     # TikTok part number (internal episode 29)
TURN = 6.4
LAPSE0, LAPSE1 = 2.2, 5.2      # DAY 1 -> DAY 30
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
HX = 40
SX = 320
COUNTER = (110, 250)           # kitchen counter between them
TOP = G - 120
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Same fridge. Same 30 days.\nWho has more energy?"
CTA = "Part 27 next:\nthe friend who's always '5 min away'"
END_TXT = "Your energy is a choice."
TALK = [(1.2, "h", "Just one more."), (5.35, "h", "So... tired..."), (7.6, "s", "Try this.")]
BEATS = [0.0, 1.0] + [LAPSE0 + 0.38 * i for i in range(8)]


def day(t): return 1 + int(29 * seg(t, LAPSE0, LAPSE1))


def his_energy(t):
    if t < LAPSE0: return 0.8 - 0.1 * seg(t, 0.3, 1.2) + 0.1 * seg(t, 0.0, 0.3)     # sugar spike, then dip
    if t < TURN: return lerp(0.7, 0.0, seg(t, LAPSE0, TURN))
    if t < 8.6: return 0.0
    return lerp(0.0, 0.35, seg(t, 8.6, 10.5))


def her_energy(t):
    if t < LAPSE0: return 0.55
    return lerp(0.55, 1.0, seg(t, LAPSE0, LAPSE1))


def beat_k(t):
    k = 0.0
    for s in BEATS:
        k = max(k, seg(t, s - 0.2, s) * (1 - seg(t, s + 0.15, s + 0.35)))
    return k


DRINK = dict(stand(), lean=-6, head=-22, arm_f=150, elb_f=110, arm_b=10, elb_b=20)


# ------------------------------------------------------------------ characters
def soda(t):
    if t < 0.25: return dict(x=HX, p=dict(stand(), arm_f=70, elb_f=40, head=-8), f=1, hip=False)     # cracks it (frame 0)
    if t < TURN - 0.4:
        sl = 0.25 * seg(t, LAPSE0, TURN)                                   # gets slower and droopier
        p = mix(dict(stand(), lean=10 * sl * 4, head=14 * sl * 4), DRINK, 0.6 * (0.5 + 0.5 * math.sin(t * 5)) * (1 - 2 * sl))
        return dict(x=HX, p=p, f=1, hip=False)
    if t < 8.6:                                                            # crashes onto the counter
        p = mix(dict(stand(), lean=20, head=20), dict(stand(), lean=62, head=30, arm_f=95, elb_f=40, arm_b=80, elb_b=40, leg_f=8, leg_b=-8), seg(t, TURN - 0.4, TURN))
        return dict(x=HX, p=p, f=1, hip=False)
    k = seg(t, 8.6, 9.0)                                                   # straightens up, drinks the water
    p = mix(dict(stand(), lean=62, head=30, arm_f=95, elb_f=40, arm_b=80, elb_b=40), DRINK, k * (1 - seg(t, 10.6, 11.0)))
    if t > 11.0: p = mix(stand(), dict(stand(), arm_f=70, elb_f=40, head=-8), seg(t, 11.8, 12.2))      # opens a bottle (loop)
    return dict(x=HX, p=p, f=1, hip=False)


def water(t):
    p = mix(stand(), dict(offer(), arm_f=80, elb_f=20, head=-8), beat_k(t)) if t < LAPSE1 else stand()
    if LAPSE1 - 0.2 <= t < TURN: p = dict(stand(), lean=4 + 3 * math.sin(t * 12), head=-4, leg_f=6 + 10 * max(0, math.sin(t * 12)), leg_b=-6)   # bouncy
    if TURN <= t < 7.4:                                                    # jumps
        p = mix(stand(), cheer(t), seg(t, TURN, TURN + 0.25) * (1 - seg(t, 7.1, 7.4)))
    if 7.4 <= t < 9.0: p = mix(stand(), dict(offer(), arm_f=85, elb_f=10, head=-6), seg(t, 7.4, 7.7) * (1 - seg(t, 8.7, 9.0)))   # slides the glass
    return dict(x=SX, p=p, f=-1, jump=TURN <= t < 7.4)


# ------------------------------------------------------------------ world
def can(c, x, y, a=1.0):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 8, y - 22, 16, 22), 3, 3), P((210, 60, 60), a))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 8, y - 22, 16, 22), 3, 3), P(INK, a, stroke=2))


def bottle(c, x, y, a=1.0):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 7, y - 30, 14, 30), 4, 4), P((150, 210, 240), a))
    c.drawRect(skia.Rect.MakeXYWH(x - 4, y - 36, 8, 6), P((60, 120, 200), a))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 7, y - 30, 14, 30), 4, 4), P(INK, a, stroke=2))


def world(c, t):
    sh = skia.GradientShader.MakeLinear([(0, G - 800), (0, G)], [C((236, 226, 210)), C((214, 196, 172))])
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, 700, G), skia.Paint(Shader=sh))
    for y in range(G - 420, G - 120, 40): c.drawLine(-300, y, 700, y, P((255, 255, 255), 0.25, stroke=2))   # tiles
    c.drawRect(skia.Rect.MakeLTRB(-260, G - 330, -150, G), P((230, 232, 236))); c.drawRect(skia.Rect.MakeLTRB(-260, G - 330, -150, G), P(INK, stroke=4))   # fridge
    c.drawLine(-160, G - 260, -160, G - 200, P(INK, stroke=5))
    c.drawRect(skia.Rect.MakeLTRB(-300, G, 700, G + 500), P((160, 130, 100)))
    x0, x1 = COUNTER
    c.drawRect(skia.Rect.MakeLTRB(x0, TOP, x1, G), P((120, 140, 160))); c.drawRect(skia.Rect.MakeLTRB(x0 - 8, TOP - 12, x1 + 8, TOP), P((240, 240, 236)))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 8, TOP - 12, x1 + 8, G), P(INK, stroke=3))
    # his cans pile up on his side of the counter, her bottles on hers
    n = 1 if t < LAPSE0 else 1 + int(29 * seg(t, LAPSE0, LAPSE1))
    for i in range(min(n, 30)):
        col, row = i % 4, i // 4
        can(c, x0 + 6 + col * 17, TOP - 12 - row * 22)
    for i in range(min(n, 30)):
        col, row = i % 4, i // 4
        bottle(c, x1 - 6 - col * 16, TOP - 12 - row * 32 if row < 3 else TOP - 12 - 2 * 32)


def to_screen(p): return (470 + (p[0] - 160) * K, 1440 + (p[1] - G) * K)


def bar(c, x, y, v, col, label):
    w, h = 300, 34
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y, w, h), 17, 17), P((20, 20, 30), 0.85))
    if v > 0.01: c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2 + 4, y + 4, (w - 8) * v, h - 8), 13, 13), P(col))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y, w, h), 17, 17), P(col, stroke=3))
    text(c, label, x, y - 12, F_SANS, 28, col, 1.0)


def frame(c, t):
    c.save(); c.translate(470, 1440); c.scale(K, K); c.translate(-160, -G)
    world(c, t)
    lo = (1, -0.6)
    h = soda(t)
    jh = figure(c, h["x"], G, h["p"], s=S, facing=h["f"], body=H_BODY, rim=((210, 220, 255), 0.5), light=lo)
    hx, hy = jh["hand_f"]
    if t < 8.6: can(c, hx, hy + 6)
    elif t < 11.0: bottle(c, hx, hy + 10)
    else: bottle(c, hx, hy + 10)
    for s0 in (0.0, 12.15):                                                # spray / hiss on opening (frame 0 and the loop)
        if s0 <= t < s0 + 0.45:
            k = (t - s0) / 0.45
            for i in range(10):
                ang = math.radians(-60 - i * 6)
                col = (190, 120, 80) if s0 == 0.0 else (170, 220, 250)
                c.drawCircle(hx + 40 * k * math.cos(ang) * (1 + i % 3), hy - 40 * k * (1 + i % 4) * 0.6, 3, P(col, 1 - k))
    w = water(t)
    jy = G - 40 * math.sin(math.pi * seg(t, TURN, TURN + 0.5)) * w.get("jump")
    jw = figure(c, w["x"], jy, w["p"], s=S, facing=w["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo)
    if t < 7.4: bottle(c, jw["hand_f"][0], jw["hand_f"][1] + 10)
    if 7.4 <= t < 8.6:                                                     # the glass slides across the counter
        k = seg(t, 7.7, 8.5); gx = lerp(COUNTER[1] - 10, COUNTER[0] + 20, k)
        c.drawRect(skia.Rect.MakeXYWH(gx - 9, TOP - 34, 18, 22), P((170, 220, 250), 0.8)); c.drawRect(skia.Rect.MakeXYWH(gx - 9, TOP - 34, 18, 22), P(INK, stroke=2))
    if TURN <= t < 8.6:                                                    # zzz
        for i in range(3):
            ph = ((t - TURN) * 0.8 + i / 3) % 1
            text(c, "z", jh["head"][0] + 20 + 30 * ph, jh["head"][1] - 30 - 60 * ph, F_CAP, 22 + 8 * i, (90, 90, 120), 1 - ph)
    c.restore()
    heads = {"h": to_screen(jh["head"]), "s": to_screen(jw["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "SODA", GREY, size=28, a=na)
        chip(c, 720, 720, "WATER", AMBER, size=28, a=na)
    vignette(c, 0.25)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    chip(c, 470, 640, f"DAY {day(t)}" + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=34 + 16 * lapse)
    he = his_energy(t)
    bar(c, 250, 530, he, (255, 110, 100) if he < 0.25 else GREY, "ENERGY")
    bar(c, 715, 530, her_energy(t), AMBER, "ENERGY")
    for ts, who, txt in TALK:
        if ts < t < ts + 1.35:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.15, ts + 1.35))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 220 if who == "h" else hx_ - 220, 300, 600)
            bubble(c, bx_, 722, txt, a, "speech", tail=(hx_ + (40 if who == "h" else -40), hy_ - 50), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", 0.02, "whoosh-fast-medium", -6], ["sfx", 12.15, "whoosh-fast-medium", -6]]
    ev += [["sfx", s, "tone-step-1", -16] for s in BEATS[2:]]
    ev += [["sfx", LAPSE0, "riser-2s-soft", -12], ["sfx", LAPSE0, "data-decrease-medium", -12]]
    ev += [["thud", TURN], ["sfx", TURN, "tone-ding-high", -8], ["summit", TURN + 0.2], ["slide", 7.8], ["text", END_T0]]
    return ev


if __name__ == "__main__":
    main("Folge29_Water_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep29_v2",
         [0.0, 0.3, 1.3, 3.5, 5.5, 6.6, 7.9, 8.9, 10.0, 11.5, 12.2, 12.45])
