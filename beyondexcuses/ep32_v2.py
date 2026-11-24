"""Episode 32 v2 (TikTok: Part 29): GYM SELFIE vs ACTUAL SET – promised by Part 28 ("the gym selfie guy").
Sport/discipline topic (+ shareable: you know exactly one gym friend like this). Retention-Standard v2.
Frame 0 (climax first): FLASH – his mirror selfie, the camera flash fills the frame (SELFIES 1).
Time-lapse DAY 1 → DAY 30: he poses and flashes (SELFIES → 300), she does alternating curls (REPS → 2,400), her dumbbells get heavier (5 → 12 KG).
TURN 6.4 s: DAY 30 – he finally grabs his dumbbell (still 5 KG, a cobweb on it) and can barely move it, while she curls 12 KG.
Second turn: he puts the phone down; she counts his first real rep.
Loop: back at the mirror – NOW he takes the selfie (after the set): FLASH = frame 0."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 29                     # TikTok part number (internal episode 32)
TURN = 6.4
LAPSE0, LAPSE1 = 2.2, 5.2      # DAY 1 -> DAY 30
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
CAMX = 190
HX = 70                        # him at the mirror
SX = 305                       # her at the rack
BENCH = (100, 170)
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Same gym. 30 days.\nWho actually changed?"
CTA = "Part 30 next:\nthe roommate and the dishes"
END_TXT = "Lift first. Post later."
TALK = [(1.0, "h", "Post first. Lift later."), (6.75, "h", "Wait... how?"), (8.4, "s", "Phone down. Rep one.")]
FLASHES = [0.0, 0.85, 2.3, 2.7, 3.1, 3.5, 3.9, 4.3, 4.7, 5.1]          # his selfie flashes


def day(t): return 1 + int(29 * seg(t, LAPSE0, LAPSE1))
def selfies(t): return 1 + (1 if t >= 0.85 else 0) + int(298 * seg(t, LAPSE0, LAPSE1))
def reps(t): return int(2400 * seg(t, LAPSE0, LAPSE1)) + (int(12 * seg(t, 0.3, LAPSE0)) if t < LAPSE0 else 0)
def her_kg(t): return 5 + int(7 * seg(t, LAPSE0, LAPSE1))


def flash(t):
    a = 0.0
    for f0 in FLASHES:
        if f0 <= t < f0 + 0.25: a = max(a, 1 - (t - f0) / 0.25)
    if t >= 12.2: a = max(a, seg(t, 12.2, 12.46))                                     # loop: his after-set selfie flash = frame 0
    return a


# ------------------------------------------------------------------ characters
SELFIE = dict(lean=-4, head=-6, arm_f=105, elb_f=70, arm_b=80, elb_b=125)            # phone up at the mirror, other arm flexed


def him(t):
    if t < 5.9:                                                            # mirror selfies, changes the flex a little
        w = 0.5 + 0.5 * math.sin(t * (9 if LAPSE0 < t < LAPSE1 else 3))
        p = dict(stand(), **SELFIE); p["elb_b"] = 110 + 30 * w; p["lean"] = -4 + 4 * w
        return dict(x=HX, p=p, f=-1, phone=True, db=False)
    if t < TURN:                                                           # turns to his dumbbell on the bench
        return dict(x=HX, p=mix(dict(stand(), **SELFIE), dict(stand(), lean=10, head=12), seg(t, 5.9, 6.3)), f=lerp(-1, 1, seg(t, 5.9, 6.2)), phone=True, db=False)
    if t < 7.7:                                                            # tries a curl with the dusty 5 kg: arm shakes, elbow barely bends
        sh = math.sin(t * 40) * 4
        p = dict(stand(), lean=-8, head=-10, arm_f=10, elb_f=35 + 15 * seg(t, TURN, 7.2) + sh, arm_b=30, elb_b=100)
        return dict(x=HX + 20, p=p, f=1, phone=True, db=True)
    if t < 8.3:                                                            # puts the phone down on the bench
        p = mix(dict(stand(), lean=-8, head=-10, arm_f=10, elb_f=40, arm_b=30, elb_b=100), dict(stand(), lean=24, head=16, arm_f=8, elb_f=20, arm_b=40, elb_b=30), seg(t, 7.7, 8.0))
        return dict(x=HX + 20, p=p, f=1, phone=t < 7.95, db=True)
    if t < 11.3:
        ph = (t - 8.3) / 1.4                                               # real curls, slow and full range
        curl = 0.5 - 0.5 * math.cos(2 * math.pi * min(ph, 2.0))
        p = dict(stand(), lean=-2, head=-6, arm_f=8, elb_f=12 + 125 * curl, arm_b=-4, elb_b=12)
        return dict(x=HX + 20, p=p, f=1, phone=False, db=True)
    k = seg(t, 11.3, 11.9)                                                 # loop: NOW the selfie – after the set (lift first, post later)
    p = mix(dict(stand(), lean=-2, head=-6, arm_f=8, elb_f=12, arm_b=-4, elb_b=12), dict(stand(), **SELFIE), k)
    return dict(x=lerp(HX + 20, HX, k), p=p, f=lerp(1, -1, seg(t, 11.3, 11.6)), phone=True, db=False)


def her(t):
    sp = 14 if LAPSE0 < t < LAPSE1 else 4.2                                # alternating curls (fast in the time-lapse)
    a = 0.5 - 0.5 * math.cos(t * sp); b = 0.5 - 0.5 * math.cos(t * sp + math.pi)
    if TURN + 1.2 < t:                                                     # pauses, counting for him; ends like frame 0 (a=0, b=1)
        k = seg(t, 11.5, 12.3)
        a, b = lerp(0.15, 0.0, k), lerp(0.15, 1.0, k)
    p = dict(stand(), lean=-2, head=-4, arm_f=8, elb_f=12 + 125 * a, arm_b=8, elb_b=12 + 125 * b)
    return dict(x=SX, p=p, f=-1, phone=False)


# ------------------------------------------------------------------ world
def gym(c, t):
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, 700, G), P((62, 66, 78)))
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, 700, G - 520), P((50, 52, 62)))
    for i in range(-2, 9):                                                 # ceiling lights
        c.drawRect(skia.Rect.MakeLTRB(i * 90 - 30, G - 560, i * 90 + 30, G - 552), P((240, 240, 255), 0.9))
        c.drawCircle(i * 90, G - 540, 30, P((240, 240, 255), 0.18, blur=14))
    m = skia.Rect.MakeLTRB(-60, G - 340, 30, G - 20)                       # the mirror behind him
    c.drawRect(m, P((150, 180, 205))); c.drawRect(m, P((210, 215, 225), stroke=6))
    for i in range(3): c.drawLine(-50 + i * 24, G - 300, -20 + i * 24, G - 340 + 20, P((230, 240, 255), 0.5, stroke=4))
    text(c, "NO SELFIES?", 210, G - 410, F_CAP, 18, (140, 145, 160), 0.0)
    for i in range(5):                                                     # dumbbell rack behind her
        y = G - 160 + i * 0  # one shelf
    c.drawRect(skia.Rect.MakeLTRB(340, G - 120, 470, G - 108), P((40, 40, 48)))
    for i in range(5): dumbbell(c, 352 + i * 26, G - 126, 4 + i * 1.6, (60, 60, 70))
    c.drawLine(345, G - 108, 345, G, P((40, 40, 48), stroke=6)); c.drawLine(465, G - 108, 465, G, P((40, 40, 48), stroke=6))
    c.drawRect(skia.Rect.MakeLTRB(-300, G, 700, G + 500), P((40, 42, 50)))
    for i in range(-3, 9): c.drawLine(i * 80, G, i * 80 - 40, G + 500, P((52, 54, 62), stroke=3))
    x0, x1 = BENCH                                                         # bench with his dusty dumbbell
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, G - 62, x1, G - 48), 5, 5), P((30, 30, 36)))
    c.drawLine(x0 + 10, G - 48, x0 + 10, G, P((80, 80, 90), stroke=5)); c.drawLine(x1 - 10, G - 48, x1 - 10, G, P((80, 80, 90), stroke=5))


def dumbbell(c, x, y, r, col=(70, 70, 80), label=None, a=1.0):
    c.drawLine(x - r * 1.6, y, x + r * 1.6, y, P((170, 170, 180), a, stroke=3))
    for sx in (-1, 1):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + sx * r * 1.6 - r * 0.45, y - r, r * 0.9, 2 * r), 2, 2), P(col, a))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + sx * r * 1.6 - r * 0.45, y - r, r * 0.9, 2 * r), 2, 2), P(INK, a, stroke=1.5))
    if label: text(c, label, x, y - r - 6, F_CAP, 13, (255, 255, 255), a, stroke=4)


def cobweb(c, x, y, a):
    if a <= 0: return
    for i in range(5):
        ang = math.pi * (0.15 + 0.17 * i)
        c.drawLine(x, y, x + 26 * math.cos(ang), y - 26 * math.sin(ang), P((230, 230, 240), 0.7 * a, stroke=1.2))
    for rr in (9, 17, 25):
        pth = skia.Path(); pth.addArc(skia.Rect.MakeXYWH(x - rr, y - rr, 2 * rr, 2 * rr), -153, 126); c.drawPath(pth, P((230, 230, 240), 0.6 * a, stroke=1.2))


def to_screen(p): return (470 + (p[0] - CAMX) * K, 1440 + (p[1] - G) * K)


def frame(c, t):
    c.save(); c.translate(470, 1440); c.scale(K, K); c.translate(-CAMX, -G)
    gym(c, t)
    lo = (1, -0.6)
    h = him(t)
    jh = figure(c, h["x"], G, h["p"], s=S, facing=h["f"], body=H_BODY, rim=((210, 220, 255), 0.5), light=lo)
    if h["phone"]:
        px, py = jh["hand_f"]
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px - 7, py - 26, 14, 28), 3, 3), P((30, 30, 40)))
    else:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(BENCH[1] - 30, G - 67, 24, 5), 2, 2), P((30, 30, 40)))   # phone on the bench
    if h["db"]:
        dumbbell(c, *jh["hand_f"], 6, label="5 KG")
        cobweb(c, jh["hand_f"][0] + 8, jh["hand_f"][1] - 4, 1 - seg(t, 8.6, 9.2))
    else:
        dumbbell(c, BENCH[0] + 40, G - 68, 6, label="5 KG")
        cobweb(c, BENCH[0] + 48, G - 72, seg(t, 3.0, 5.0) * (t < TURN))
    e = her(t)
    je = figure(c, e["x"], G, e["p"], s=S, facing=e["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo)
    kg = her_kg(t)
    r = 5 + 0.55 * (kg - 5)
    if e["phone"]:
        px, py = je["hand_f"]
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px - 7, py - 26, 14, 28), 3, 3), P((30, 30, 40)))
        dumbbell(c, SX + 30, G - 8, r)
    else:
        dumbbell(c, *je["hand_f"], r, label=f"{kg} KG")
        dumbbell(c, *je["hand_b"], r)
    c.restore()
    fa = flash(t)                                                          # camera flash
    if fa > 0:
        src = to_screen(jh["hand_f"])                                     # the flash lights him up (frame 0 and loop)
        c.drawCircle(src[0], src[1] - 30, 90 + 180 * fa, P((255, 255, 255), 0.8 * fa, blur=40))
        c.drawRect(skia.Rect.MakeLTRB(0, 0, 1080, 1920), P((255, 255, 255), 0.2 * fa))
    heads = {"h": to_screen(jh["head"]), "s": to_screen(je["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "GYM SELFIE", GREY, size=28, a=na)
        chip(c, 790, 720, "ACTUAL SET", AMBER, size=28, a=na)
    vignette(c, 0.25)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    if t < 9.6:
        chip(c, 540, 640, f"DAY {day(t)}" + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=34 + 16 * lapse)
        chip(c, 250, 545, f"SELFIES {selfies(t)}", GREY, size=34)
        chip(c, 790, 545, f"REPS {reps(t):,}", AMBER, size=34)
    if TURN <= t < 8.2:                                                    # the weigh-in
        a = seg(t, TURN, TURN + 0.1) * (1 - seg(t, 7.9, 8.2)); pop = 1 + 0.3 * (1 - seg(t, TURN, TURN + 0.25))
        chip(c, 250, 720, "5 KG → 5 KG", GREY, size=40, a=a, pop=pop)
        chip(c, 790, 720, "5 KG → 12 KG", AMBER, size=40, a=a, pop=pop)
    for ts, who, txt in TALK:
        if ts < t < ts + 1.3:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.1, ts + 1.3))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 230 if who == "h" else hx_ - 230, 320, 700)
            bubble(c, bx_, 900, txt, a, "speech", tail=(hx_ + (40 if who == "h" else -40), hy_ - 50), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", f0, "pop-small-in", -8] for f0 in FLASHES]              # shutter clicks
    ev += [["sfx", LAPSE0, "time-clock-fast", -10], ["sfx", LAPSE0, "data-countup-long", -14], ["sfx", LAPSE0, "riser-2s-soft", -12]]
    ev += [["sfx", TURN, "cinematic-slam-big", -10], ["thud", 7.95], ["sfx", 9.0, "tone-step-1", -8], ["sfx", 10.4, "tone-step-2", -8],
           ["sfx", 12.2, "pop-small-in", -6], ["text", END_T0]]
    return ev


if __name__ == "__main__":
    main("Folge32_GymSelfie_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep32_v2",
         [0.0, 0.4, 1.3, 2.9, 4.4, 5.6, 6.1, 6.6, 7.4, 8.1, 9.0, 10.3, 11.8, 12.3])
