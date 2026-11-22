"""Episode 26 v2 (TikTok: Part 23): SPENDER vs SAVER – promised by Part 22 ("the one who saves $1 a day"). Retention-Standard v2.
Frame 0: he feeds $1 into a soda machine (clunk), she drops $1 into a glass jar (clink).
Time-lapse DAY 1 → DAY 365: his empty cans pile up, her jar fills (SPENT $365 vs SAVED $365).
TURN 6.4 s: she tips the full jar – a shiny new bike pops up next to her ("$365").
Second turn: he turns out his empty pockets, then grabs an empty jar of his own.
Loop: he drops his first $1 into his own jar → same clink as frame 0."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 23                     # TikTok part number (internal episode 26)
TURN = 6.4
LAPSE0, LAPSE1 = 2.2, 5.2      # DAY 1 -> DAY 365
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
HX = 55                        # spender (faces the machine on the left)
SX = 318                       # saver (faces her table on the left)
MACH = (-60, 12)               # soda machine x range
TABLE = (178, 270)
TABLE_H = 112
JAR = (222, G - TABLE_H)
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Same $1. Every single day.\nWho has more after a year?"
CTA = "Part 24 next:\nthe one who goes all in on day 1"
END_TXT = "Small money. Big habit."
TALK = [(1.15, "h", "Just one soda."), (5.35, "h", "Where'd it go?"), (7.6, "s", "Start with $1.")]
COINS = [0.0, 1.1] + [LAPSE0 + 0.38 * i for i in range(8)]       # her drops (his buys happen at the same beats)


def day(t): return 1 + int(364 * seg(t, LAPSE0, LAPSE1) ** 1.2)


def money(t):
    if t < LAPSE0: return sum(1 for s in COINS[:2] if t >= s)
    return min(365, day(t))


def beat_k(t, lead=0.25):
    k = 0.0
    for s in COINS:
        k = max(k, seg(t, s - lead, s) * (1 - seg(t, s + 0.1, s + 0.3)))
    return k


# ------------------------------------------------------------------ characters
def spender(t):
    p = stand()
    if t < LAPSE1:                                                        # feeds the machine on every beat, drinks in between
        p = mix(p, dict(offer(), arm_f=85, elb_f=10, head=-4), beat_k(t))
        if t > 0.35 and t < LAPSE1: p = dict(p, arm_b=lerp(p["arm_b"], 150, 0.5 + 0.5 * math.sin(t * 6)), elb_b=lerp(p["elb_b"], 120, 0.5 + 0.5 * math.sin(t * 6)))
    if LAPSE1 <= t < 7.3: p = mix(p, shrug(1.0), seg(t, LAPSE1 + 0.1, LAPSE1 + 0.4))                 # where did the money go?
    if 7.3 <= t < 8.6: p = mix(shrug(1.0), dict(stand(), head=-8, lean=-4), seg(t, 7.3, 7.6))        # looks at her bike
    if 8.6 <= t < 9.6: p = mix(stand(), dict(crouch(), arm_f=60, elb_f=20, arm_b=50, elb_b=20), seg(t, 8.6, 8.9) * (1 - seg(t, 9.3, 9.6)))   # grabs a jar
    if t >= 9.6:                                                          # holds his own jar, drops the first $1 at the end (loop)
        p = dict(stand(), lean=6, head=8, arm_b=55, elb_b=80, arm_f=lerp(20, 80, seg(t, 11.9, 12.2)), elb_f=lerp(40, 70, seg(t, 11.9, 12.2)))
    f = 1 if 7.3 <= t < 8.6 else -1
    return dict(x=HX, p=p, f=f)


def saver(t):
    p = stand()
    if t < LAPSE1: p = mix(p, dict(offer(), arm_f=80, elb_f=14, head=-10), beat_k(t))
    if LAPSE1 <= t < TURN: p = mix(p, dict(crouch(), arm_f=70, elb_f=20, arm_b=60, elb_b=20), seg(t, LAPSE1 + 0.3, TURN - 0.2))   # picks up the full jar
    if TURN <= t < 7.4: p = mix(p, cheer(t), seg(t, TURN, TURN + 0.3) * (1 - seg(t, 7.1, 7.4)))
    if 7.4 <= t < 9.0: p = mix(p, dict(offer(), arm_f=100, elb_f=10, head=-6), seg(t, 7.4, 7.7) * (1 - seg(t, 8.7, 9.0)))   # points: "start with $1"
    if t >= 9.0: p = mix(p, dict(offer(), arm_f=80, elb_f=14, head=-10), beat_k(t + 0.0) if t > 11.5 else 0)
    return dict(x=SX, p=p, f=-1)


# ------------------------------------------------------------------ world
def can(c, x, y, rot=0.0, a=1.0):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-7, -18, 14, 18), 3, 3), P((210, 70, 70), a))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-7, -18, 14, 18), 3, 3), P(INK, a, stroke=2))
    c.restore()


def machine(c, t):
    x0, x1 = MACH
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, G - 290, x1, G), 8, 8), P((200, 60, 60)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, G - 290, x1, G), 8, 8), P(INK, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 10, G - 270, x1 - 26, G - 120), P((240, 230, 220)))
    for r in range(4):
        for k in range(2): can(c, x0 + 22 + k * 22, G - 236 + r * 36)
    c.drawRect(skia.Rect.MakeLTRB(x1 - 20, G - 220, x1 - 8, G - 160), P((60, 60, 70)))
    glow = beat_k(t, 0.1)
    if glow > 0: c.drawRect(skia.Rect.MakeLTRB(x1 - 20, G - 220, x1 - 8, G - 160), P((255, 230, 150), 0.6 * glow))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 10, G - 90, x1 - 10, G - 50), P((40, 40, 50)))
    text(c, "SODA $1", (x0 + x1) / 2, G - 104, F_CAP, 16, (255, 255, 255), 1.0)


def cans_pile(c, t):
    n = money(t) if t < LAPSE1 else 365
    shown = min(18, 2 + n // 22) if n > 2 else n
    for i in range(shown):
        x = 25 + (i * 37) % 120 - 20; y = G - 2 - (i // 6) * 14
        can(c, x, y, rot=90 if i % 3 else 70)


def jar(c, t):
    x, y = JAR
    fill = min(1.0, money(t) / 365) if t < TURN else 1.0
    tip = seg(t, TURN - 0.25, TURN)                                        # she tips it at the turn
    if t > TURN + 0.25: return
    c.save(); c.translate(x, y); c.rotate(-80 * tip)
    body = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-26, -76, 52, 76), 10, 10)
    c.drawRRect(body, P((210, 235, 245), 0.55))
    h = 70 * max(fill, 0.04)
    c.drawRect(skia.Rect.MakeXYWH(-22, -4 - h, 44, h), P((110, 180, 100)))
    for k in range(int(6 * fill)): c.drawCircle(-14 + (k * 11) % 30, -10 - k * 10, 6, P((240, 200, 80)))
    c.drawRRect(body, P(INK, stroke=3)); c.drawRect(skia.Rect.MakeXYWH(-20, -84, 40, 10), P((120, 90, 60)))
    c.restore()


def coin(c, t):
    for s in COINS + ([12.2] if True else []):
        k = seg(t, s - 0.22, s)
        if s - 0.22 < t < s + 0.02 and t < LAPSE1 or (s == 12.2 and s - 0.22 < t < s + 0.02):
            if s == 12.2: x0, y0, x1, y1 = HX + 30, G - 175, HX + 30, G - 120
            else: x0, y0, x1, y1 = SX - 70, G - 200, JAR[0], JAR[1] - 70
            x = lerp(x0, x1, k); y = lerp(y0, y1, k) - 30 * math.sin(math.pi * k)
            c.drawCircle(x, y, 8, P((240, 200, 80))); c.drawCircle(x, y, 8, P(INK, stroke=2))


def bike(c, t):
    if t < TURN: return
    k = seg(t, TURN, TURN + 0.2); pop = 1 + 0.4 * (1 - seg(t, TURN, TURN + 0.25))
    c.save(); c.translate(228, G - 2); c.scale(1.45 * k * pop, 1.45 * k * pop)
    for wx in (-38, 38): c.drawCircle(wx, -26, 24, P(INK, stroke=5)); c.drawCircle(wx, -26, 4, P(INK))
    c.drawPath(poly([(-38, -26), (-6, -70), (30, -70), (38, -26), (0, -26)]), P(AMBER, stroke=7))
    c.drawLine(30, -70, 36, -86, P(INK, stroke=5)); c.drawLine(-12, -78, 4, -78, P(INK, stroke=6))
    if t < TURN + 1.2: c.drawCircle(0, -50, 90, P((255, 220, 130), 0.4 * (1 - seg(t, TURN + 0.2, TURN + 1.2)), blur=30))
    c.restore()


def his_jar(c, t, hand):
    if t < 9.0: return
    a = seg(t, 9.0, 9.3)
    x, y = hand if t >= 9.6 else (HX + 25, G)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 18, y - 46, 36, 50), 8, 8), P((210, 235, 245), 0.55 * a))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 18, y - 46, 36, 50), 8, 8), P(INK, a, stroke=3))


def world(c, t):
    sh = skia.GradientShader.MakeLinear([(0, G - 800), (0, G)], [C((150, 190, 225)), C((235, 220, 200))])
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, 700, G), skia.Paint(Shader=sh))
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 420, 700, G - 60), P((214, 196, 172)))                 # shop wall
    for bx in range(-300, 700, 46): c.drawLine(bx, G - 420, bx, G - 60, P((190, 172, 150), stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(-300, G, 700, G + 500), P((150, 140, 128)))
    machine(c, t)
    x0, x1 = TABLE; top = G - TABLE_H
    ta = 1 - seg(t, TURN, TURN + 0.25)                                    # the table makes room for the bike
    if ta > 0:
        c.drawRect(skia.Rect.MakeLTRB(x0, top, x1, top + 14), P((150, 104, 70), ta)); c.drawRect(skia.Rect.MakeLTRB(x0, top, x1, top + 14), P(INK, ta, stroke=3))
        for px in (x0 + 8, x1 - 8): c.drawLine(px, top + 14, px, G, P((110, 76, 52), ta, stroke=9))
    cans_pile(c, t); jar(c, t); bike(c, t)


def to_screen(p): return (470 + (p[0] - 160) * K, 1440 + (p[1] - G) * K)


def frame(c, t):
    c.save(); c.translate(470, 1440); c.scale(K, K); c.translate(-160, -G)
    world(c, t)
    lo = (1, -0.6)
    h = spender(t)
    jh = figure(c, h["x"], G, h["p"], s=S, facing=h["f"], body=H_BODY, rim=((210, 220, 255), 0.5), light=lo)
    if 0.35 < t < LAPSE1: can(c, jh["hand_b"][0], jh["hand_b"][1] + 8)        # the soda in his other hand
    his_jar(c, t, jh["hand_b"])
    sp = saver(t)
    js = figure(c, sp["x"], G, sp["p"], s=S, facing=sp["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo)
    coin(c, t)
    c.restore()
    heads = {"h": to_screen(jh["head"]), "s": to_screen(js["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "SPENDER", GREY, size=28, a=na)
        chip(c, 720, 720, "SAVER", AMBER, size=28, a=na)
    vignette(c, 0.28)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    chip(c, 470, 640, f"DAY {day(t)}" + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=34 + 16 * lapse)
    m = money(t)
    chip(c, 250, 545, f"SPENT ${m}", GREY, size=36)
    chip(c, 715, 545, f"SAVED ${m}" if t < TURN else "NEW BIKE ✓", AMBER, size=36, pop=1 + 0.3 * (1 - seg(t, TURN, TURN + 0.25)) * (t > TURN))
    for ts, who, txt in TALK:
        if ts < t < ts + 1.35:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.15, ts + 1.35))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 220 if who == "h" else hx_ - 220, 300, 600)
            bubble(c, bx_, 722, txt, a, "speech", tail=(hx_ + (40 if who == "h" else -40), hy_ - 50), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", s, "money-coin-drop", -8 if s < 2 else -14] for s in COINS] + [["sfx", 12.2, "money-coin-drop", -8]]
    ev += [["sfx", LAPSE0, "riser-2s-soft", -12], ["sfx", LAPSE0, "data-countup-medium", -12]]
    ev += [["sfx", TURN - 0.1, "money-coins-pour", -6], ["thud", TURN + 0.2], ["summit", TURN + 0.2], ["text", END_T0]]
    return ev


if __name__ == "__main__":
    main("Folge26_Saver_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep26_v2",
         [0.0, 0.3, 1.3, 3.5, 5.5, 6.6, 7.8, 8.9, 10.0, 11.5, 12.2, 12.45])
