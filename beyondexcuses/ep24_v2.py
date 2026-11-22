"""Episode 24 v2 (TikTok: Part 21): CONSUMER vs CREATOR – rebuilt to Retention-Standard v2 (episodes.md).
Weekend market. Frame 0: he swipes his card at the SALE stall (bag pops onto his arm), she hammers the first plank of her own stall.
Time-lapse DAY 1 → DAY 14: bag after bag, his wallet $500 → $40; her stall goes up, mugs appear, her jar $0 → $360.
TURN 6.5 s: he walks over – "I need this!" – and his last $40 lands in HER jar: $0 vs $400.
Second turn: she hands him her hammer – "Make one yourself." – he drops the bags and starts building his own crate.
Loop: he is back at the left, arm swinging, she works her stall → frame 0."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 21                     # TikTok part number (internal episode 24)
TURN = 6.5                     # his last money lands in her jar
LAPSE0, LAPSE1 = 2.2, 5.2      # DAY 1 -> DAY 14
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
TABLE = G - 112
CX0 = 60                       # his spot at the SALE stall
STALL = (205, 330)
RX = 275                       # she stands behind her table
JAR = (312, TABLE)
C_BODY = (196, 202, 216)
R_BODY = (255, 226, 178)
HOOK = "Same $500. Same weekend.\nWho goes home richer?"
CTA = "Part 22 next:\nthe one with 100 unfinished ideas"
END_TXT = "Make more than you buy."
TALK = [(1.1, "c", "Ooh, 50% off!"), (5.35, "c", "I need this!"), (7.5, "r", "Make one yourself.")]
BUYS = [0.3, 1.0, 1.7] + [LAPSE0 + 0.45 * i for i in range(7)]


def bags(t): return min(6, sum(1 for b in BUYS if t >= b + 0.15))


def wallet(t):
    if t >= TURN: return 0
    n = sum(1 for b in BUYS if t >= b + 0.15)
    return max(40, 500 - 46 * n)


def earned(t):
    if t >= TURN + 0.05: return 400
    return int(360 * seg(t, LAPSE0, LAPSE1))


def build_k(t): return 0.3 + 0.7 * seg(t, LAPSE0, LAPSE1) if t < LAPSE1 else 1.0


def day(t): return 1 + int(13 * seg(t, LAPSE0, LAPSE1)) if t < 8 else 14


def cons_x(t):
    x = CX0
    x = lerp(x, 150, seg(t, 5.15, 6.0))
    x = lerp(x, CX0 + 15, seg(t, 9.0, 9.9))
    x = lerp(x, CX0, seg(t, 11.7, 12.2))
    return x


def cons_f(t):
    f = -1
    f = lerp(f, 1, seg(t, 5.0, 5.3))
    f = lerp(f, -1, seg(t, 8.95, 9.25))
    return f


# ------------------------------------------------------------------ characters
def consumer(t):
    x = cons_x(t)
    if 5.15 < t < 6.0 or 9.0 < t < 9.9:
        return dict(x=x, p=walk(t * 8, lean=4, stride=18, arm=10), f=cons_f(t))
    p = stand()
    if t < 5.15:
        for b in BUYS:                                    # card out, then back
            k = seg(t, b - 0.22, b) * (1 - seg(t, b + 0.12, b + 0.3))
            p = mix(p, dict(offer(), head=-4), k)
        if LAPSE1 - 0.3 < t: p = mix(p, dict(stand(), lean=8, head=6), seg(t, LAPSE1 - 0.3, LAPSE1))
    elif t < 9.0:
        k = seg(t, TURN - 0.45, TURN - 0.25) * (1 - seg(t, TURN + 0.2, TURN + 0.5))     # pays with his last $40
        p = mix(p, dict(offer(), head=-4), k)
        p = mix(p, dict(stand(), head=14, lean=8), seg(t, TURN + 0.5, TURN + 0.8) * (1 - seg(t, 7.7, 8.0)))   # empty wallet
        p = mix(p, dict(offer(), head=0), seg(t, 8.2, 8.45) * (1 - seg(t, 8.65, 8.9)))     # takes the hammer
    else:                                                 # builds his own crate
        sw = 0.5 + 0.5 * math.sin((t - 9.9) * 9 - math.pi / 2)
        k = seg(t, 9.9, 10.2) * (1 - seg(t, 11.6, 12.0))
        p = mix(stand(), dict(stand(), lean=18, head=22, arm_f=lerp(30, 125, sw), elb_f=lerp(70, 20, sw)), k)
    return dict(x=x, p=p, f=cons_f(t))


def creator(t):
    if t < LAPSE1:                                        # hammering her stall
        rate = 9 if t < LAPSE0 else 18
        sw = 0.5 + 0.5 * math.sin(t * rate)
        return dict(p=dict(stand(), lean=10, head=10, arm_f=lerp(55, 140, sw), elb_f=lerp(80, 20, sw)), hammer=True)
    p = stand()
    if TURN + 0.05 < t < 7.4: p = mix(p, cheer(t), seg(t, TURN + 0.05, TURN + 0.35) * (1 - seg(t, 7.0, 7.4)))
    if 7.5 < t < 9.0: p = mix(p, offer(), seg(t, 7.7, 8.1) * (1 - seg(t, 8.65, 9.0)))   # hands him the hammer
    if t > 9.2:                                            # arranges her mugs
        sw = 0.5 + 0.5 * math.sin((t - 9.2) * 4)
        p = mix(p, dict(stand(), lean=12, head=14, arm_f=lerp(40, 75, sw), elb_f=lerp(50, 25, sw)), seg(t, 9.2, 9.5))
    return dict(p=p, hammer=7.7 < t < 8.6)


# ------------------------------------------------------------------ world
def mug(c, x, y, col, a=1.0):
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 9, y - 20, 18, 20), 3, 3)
    c.drawRRect(r, P(col, a)); c.drawRRect(r, P(INK, a, stroke=2)); c.drawCircle(x + 11, y - 11, 5, P(INK, a, stroke=2.5))


def bag(c, x, y, col):
    c.drawRect(skia.Rect.MakeXYWH(x - 12, y, 24, 28), P(col)); c.drawRect(skia.Rect.MakeXYWH(x - 12, y, 24, 28), P(INK, stroke=2))
    c.drawArc(skia.Rect.MakeXYWH(x - 7, y - 8, 14, 16), 180, 180, False, P(INK, stroke=2.5))


def hammer(c, hx, hy, ang=-0.3):
    ex, ey = hx + 30 * math.sin(ang), hy - 30 * math.cos(ang)
    c.drawLine(hx, hy, ex, ey, P((120, 84, 56), stroke=5))
    c.save(); c.translate(ex, ey); c.rotate(math.degrees(ang)); c.drawRect(skia.Rect.MakeXYWH(-13, -6, 26, 11), P((90, 90, 100))); c.restore()


def sale_stall(c):
    c.drawRect(skia.Rect.MakeLTRB(-200, TABLE, 10, TABLE + 14), P((150, 100, 70))); c.drawRect(skia.Rect.MakeLTRB(-200, TABLE, 10, TABLE + 14), P(INK, stroke=3))
    c.drawRect(skia.Rect.MakeLTRB(-190, TABLE + 14, 0, G), P((190, 60, 60))); c.drawRect(skia.Rect.MakeLTRB(-190, TABLE + 14, 0, G), P(INK, stroke=3))
    c.drawLine(0, TABLE, 0, G - 330, P((90, 70, 54), stroke=7))
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-76, G - 352, 84, 34), 6, 6)
    c.drawRRect(r, P((230, 70, 70))); c.drawRRect(r, P(INK, stroke=3))
    text(c, "SALE", -34, G - 326, F_CAP, 24, (255, 246, 220), 1.0)
    for i in range(4): bag(c, -150 + i * 34, TABLE - 28, [(120, 170, 220), (230, 180, 80), (160, 120, 200), (120, 200, 150)][i])


def her_stall(c, t):
    k = build_k(t)
    x0, x1 = STALL
    if k > 0.05:
        for px in (x0 + 8, x1 - 8): c.drawLine(px, TABLE + 10, px, G, P((120, 84, 56), stroke=9))
    if k > 0.2:
        c.drawRect(skia.Rect.MakeLTRB(x0, TABLE, x1, TABLE + 16), P((170, 120, 80))); c.drawRect(skia.Rect.MakeLTRB(x0, TABLE, x1, TABLE + 16), P(INK, stroke=3))
        cl = seg(k, 0.2, 0.45)
        c.drawRect(skia.Rect.MakeLTRB(x0 + 4, TABLE + 16, x1 - 4, lerp(TABLE + 16, G, cl)), P((70, 110, 90)))
        c.drawRect(skia.Rect.MakeLTRB(x0 + 4, TABLE + 16, x1 - 4, lerp(TABLE + 16, G, cl)), P(INK, stroke=3))
    if k > 0.55:
        for px in (x0, x1): c.drawLine(px, TABLE, px, lerp(TABLE, G - 330, seg(k, 0.55, 0.7)), P((120, 84, 56), stroke=7))
    if k > 0.75:
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0 - 6, G - 352, x1 - x0 + 12, 34), 6, 6)
        c.drawRRect(r, P((60, 44, 34))); c.drawRRect(r, P(INK, stroke=3))
        text(c, "HANDMADE", (x0 + x1) / 2, G - 326, F_CAP, 21, AMBER, seg(k, 0.75, 0.85))
    n = int(5 * seg(t, LAPSE0 + 1.0, LAPSE1)) if t < 9.2 else 5
    for i in range(n): mug(c, x0 + 16 + i * 17, TABLE, [(240, 180, 90), (120, 180, 220), (230, 120, 110), (150, 200, 140)][i % 4])
    if t < 7.7 and t > LAPSE1: hammer(c, x0 + 20, TABLE - 4, ang=1.45)    # her hammer lies on the table
    jx, jy = JAR                                            # money jar
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(jx - 16, jy - 40, 32, 40), 6, 6)
    c.drawRRect(r, P((200, 230, 240), 0.7))
    fill = 0.05 + 0.75 * seg(t, LAPSE0, LAPSE1) + 0.2 * seg(t, TURN, TURN + 0.2)
    c.drawRect(skia.Rect.MakeXYWH(jx - 13, jy - 3 - 32 * fill, 26, 32 * fill), P((90, 170, 90)))
    c.drawRRect(r, P(INK, stroke=3))


def crate(c, t):
    k = seg(t, 9.9, 12.4)
    if k <= 0: return
    x0 = -12
    for i in range(1 + int(3 * k)):                         # planks of his own crate
        r = skia.Rect.MakeXYWH(x0, G - 14 - i * 16, 70, 13)
        c.drawRect(r, P((170, 120, 80))); c.drawRect(r, P(INK, stroke=2))


def world(c, t):
    ev = 0.25 + 0.25 * math.sin(math.pi * 2 * (t - LAPSE0) / 1.5) if LAPSE0 < t < LAPSE1 else 0.0   # days fly by
    sh = skia.GradientShader.MakeLinear([(0, G - 700), (0, G)], [C(lerpc((150, 190, 230), (90, 80, 140), ev)), C(lerpc((240, 226, 200), (250, 170, 120), ev))])
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, 700, G), skia.Paint(Shader=sh))
    sx = -40 + ((t - LAPSE0) / 1.5 % 1) * 420 if LAPSE0 < t < LAPSE1 else 300
    sun(c, sx, G - 620 + 60 * math.sin(math.pi * ((t - LAPSE0) / 1.5 % 1)) if LAPSE0 < t < LAPSE1 else G - 620, 0.85, r=40)
    for hx, hw, hh, col in ((-200, 170, 470, (180, 150, 130)), (360, 220, 520, (160, 140, 160)), (30, 150, 380, (200, 170, 150))):
        c.drawRect(skia.Rect.MakeLTRB(hx, G - hh, hx + hw, G), P(lerpc(col, (110, 96, 120), ev)))
        c.drawRect(skia.Rect.MakeLTRB(hx, G - hh, hx + hw, G), P(INK, stroke=4))
        for wy in range(G - hh + 40, G - 60, 90):
            for wx in range(hx + 24, hx + hw - 30, 56): c.drawRect(skia.Rect.MakeXYWH(wx, wy, 26, 36), P((90, 90, 120), 0.6))
    for i in range(12):                                     # string lights
        x = -80 + i * 50; y = G - 440 + 26 * math.sin(i / 11 * math.pi)
        c.drawCircle(x, y, 5, P((255, 214, 140), 0.6 + 0.4 * ev)); c.drawCircle(x, y, 15, P((255, 214, 140), 0.25, blur=8))
    haze(c, G - 30, (240, 220, 200), 0.22)
    c.drawRect(skia.Rect.MakeLTRB(-300, G, 700, G + 500), P((150, 140, 128)))
    for k in range(-300, 700, 60): c.drawLine(k, G, k - 40, G + 400, P((120, 110, 100), 0.5, stroke=3))
    sale_stall(c)


def to_screen(p): return (470 + (p[0] - 160) * K, 1440 + (p[1] - G) * K)


def frame(c, t):
    c.save(); c.translate(470, 1440); c.scale(K, K); c.translate(-160, -G)
    world(c, t)
    crate(c, t)
    lo = (1, -0.6)
    r = creator(t)
    jr = figure(c, RX, G, r["p"], s=S, facing=-1, body=R_BODY, rim=((255, 220, 170), 0.6), light=lo)
    if r["hammer"]:
        hx, hy = jr["hand_f"]; hammer(c, hx, hy, ang=-0.4 if t < LAPSE1 else 0.6)
    her_stall(c, t)
    # dropped bags on the floor after he puts them down
    cols = [(120, 170, 220), (230, 180, 80), (160, 120, 200), (120, 200, 150), (240, 140, 120), (200, 200, 120)]
    if t >= 7.8:
        for i in range(6): bag(c, 100 + (i % 3) * 26 - (i // 3) * 12, G - 28 - (i // 3) * 26, cols[i])
    cs = consumer(t)
    jc = figure(c, cs["x"], G, cs["p"], s=S, facing=cs["f"], body=C_BODY, rim=((210, 220, 255), 0.5), light=lo)
    hb = jc["hand_b"]
    if t < 7.8:
        drop = seg(t, 7.5, 7.8)
        for i in range(bags(t)):                            # bags pile up on his arm
            pk = 1 + 0.4 * (1 - seg(t, BUYS[i] + 0.15, BUYS[i] + 0.35)) if i < len(BUYS) else 1
            bx, by = hb[0] - 14 + (i % 3) * 14, hb[1] - 4 + (i // 3) * 22 + 30 * drop
            c.save(); c.translate(bx, by); c.scale(pk, pk); bag(c, 0, 0, cols[i]); c.restore()
    if 8.6 < t < 11.8:
        hx, hy = jc["hand_f"]; hammer(c, hx, hy, ang=-0.4 if t > 9.9 else 0.3)
    if t >= 11.8: hammer(c, 22, G - 66, ang=1.45)                       # put down on his crate
    for b in BUYS:                                          # card swipe flash at the SALE stall
        if b - 0.05 < t < b + 0.15 and t < 5.15:
            hx, hy = jc["hand_f"]
            c.drawRect(skia.Rect.MakeXYWH(hx - 10, hy - 6, 20, 13), P((80, 140, 220)))
            c.drawCircle(hx, hy, 30, P((255, 240, 180), 0.5 * (1 - seg(t, b, b + 0.15)), blur=10))
    if TURN - 0.25 < t < TURN + 0.05:                       # his last coins fly into her jar
        k = seg(t, TURN - 0.25, TURN + 0.05)
        sx_, sy_ = jc["hand_f"]
        for j in range(3):
            cx_ = lerp(sx_, JAR[0], k) + j * 6; cy_ = lerp(sy_, JAR[1] - 44, k) - 60 * math.sin(math.pi * k) + j * 4
            c.drawCircle(cx_, cy_, 6, P((255, 210, 90))); c.drawCircle(cx_, cy_, 6, P(INK, stroke=2))
    c.restore()
    heads = {"c": to_screen(jc["head"]), "r": to_screen(jr["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "CONSUMER", GREY, size=28, a=na)
        chip(c, 720, 720, "CREATOR", AMBER, size=28, a=na)
    vignette(c, 0.3)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    chip(c, 480, 545, f"DAY {day(t)}" + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=36 + 16 * lapse)
    w = wallet(t)
    hit = max([1 - seg(t, b + 0.15, b + 0.4) for b in BUYS if t >= b + 0.15] + [0])
    chip(c, 230, 545 + 4 * math.sin(t * 60) * (TURN < t < TURN + 0.4), f"${w}", GREY, size=40, pop=1 + 0.15 * hit)
    e = earned(t)
    k = seg(t, TURN, TURN + 0.25)
    chip(c, 735, 545, f"${e}", AMBER, size=40 + 10 * (t > TURN), pop=1 + 0.3 * (1 - k) * (t > TURN))
    for ts, who, txt in TALK:
        if ts < t < ts + 1.35:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.15, ts + 1.35))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 220 if who == "c" else hx_ - 220, 300, 600)
            bubble(c, bx_, 612, txt, a, "speech", tail=(hx_ + (40 if who == "c" else -40), hy_ - 60), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", b, "money-register" if b < 2 else "data-tick", -8 if b < 2 else -12] for b in BUYS]
    ev += [["thud", 0.0], ["thud", 0.7]] + [["thud", LAPSE0 + 0.35 * i] for i in range(8)]
    ev += [["sfx", LAPSE0, "riser-2s-soft", -12], ["sfx", LAPSE0 + 1.0, "money-coins-pour", -12]]
    ev += [["step", 5.2 + 0.2 * i, 0] for i in range(4)] + [["step", 9.05 + 0.2 * i, 0] for i in range(4)]
    ev += [["sfx", TURN, "money-coin-drop", -6], ["summit", TURN + 0.2], ["thud", 7.8], ["slide", 8.4], ["text", END_T0]]
    ev += [["thud", 10.1 + 0.7 * i] for i in range(3)]
    return ev


if __name__ == "__main__":
    main("Folge24_Creator_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep24_v2",
         [0.0, 0.3, 1.3, 3.0, 5.5, 6.6, 7.8, 8.6, 10.3, 11.5, 12.0, 12.45])
