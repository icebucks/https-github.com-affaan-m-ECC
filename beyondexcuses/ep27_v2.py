"""Episode 27 v2 (TikTok: Part 24): DAY 1 HERO vs DAILY 1% – promised by Part 23 ("the one who goes all in on day 1"). Retention-Standard v2.
A gym. Frame 0: he rips a huge barbell up (strain), she lifts a tiny bar. At 1.1 s he drops it – THUD – back pain.
Time-lapse DAY 1 → DAY 100: he sits on the bench with an ice pack (cobweb grows), her plates grow every beat (20 → 100 kg).
TURN 6.4 s: she presses the big barbell overhead – "100 KG".
Second turn: he gets up, takes the tiny bar and does his first small rep.
Loop: his small lift at the end mirrors her small lift at frame 0."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 24                     # TikTok part number (internal episode 27)
TURN = 6.4
LAPSE0, LAPSE1 = 2.2, 5.2      # DAY 1 -> DAY 100
DROP = 1.1
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
HX = 0
SX = 345
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Same gym. Same 100 days.\nWho lifts more?"
CTA = "Part 25 next:\nthe one who only watches"
END_TXT = "1% a day beats 100% once."
TALK = [(1.3, "h", "Ouch. My back!"), (5.35, "h", "Next Monday..."), (7.6, "s", "Start light. Daily.")]
REPS = [0.0, 0.9] + [LAPSE0 + 0.38 * i for i in range(8)]


def day(t): return 1 + int(99 * seg(t, LAPSE0, LAPSE1))


def her_kg(t):
    if t >= TURN - 0.4: return 100
    return 20 + int(80 * seg(t, LAPSE0, LAPSE1))


def rep_k(t, reps=REPS):
    k = 0.0
    for s in reps:
        k = max(k, seg(t, s - 0.05, s + 0.25) * (1 - seg(t, s + 0.3, s + 0.45)))
    return k


DOWN = dict(stand(), lean=8, head=6, arm_f=25, elb_f=20, arm_b=25, elb_b=20, leg_f=10, leg_b=-10)
UP = dict(stand(), lean=-2, head=-10, arm_f=170, elb_f=4, arm_b=170, elb_b=4, leg_f=6, leg_b=-6)


# ------------------------------------------------------------------ characters
def hero(t):
    if t < DROP:                                                          # rips the huge bar up, shaking
        p = mix(DOWN, dict(UP, arm_f=150, arm_b=150, elb_f=25, elb_b=25), seg(t, 0.0, 0.6))
        p = dict(p, lean=p["lean"] + 3 * math.sin(t * 60))
        return dict(x=HX, p=p, f=1, hip=False)
    if t < LAPSE0:                                                        # drops it, holds his back
        p = mix(UP, dict(stand(), lean=28, head=18, arm_f=-40, elb_f=100, arm_b=-30, elb_b=100), seg(t, DROP, DROP + 0.3))
        return dict(x=HX, p=p, f=1, hip=False)
    if t < 8.2:                                                           # sits on the bench with an ice pack
        k = seg(t, LAPSE0, LAPSE0 + 0.3)
        p = mix(stand(), dict(sit(t), lean=16, head=14, arm_f=70, elb_f=110, arm_b=20, elb_b=40), k)
        if 6.5 < t < 8.2: p = dict(p, head=lerp(p["head"], -8, seg(t, 6.5, 6.8)))          # looks at her
        return dict(x=HX, p=p, f=1, hip=k > 0.5)
    k = seg(t, 8.2, 8.6)                                                  # gets up, picks the light bar, first small reps
    p = mix(dict(sit(t), lean=10), DOWN, k)
    if t > 9.0: p = mix(DOWN, dict(UP, arm_f=160, arm_b=160), rep_k(t, [9.6, 10.6, 11.6, 12.5]))
    return dict(x=HX, p=p, f=1, hip=k < 0.5)


def daily(t):
    p = mix(DOWN, UP, rep_k(t)) if t < TURN - 0.6 else DOWN
    if TURN - 0.6 <= t < 7.6: p = mix(DOWN, UP, seg(t, TURN - 0.4, TURN))                 # the big press
    if 7.6 <= t < 9.0: p = mix(UP, dict(offer(), arm_f=100, elb_f=10, head=-6), seg(t, 7.6, 7.9) * (1 - seg(t, 8.7, 9.0)))
    if t >= 9.0: p = mix(DOWN, UP, rep_k(t, [9.6, 10.6, 11.6, 12.5]))
    return dict(x=SX, p=p, f=-1)


# ------------------------------------------------------------------ world
def plate(c, x, y, r, col):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 7, y - r, 14, 2 * r), 4, 4), P(col))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 7, y - r, 14, 2 * r), 4, 4), P(INK, stroke=3))


def barbell(c, hf, hb, r, n=1, col=(60, 60, 70)):
    """seen from the side: the bar points at the camera, so only the plates show – as a disc at the hands"""
    (x1, y1), (x2, y2) = hf, hb
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    R = r * 1.25 + 4 * (n - 1)
    c.drawCircle(cx, cy, R, P(col)); c.drawCircle(cx, cy, R, P(INK, stroke=3))
    for i in range(1, n + 1): c.drawCircle(cx, cy, R * (1 - 0.18 * i), P(INK, 0.35, stroke=2))
    c.drawCircle(cx, cy, 6, P((170, 170, 180))); c.drawCircle(cx, cy, 6, P(INK, stroke=2))


def world(c, t):
    sh = skia.GradientShader.MakeLinear([(0, G - 800), (0, G)], [C((60, 64, 80)), C((110, 104, 112))])
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, 700, G), skia.Paint(Shader=sh))
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 300, 700, G - 120), P((70, 74, 92)))                   # mirror
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 300, 700, G - 120), P(INK, 0.5, stroke=3))
    for wx in range(-280, 700, 120): c.drawCircle(wx, G - 640, 70, P((255, 230, 180), 0.08, blur=40))
    c.drawRect(skia.Rect.MakeLTRB(-300, G, 700, G + 500), P((70, 70, 78)))
    for k in range(-300, 700, 70): c.drawLine(k, G, k - 40, G + 400, P((55, 55, 62), 0.6, stroke=3))
    # bench + cobweb + ice pack area
    c.drawRect(skia.Rect.MakeLTRB(HX - 46, G - 60, HX + 54, G - 46), P((50, 50, 60))); c.drawLine(HX - 30, G - 46, HX - 30, G, P(INK, stroke=6)); c.drawLine(HX + 40, G - 46, HX + 40, G, P(INK, stroke=6))
    web = seg(t, LAPSE0 + 0.5, LAPSE1)
    if web > 0 and t < 8.4:
        cx, cy = HX - 40, G - 330
        for i in range(6):
            ang = math.radians(-90 + i * 30)
            c.drawLine(cx, cy, cx + 90 * web * math.cos(ang), cy - 90 * web * math.sin(ang) * -1, P((235, 235, 245), 0.6, stroke=1.5))
        for r_ in (25, 50, 75):
            if r_ < 90 * web: c.drawArc(skia.Rect.MakeXYWH(cx - r_, cy - r_, 2 * r_, 2 * r_), -90, 180, False, P((235, 235, 245), 0.5, stroke=1.5))
    # the huge barbell he dropped lies on the floor after the drop
    if t >= DROP + 0.25 and t < 8.6:
        barbell(c, (HX + 120, G - 44), (HX + 140, G - 44), 34, 3, (200, 60, 60))


def to_screen(p): return (470 + (p[0] - 160) * K, 1440 + (p[1] - G) * K)


def frame(c, t):
    c.save(); c.translate(470, 1440); c.scale(K, K); c.translate(-160, -G)
    world(c, t)
    lo = (1, -0.6)
    h = hero(t)
    jh = figure(c, h["x"], G - 52 if h.get("hip") else G, h["p"], s=S, facing=h["f"], body=H_BODY, rim=((210, 220, 255), 0.5), light=lo,
                mode="hip" if h.get("hip") else "feet")
    if t < DROP + 0.25:                                                   # the huge bar in his hands, falling at the drop
        fall = seg(t, DROP, DROP + 0.25)
        hf, hb = jh["hand_f"], jh["hand_b"]
        barbell(c, (hf[0], lerp(hf[1], G - 30, fall)), (hb[0], lerp(hb[1], G - 30, fall)), 34, 3, (200, 60, 60))
    if LAPSE0 <= t < 8.2:                                                 # ice pack on his back
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(jh["hand_f"][0] - 14, jh["hand_f"][1] - 10, 28, 20), 6, 6), P((150, 210, 240)))
    if t >= 8.6:
        barbell(c, jh["hand_f"], jh["hand_b"], 14, 1, (90, 160, 220))      # his light bar
    d = daily(t)
    jd = figure(c, d["x"], G, d["p"], s=S, facing=d["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo)
    kg = her_kg(t)
    r = 14 + 20 * (kg - 20) / 80
    barbell(c, jd["hand_f"], jd["hand_b"], r, 1 + int(2 * (kg - 20) / 80), AMBER if kg >= 100 else (90, 160, 220))
    if TURN < t < TURN + 1.0:
        k = seg(t, TURN, TURN + 1.0); hx, hy = jd["hand_f"]
        for i in range(10):
            ang = i / 10 * 2 * math.pi; rr = 40 + 70 * k
            c.drawCircle(hx + rr * math.cos(ang), hy + rr * math.sin(ang), 5 * (1 - k) + 1, P((255, 220, 120), 1 - k))
    c.restore()
    heads = {"h": to_screen(jh["head"]), "s": to_screen(jd["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "DAY 1 HERO", GREY, size=28, a=na)
        chip(c, 720, 720, "DAILY 1%", AMBER, size=28, a=na)
    vignette(c, 0.28)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    chip(c, 470, 640, f"DAY {day(t)}" + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=34 + 16 * lapse)
    hk = "120 KG" if t < DROP + 0.3 else ("0 KG" if t < 8.6 else "20 KG")
    chip(c, 250, 545, hk, GREY, size=38, pop=1 + 0.3 * (1 - seg(t, DROP + 0.3, DROP + 0.55)) * (DROP + 0.3 < t < DROP + 0.6))
    chip(c, 715, 545, f"{kg} KG", AMBER, size=38, pop=1 + 0.35 * (1 - seg(t, TURN, TURN + 0.25)) * (t > TURN))
    for ts, who, txt in TALK:
        if ts < t < ts + 1.35:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.15, ts + 1.35))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 220 if who == "h" else hx_ - 220, 300, 600)
            bubble(c, bx_, 722, txt, a, "speech", tail=(hx_ + (40 if who == "h" else -40), hy_ - 50), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["thud", DROP + 0.25], ["sfx", DROP + 0.25, "cinematic-slam-big", -6]]
    ev += [["sfx", s, "tone-step-2", -14] for s in REPS[2:]]
    ev += [["sfx", LAPSE0, "riser-2s-soft", -12], ["sfx", LAPSE0, "data-countup-medium", -12]]
    ev += [["sfx", TURN, "tone-ding-high", -6], ["summit", TURN + 0.2], ["slide", 8.3], ["text", END_T0]]
    return ev


if __name__ == "__main__":
    main("Folge27_Daily1_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep27_v2",
         [0.0, 0.5, 1.3, 3.5, 5.5, 6.6, 7.8, 8.9, 10.0, 11.5, 12.2, 12.45])
