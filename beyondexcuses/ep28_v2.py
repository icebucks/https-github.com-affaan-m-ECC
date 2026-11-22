"""Episode 28 v2 (TikTok: Part 25): SPECTATOR vs PLAYER – promised by Part 24 ("the one who only watches"). Retention-Standard v2.
An outdoor court at sunset. Frame 0: she shoots (ball in the air, clang off the rim); he sits on the bench, phone in hand.
Time-lapse DAY 1 → DAY 60: her shots fly every beat, misses turn into makes (MADE 1/10 → 9/10); he scrolls, leaves pile up.
TURN 6.4 s: swish – net flash, "9/10".
Second turn: the ball bounces to him; he puts the phone down, stands up and takes his first shot.
Loop: his shot leaves the hands at the end like hers at frame 0."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 25                     # TikTok part number (internal episode 28)
TURN = 6.4
LAPSE0, LAPSE1 = 2.2, 5.2      # DAY 1 -> DAY 60
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
HX = -25                       # spectator on the bench (faces right)
SX = 195                       # player (faces right, hoop on the right)
HOOP = (318, G - 300)
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Same court. Same 60 days.\nWho can actually shoot?"
CTA = "Part 26 next:\nsoda every day vs water every day"
END_TXT = "Watch less. Play more."
TALK = [(1.2, "h", "I'll start tomorrow."), (5.35, "h", "Wow, she's good..."), (7.7, "s", "Your turn.")]
SHOTS = [0.0, 1.0] + [LAPSE0 + 0.38 * i for i in range(8)] + [TURN - 0.75]
HIS_SHOT = 11.7


def day(t): return 1 + int(59 * seg(t, LAPSE0, LAPSE1))


def made(t):
    if t >= TURN: return 9
    if t < LAPSE0: return 1
    return 1 + int(7 * seg(t, LAPSE0, LAPSE1))


def shot_k(t, shots):
    k = 0.0
    for s in shots:
        k = max(k, seg(t, s - 0.25, s) * (1 - seg(t, s + 0.12, s + 0.35)))
    return k


SET = dict(stand(), lean=-2, head=-12, arm_f=150, elb_f=60, arm_b=140, elb_b=70, leg_f=14, leg_b=-8, knee_f=30, knee_b=20)
REL = dict(stand(), lean=-4, head=-16, arm_f=165, elb_f=6, arm_b=150, elb_b=20, leg_f=4, leg_b=-4)


# ------------------------------------------------------------------ characters
def spectator(t):
    if t < 8.4:                                                           # sits, phone up, thumb scrolling
        p = dict(sit(t), lean=10, head=16, arm_f=70, elb_f=110 + 8 * math.sin(t * 10), arm_b=40, elb_b=90)
        if 6.5 < t < 8.4: p = dict(p, head=lerp(16, -6, seg(t, 6.5, 6.8)))  # looks up at the swish
        return dict(x=HX, p=p, f=1, hip=True)
    k = seg(t, 8.4, 8.8)
    p = mix(dict(sit(t), lean=10), stand(), k)
    if t > 9.2: p = mix(dict(stand(), arm_f=60, elb_f=60, arm_b=50, elb_b=60, head=-6), SET, seg(t, HIS_SHOT - 0.6, HIS_SHOT - 0.25))
    if t > HIS_SHOT - 0.25: p = mix(SET, REL, seg(t, HIS_SHOT - 0.25, HIS_SHOT))
    return dict(x=lerp(HX, 55, seg(t, 8.8, 9.6)), p=p, f=1, hip=k < 0.5)


def player(t):
    p = mix(dict(stand(), arm_f=60, elb_f=60, arm_b=50, elb_b=60, head=-6), SET, seg(t, 0.0, 0.01) if t < 0.2 else 0)
    k_set = max(shot_k(t, [s for s in SHOTS]), 0)
    p = mix(dict(stand(), arm_f=60, elb_f=60, arm_b=50, elb_b=60, head=-6), REL, k_set)
    if t < 0.12: p = REL
    if TURN < t < 7.5: p = mix(p, cheer(t), seg(t, TURN + 0.05, TURN + 0.35) * (1 - seg(t, 7.2, 7.5)))
    if 7.5 <= t < 9.2: p = mix(stand(), dict(offer(), arm_f=95, elb_f=10, head=-4), seg(t, 7.5, 7.8) * (1 - seg(t, 8.9, 9.2)))
    if t >= 9.2: p = dict(stand(), head=-4, arm_f=10, elb_f=40)
    f = 1 if t < 7.4 or t > 9.4 else -1                                    # turns to him for "Your turn."
    if 9.2 <= t < 9.9: p = walk(t * 9, stride=14, arm=14)
    return dict(x=lerp(SX, 255, seg(t, 9.2, 9.9)), p=p, f=f)


# ------------------------------------------------------------------ ball
def ball_pos(t):
    """returns (x, y) in world or None"""
    for i, s in enumerate(SHOTS):
        if s <= t < s + 0.6:
            k = (t - s) / 0.6
            make = (i >= 4) or (s >= TURN - 1)
            x0, y0 = SX + 18, G - 230
            x1, y1 = (HOOP[0], HOOP[1] + 10) if make else (HOOP[0] + 14, HOOP[1] - 8)
            return (lerp(x0, x1, k), lerp(y0, y1, k) - 110 * math.sin(math.pi * k)), make, k
    if TURN <= t < 8.6:                                                   # bounces to him after the swish
        k = seg(t, TURN + 0.1, 8.6)
        return (lerp(HOOP[0], HX + 40, k), G - 20 - 160 * abs(math.sin(k * math.pi * 3)) * (1 - k)), True, 1
    if HIS_SHOT - 0.6 <= t < HIS_SHOT: return None, False, 0
    if t >= HIS_SHOT:
        k = (t - HIS_SHOT) / 0.6
        return (lerp(85, HOOP[0] - 20, k), G - 230 - 110 * math.sin(math.pi * min(k, 1))), False, k
    return None, False, 0


# ------------------------------------------------------------------ world
def hoop(c, t):
    x, y = HOOP
    c.drawLine(x + 44, y - 70, x + 44, G, P((80, 80, 90), stroke=9))
    c.drawRect(skia.Rect.MakeXYWH(x + 22, y - 90, 18, 110), P((240, 240, 240))); c.drawRect(skia.Rect.MakeXYWH(x + 22, y - 90, 18, 110), P(INK, stroke=3))
    c.drawLine(x - 26, y, x + 22, y, P((230, 90, 40), stroke=6))
    flash = seg(t, TURN, TURN + 0.1) * (1 - seg(t, TURN + 0.3, TURN + 0.9))
    for i in range(5):
        xx = x - 22 + i * 10
        c.drawLine(xx, y + 2, xx + 3 * math.sin(t * 20) * flash, y + 34, P((255, 255, 255), 0.85, stroke=2))
    if flash > 0: c.drawCircle(x, y + 10, 70, P((255, 230, 150), 0.6 * flash, blur=26))


def world(c, t):
    sh = skia.GradientShader.MakeLinear([(0, G - 800), (0, G)], [C((120, 110, 170)), C((250, 170, 120))])
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, 700, G), skia.Paint(Shader=sh))
    sun(c, 180, G - 260, 0.7, r=60)
    for fx in range(-300, 700, 26): c.drawLine(fx, G - 260, fx + 26, G - 120, P((80, 80, 90), 0.4, stroke=2)); c.drawLine(fx + 26, G - 260, fx, G - 120, P((80, 80, 90), 0.4, stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(-300, G, 700, G + 500), P((190, 120, 80)))
    c.drawLine(-300, G + 60, 700, G + 60, P((255, 255, 255), 0.6, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(HX - 40, G - 52, HX + 60, G - 40), P((120, 80, 60))); c.drawLine(HX - 30, G - 40, HX - 30, G, P(INK, stroke=6)); c.drawLine(HX + 50, G - 40, HX + 50, G, P(INK, stroke=6))
    nl = int(12 * seg(t, LAPSE0, LAPSE1)) if t < 8.4 else 12               # leaves pile up at his feet
    for i in range(nl):
        c.drawOval(skia.Rect.MakeXYWH(HX - 30 + (i * 23) % 90, G - 8 - (i // 4) * 5, 16, 8), P([(200, 120, 50), (230, 170, 60), (170, 90, 50)][i % 3]))
    hoop(c, t)


def to_screen(p): return (470 + (p[0] - 160) * K, 1440 + (p[1] - G) * K)


def frame(c, t):
    c.save(); c.translate(470, 1440); c.scale(K, K); c.translate(-160, -G)
    world(c, t)
    lo = (-1, -0.6)
    h = spectator(t)
    jh = figure(c, h["x"], G - 54 if h.get("hip") else G, h["p"], s=S, facing=h["f"], body=H_BODY, rim=((210, 220, 255), 0.5), light=lo,
                mode="hip" if h.get("hip") else "feet")
    if t < 8.6:                                                           # his phone (glowing)
        hx, hy = jh["hand_f"]
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(hx - 6, hy - 26, 14, 30), 3, 3), P((30, 30, 40)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(hx - 4, hy - 23, 10, 24), 2, 2), P((120, 190, 255)))
    pl = player(t)
    jp = figure(c, pl["x"], G, pl["p"], s=S, facing=pl["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo)
    pos, mk, k = ball_pos(t)
    if pos is None and (HIS_SHOT - 0.6 <= t < HIS_SHOT): pos = ((jh["hand_f"][0] + jh["hand_b"][0]) / 2, (jh["hand_f"][1] + jh["hand_b"][1]) / 2 - 10)
    if pos is None and t < LAPSE1 + 1.3: pos = ((jp["hand_f"][0] + jp["hand_b"][0]) / 2, (jp["hand_f"][1] + jp["hand_b"][1]) / 2 - 10)
    if pos:
        c.drawCircle(pos[0], pos[1], 13, P((230, 120, 40))); c.drawCircle(pos[0], pos[1], 13, P(INK, stroke=3))
        c.drawLine(pos[0] - 13, pos[1], pos[0] + 13, pos[1], P(INK, stroke=2))
    c.restore()
    heads = {"h": to_screen(jh["head"]), "s": to_screen(jp["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "SPECTATOR", GREY, size=28, a=na)
        chip(c, 720, 720, "PLAYER", AMBER, size=28, a=na)
    vignette(c, 0.28)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    chip(c, 470, 640, f"DAY {day(t)}" + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=34 + 16 * lapse)
    chip(c, 250, 545, "SHOTS: 0" if t < HIS_SHOT else "SHOTS: 1", GREY, size=36, pop=1 + 0.3 * (1 - seg(t, HIS_SHOT, HIS_SHOT + 0.25)) * (t > HIS_SHOT))
    chip(c, 715, 545, f"MADE {made(t)}/10", AMBER, size=36, pop=1 + 0.35 * (1 - seg(t, TURN, TURN + 0.25)) * (t > TURN))
    for ts, who, txt in TALK:
        if ts < t < ts + 1.35:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.15, ts + 1.35))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 220 if who == "h" else hx_ - 220, 300, 600)
            bubble(c, bx_, 722, txt, a, "speech", tail=(hx_ + (40 if who == "h" else -40), hy_ - 50), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", s + 0.55, "tone-step-1" if i < 4 else "tone-step-3", -14] for i, s in enumerate(SHOTS[:-1])]
    ev += [["sfx", LAPSE0, "riser-2s-soft", -12], ["sfx", LAPSE0, "data-countup-medium", -12]]
    ev += [["sfx", TURN, "tone-ding-high", -6], ["summit", TURN + 0.2], ["thud", TURN + 0.5], ["thud", TURN + 0.9],
           ["slide", 8.5], ["text", END_T0], ["sfx", HIS_SHOT, "whoosh-medium-soft", -10]]
    return ev


if __name__ == "__main__":
    main("Folge28_Player_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep28_v2",
         [0.0, 0.3, 1.3, 3.5, 5.5, 6.5, 7.8, 8.9, 10.0, 11.5, 12.0, 12.45])
