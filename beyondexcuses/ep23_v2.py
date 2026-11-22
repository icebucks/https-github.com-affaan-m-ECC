"""Episode 23 v2 (TikTok: Part 20): DISTRACTED vs FOCUSED – rebuilt to Retention-Standard v2 (episodes.md).
One library table at night, they sit face to face. Frame 0: both phones buzz – he grabs his, she slides hers into the drawer.
Time-lapse 10 PM → 12 AM (clock chip, whirling wall clock): her pages fly (PAGE 1 → 212), a cobweb grows on his book.
TURN 6.6 s: she slams the finished book shut – DONE ✓. Second turn: he looks at the clock, then puts HIS phone in the drawer,
brushes off the cobweb and starts flipping; she opens book 2 at PAGE 1. Loop: his drawer buzzes again → frame 0."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 20                     # TikTok part number (internal episode 23)
TURN = 6.6                     # she slams the finished book shut
LAPSE0, LAPSE1 = 2.2, 5.4      # time-lapse 10:00 PM -> 12:00 AM
END_T0 = 9.6
G = 1300
S = 1.45
K = 2.1                        # camera ≈ 1.7× closer than Part 19
SEAT = 56
TOP = G - 118                  # table top
D_X, F_X = 22, 308              # hips: him left (facing right), her right (facing left)
D_BOOK, F_BOOK = 118, 212
D_PHONE, F_PHONE = 86, 250
D_BODY = (196, 202, 216)
F_BODY = (255, 226, 178)
HOOK = "Same book. Same 2 hours.\nWho actually finishes it?"
CTA = "Part 21 next:\nthe one who buys everything"
END_TXT = "Phone away. Pages turn."
TALK = [(1.15, "d", "Just one video."), (5.25, "d", "Wait... 2 hours?!"), (7.5, "f", "Phone in the drawer.")]


def path(t, keys):
    """eased piecewise path through (time, (x, y)) keys"""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t < t1:
            u = ease((t - t0) / (t1 - t0)); return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))
    return keys[-1][1]


def clock_h(t):                # hours after 10 PM
    return 2 * seg(t, LAPSE0, LAPSE1) ** 0.9 + 0.7 * seg(t, LAPSE1, T_END) * (T_END - LAPSE1) / 7


def f_pages(t):
    if t < LAPSE0: return 1
    if t < LAPSE1: return 1 + int(205 * (t - LAPSE0) / (LAPSE1 - LAPSE0))
    if t < TURN: return 211 if t < 6.1 else 212
    return 1


def d_pages(t):
    return 1 if t < 9.0 else 2 + int((t - 9.0) / 0.6)


def flip_u(t):
    """0..1 page sweep for her hand; fast during the time-lapse"""
    if LAPSE0 <= t < LAPSE1: return 0.5 - 0.5 * math.cos(2 * math.pi * (t - LAPSE0) / 0.25)
    if 5.75 <= t < 6.35: return math.sin(math.pi * (t - 5.75) / 0.6)            # the last page, slow
    if 10.6 <= t: return 0.5 - 0.5 * math.cos(2 * math.pi * (t - 10.6) / 1.4) if t < 12.0 else 0
    return 0


def d_flip(t):
    if 9.0 <= t < 12.0: return 0.5 - 0.5 * math.cos(2 * math.pi * (t - 9.0) / 0.6)
    return 0


# ------------------------------------------------------------------ characters
FACE_D = (52, G - 216)
def d_hand(t):
    keys = [(-0.3, (D_BOOK + 8, TOP - 4)), (0.35, (D_PHONE, TOP - 4)), (0.8, FACE_D), (5.2, FACE_D), (5.6, (66, G - 172)),
            (7.6, (66, G - 172)), (8.1, (80, TOP + 30)), (8.4, (80, TOP + 30)), (8.6, (D_BOOK + 30, TOP - 10)),
            (8.8, (D_BOOK - 10, TOP - 8)), (9.0, (D_BOOK + 8, TOP - 4))]
    x, y = path(t, keys)
    if 0.8 < t < 5.2:            # thumb-scrolling, laughing
        x += 2 * math.sin(t * 9); y += 3 * math.sin(t * 13) + (5 * math.sin(t * 30) if 3.0 < t < 4.4 else 0)
    u = d_flip(t)
    if u: x -= 26 * u; y -= 14 * math.sin(math.pi * u)
    return (x, y)


def distracted(t):
    base = sit(t)
    p = dict(base, lean=10, head=14)
    look_phone = seg(t, 0.4, 0.8) * (1 - seg(t, 5.2, 5.5))
    p["head"] = lerp(14, 22, look_phone) - 4 * seg(t, 5.3, 5.6) * (1 - seg(t, 6.8, 7.2)) * 8 / 4
    p["lean"] = lerp(10, -2, look_phone) + (3 * math.sin(t * 15) if 3.0 < t < 4.4 else 0)
    if 6.6 < t < 7.6: p["head"] = lerp(p["head"], -10, seg(t, 6.6, 6.9) * (1 - seg(t, 7.2, 7.6)))   # looks at her book
    if t > 8.4: p["lean"] = lerp(p["lean"], 14, seg(t, 8.4, 8.9)); p["head"] = lerp(p["head"], 20, seg(t, 8.4, 8.9))
    return dict(x=D_X, y=G - SEAT, p=p, f=1, reach={"f": d_hand(t), "b": (D_BOOK - 18, TOP - 3)})


def f_hand(t):
    keys = [(-0.4, (F_PHONE - 20, TOP - 4)), (0.35, (F_PHONE + 18, TOP - 4)), (0.7, (272, TOP + 32)), (1.0, (F_BOOK + 6, TOP - 5)),
            (6.35, (F_BOOK + 6, TOP - 5)), (6.5, (F_BOOK - 6, TOP - 40)), (6.6, (F_BOOK - 2, TOP - 12)),
            (6.9, (290, G - 232)), (7.3, (290, G - 232)), (7.6, (196, G - 176)), (8.9, (196, G - 176)),
            (9.4, (F_BOOK + 6, TOP - 5))]
    x, y = path(t, keys)
    if 6.9 < t < 7.4: y -= 10 * abs(math.sin((t - 6.9) * 12))                  # fist pump
    u = flip_u(t)
    if u: x -= 26 * u; y -= 16 * math.sin(math.pi * u)
    return (x, y)


def focused(t):
    base = sit(t)
    p = dict(base, lean=14, head=18)
    if 6.6 < t < 7.6: p = dict(p, lean=lerp(14, -4, seg(t, 6.7, 7.0) * (1 - seg(t, 7.3, 7.6))), head=lerp(18, -14, seg(t, 6.7, 7.0) * (1 - seg(t, 7.3, 7.6))))
    if 7.5 < t < 9.0: p = dict(p, head=lerp(18, 4, seg(t, 7.5, 7.8) * (1 - seg(t, 8.7, 9.0))))
    return dict(x=F_X, y=G - SEAT, p=p, f=-1, reach={"f": f_hand(t), "b": (F_BOOK + 26, TOP - 3)})


# ------------------------------------------------------------------ world
def phone(c, x, y, glow=1.0, buzz=0.0, upright=False):
    if buzz: x += 3 * math.sin(NOW_T * 90) * buzz
    r = skia.Rect.MakeXYWH(x - 7, y - 32, 15, 34) if upright else skia.Rect.MakeXYWH(x - 17, y - 7, 34, 7)
    c.drawRRect(skia.RRect.MakeRectXY(r, 3, 3), P((30, 30, 40)))
    if glow > 0:
        col = (120, 190, 255) if not (LAPSE0 < NOW_T < LAPSE1) else [(120, 190, 255), (255, 140, 200), (140, 255, 190)][int(NOW_T * 8) % 3]
        if upright: c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 5, y - 29, 11, 28), 2, 2), P(col, glow))
        c.drawCircle(x, y - (18 if upright else 6), 60, P(col, 0.28 * glow, blur=24))


def drawer(c, x0, x1, out):
    r = skia.Rect.MakeLTRB(x0 + out, TOP + 18, x1 + out, TOP + 54)
    c.drawRect(r, P((128, 88, 60))); c.drawRect(r, P(INK, stroke=3))
    c.drawLine((x0 + x1) / 2 + out - 14, TOP + 36, (x0 + x1) / 2 + out + 14, TOP + 36, P(INK, stroke=4))


def book(c, x, flip=0.0, closed=0.0, cover=(170, 60, 50), web=0.0):
    y = TOP
    if closed > 0.5:
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 44, y - 20, 88, 20), 4, 4)
        c.drawRRect(r, P(cover)); c.drawRRect(r, P(INK, stroke=3)); return
    cv = [(x - 52, y + 2), (x, y - 3), (x + 52, y + 2), (x + 50, y - 6), (x - 50, y - 6)]
    c.drawPath(poly(cv), P(cover)); c.drawPath(poly(cv), P(INK, stroke=2))
    pts = [(x - 48, y), (x, y - 5), (x + 48, y), (x + 45, y - 15), (x, y - 20), (x - 45, y - 15)]
    c.drawPath(poly(pts), P((246, 240, 226))); c.drawPath(poly(pts), P(INK, stroke=3))
    for k in range(3): c.drawLine(x - 38 + k * 4, y - 12 + k * 2, x - 8, y - 13 + k * 2, P(INK, 0.35, stroke=1.5))
    if flip:
        a = math.pi * flip; px = x + 45 * math.cos(a); py = y - 18 - 30 * math.sin(a)
        q = poly([(x, y - 20), (px, py), (px, py + 8), (x, y - 6)])
        c.drawPath(q, P((255, 250, 236))); c.drawPath(q, P(INK, stroke=2))
    if web > 0:                                                            # cobweb on his untouched book
        cx, cy = x + 40, y - 18
        for k in range(6):
            ang = math.radians(150 + k * 20)
            c.drawLine(cx, cy, cx + 46 * web * math.cos(ang), cy - 46 * web * math.sin(ang) * -1, P((235, 235, 245), 0.7 * web, stroke=1.5))
        for rr in (14, 26, 38):
            if rr < 46 * web: c.drawArc(skia.Rect.MakeXYWH(cx - rr, cy - rr, 2 * rr, 2 * rr), 150, 100, False, P((235, 235, 245), 0.6 * web, stroke=1.5))


NOW_T = 0.0


def world(c, t):
    lapse = seg(t, LAPSE0, LAPSE0 + 0.3) * (1 - seg(t, LAPSE1 - 0.3, LAPSE1))
    sh = skia.GradientShader.MakeLinear([(0, G - 700), (0, G)], [C((44, 40, 58)), C((92, 70, 72))])
    c.drawRect(skia.Rect.MakeLTRB(-400, G - 900, W, G), skia.Paint(Shader=sh))
    rng = np.random.default_rng(9)
    for sx in (-150, 330):                                                # bookshelves behind them
        c.drawRect(skia.Rect.MakeLTRB(sx, G - 720, sx + 220, G), P((90, 62, 46)))
        for sy in range(G - 700, G - 60, 120):
            c.drawRect(skia.Rect.MakeLTRB(sx + 8, sy + 102, sx + 212, sy + 112), P((60, 40, 30)))
            bx = sx + 12
            while bx < sx + 204:
                bw = int(rng.integers(12, 22)); bh = int(rng.integers(64, 98))
                col = [(150, 70, 60), (70, 100, 130), (170, 140, 80), (90, 120, 80), (120, 90, 130)][int(rng.integers(0, 5))]
                c.drawRect(skia.Rect.MakeLTRB(bx, sy + 102 - bh, bx + bw, sy + 102), P(col, 0.85)); bx += bw + 2
    # window with the moon moving through the night
    c.drawRect(skia.Rect.MakeLTRB(90, G - 640, 250, G - 420), P((30, 34, 70)))
    m = clock_h(t) / 2.7
    moon(c, 220 - 110 * m, G - 600 + 60 * m, 0.9)
    c.drawRect(skia.Rect.MakeLTRB(90, G - 640, 250, G - 420), P((80, 56, 46), stroke=10))
    c.drawLine(170, G - 640, 170, G - 420, P((80, 56, 46), stroke=6))
    # floor
    c.drawRect(skia.Rect.MakeLTRB(-400, G, W, G + 500), P((70, 48, 40)))
    for k in range(-400, 700, 70): c.drawLine(k, G, k - 50, G + 400, P((52, 36, 30), 0.6, stroke=3))
    # pendant lamp: brighter when she finishes
    on = 0.7 + 0.5 * seg(t, TURN, TURN + 0.3) * (1 - 0.4 * seg(t, 9.6, 10.4))
    c.drawLine(165, G - 900, 165, G - 395, P((40, 40, 48), stroke=3))
    c.drawPath(poly([(140, G - 392), (190, G - 392), (205, G - 370), (125, G - 370)]), P((40, 80, 70)))
    c.drawCircle(165, G - 300, 260, P((255, 214, 140), 0.10 * on, blur=60))


def table(c, t):
    c.drawRect(skia.Rect.MakeLTRB(48, TOP, 282, TOP + 18), P((140, 96, 64))); c.drawRect(skia.Rect.MakeLTRB(48, TOP, 282, TOP + 18), P(INK, stroke=4))
    for lx in (62, 268): c.drawLine(lx, TOP + 18, lx, G, P(INK, stroke=8))
    drawer(c, 68, 128, -30 * (seg(t, 7.6, 8.0) * (1 - seg(t, 8.4, 8.7))))
    drawer(c, 204, 262, 30 * (seg(t, 0.2, 0.45) * (1 - seg(t, 0.75, 1.0))))
    if t > 11.9:                                                           # his phone buzzes in the drawer (→ loop)
        a = seg(t, 11.9, 12.1)
        c.drawCircle(98 + 2 * math.sin(t * 90), TOP + 36, 40, P((120, 190, 255), 0.35 * a, blur=18))


def chair(c, x, f):
    c.drawRect(skia.Rect.MakeLTRB(x - 36, G - SEAT, x + 36, G - SEAT + 12), P((110, 76, 54)))
    c.drawRect(skia.Rect.MakeLTRB(x - 36, G - SEAT, x + 36, G - SEAT + 12), P(INK, stroke=3))
    c.drawLine(x - 34 * f, G - SEAT, x - 40 * f, G - SEAT - 110, P((110, 76, 54), stroke=10))
    for lx in (x - 30, x + 30): c.drawLine(lx, G - SEAT + 12, lx, G, P(INK, stroke=6))


def to_screen(p): return (470 + (p[0] - 165) * K, 1180 + (p[1] - (G - 120)) * K)


def frame(c, t):
    global NOW_T
    NOW_T = t
    c.save(); c.translate(470, 1180); c.scale(K, K); c.translate(-165, -(G - 120))
    world(c, t)
    chair(c, D_X, 1); chair(c, F_X, -1)
    table(c, t)
    book(c, D_BOOK, flip=d_flip(t), web=seg(t, LAPSE0 + 0.3, LAPSE1) * (1 - seg(t, 8.6, 8.85)))
    closed = seg(t, 6.45, 6.6) * (1 - seg(t, 10.0, 10.05))
    book(c, F_BOOK, flip=flip_u(t), closed=closed, cover=(170, 60, 50) if t < 10.0 else (60, 110, 160))   # 10 s: book 2
    if t < 0.75:                                                           # her phone slides into the drawer
        px = lerp(F_PHONE - 20, F_PHONE + 18, seg(t, -0.4, 0.35)); py = lerp(TOP, TOP + 36, seg(t, 0.35, 0.7))
        if t < 0.35: px = f_hand(t)[0]
        else: px, py = f_hand(t)
        phone(c, px, py + 2, glow=1 - seg(t, 0.3, 0.6), buzz=1 - seg(t, 0.0, 0.3))
    lo = (1, -0.6)
    d = distracted(t)
    jd = figure(c, d["x"], d["y"], d["p"], s=S, facing=d["f"], body=D_BODY, rim=((210, 220, 255), 0.5), light=lo, mode="hip", reach=d["reach"])
    hx, hy = d["reach"]["f"]
    if t < 0.35: phone(c, D_PHONE, TOP, glow=1, buzz=1 - seg(t, 0.2, 0.35))
    elif t < 8.4: phone(c, hx + 4, hy + 6, glow=1 - seg(t, 7.9, 8.2), upright=True)
    fo = focused(t)
    jf = figure(c, fo["x"], fo["y"], fo["p"], s=S, facing=fo["f"], body=F_BODY, rim=((255, 220, 170), 0.6), light=lo, mode="hip", reach=fo["reach"])
    c.restore()
    heads = {"d": to_screen(jd["head"]), "f": to_screen(jf["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 230, 860, "DISTRACTED", GREY, size=28, a=na)
        chip(c, 720, 860, "FOCUSED", AMBER, size=28, a=na)
    vignette(c, 0.3)
    # counters
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    hrs = 10 + clock_h(t); hh = int(hrs) % 12 or 12; mm = int((hrs % 1) * 60) // 10 * 10
    ampm = "PM" if hrs < 12 else "AM"
    chip(c, 470, 580, f"{hh}:{mm:02d} {ampm}" + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=40 + 22 * lapse,
         pop=1 + 0.08 * lapse * abs(math.sin(t * 2 * math.pi / 0.27)))
    dp = d_pages(t)
    chip(c, 250, 765, f"PAGE {dp}", GREY, size=36, pop=1 + 0.15 * (1 - seg(t, 9.0 + 0.6 * (dp - 2), 9.2 + 0.6 * (dp - 2))) * (dp > 1))
    if TURN <= t < 9.9:
        k = seg(t, TURN, TURN + 0.25)
        chip(c, 690, 765, "DONE ✓", AMBER, size=36 + 14 * k, pop=1 + 0.3 * (1 - k))
    else:
        chip(c, 690, 765, f"PAGE {f_pages(t)}", AMBER, size=36)
        if 10.0 < t < 11.2: plate_label(c, "BOOK 2", 690, 712, AMBER, seg(t, 10.0, 10.2) * (1 - seg(t, 10.9, 11.2)))
    for ts, who, txt in TALK:
        if ts < t < ts + 1.35:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.15, ts + 1.35))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 200, 300, 560) if who == "d" else clamp(hx_ - 200, 400, 600)
            bubble(c, bx_, hy_ - 170, txt, a, "speech", tail=(hx_ + (40 if who == 'd' else -40), hy_ - 60), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", 0.0, "tone-ding-high", -9], ["slide", 0.3], ["sfx", LAPSE0, "time-clock-fast", -8], ["sfx", LAPSE0, "riser-2s-soft", -12]]
    ev += [["sfx", LAPSE0 + 0.25 * i, "data-tick", -16] for i in range(int((LAPSE1 - LAPSE0) / 0.25))]
    ev += [["jump", 5.75], ["thud", TURN], ["summit", TURN + 0.3], ["sfx", TURN, "cinematic-slam-big", -10],
           ["slide", 8.0], ["thud", 8.5], ["text", END_T0], ["sfx", 11.95, "tone-ding-high", -12]]
    ev += [["jump", 9.0 + 0.6 * i] for i in range(5)]
    return ev


if __name__ == "__main__":
    main("Folge23_Focused_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep23_v2",
         [0.0, 0.4, 1.2, 3.0, 5.4, 6.7, 7.8, 8.6, 9.8, 11.0, 11.7, 12.45])
