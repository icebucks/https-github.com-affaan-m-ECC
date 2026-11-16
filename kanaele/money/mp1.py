"""Money Psychology #1: THE $5 COFFEE – SPENDER vs INVESTOR, city street, morning -> golden evening.
Every day both drink coffee. Spender buys a $5 cup at the kiosk, Investor brews at home and drops the $5 into a jar.
Numbers: $5 x 365 = $1,825 a year. Invested yearly at 8 % (future value of an annuity):
year 1 $1,825 · year 3 $5,925 · year 5 $10,707 · year 10 $26,438. Spent after 10 years: $18,250."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "beyondexcuses"))
os.environ.setdefault("OUT_DIR", HERE)
from lib import *

T_END = 17.4
G = 1240
SC = 1.35
S = 1.0
KX = 300            # kiosk counter (right edge)
XS = 480            # spender home spot
XI = 705            # investor
JX = 800            # jar on the table
PH = 2.2            # length of one time phase
PHASES = [("DAY 1", 5, 5), ("MONTH 1", 150, 150), ("YEAR 1", 1825, 1825), ("YEAR 3", 5475, 5925),
          ("YEAR 5", 9125, 10707), ("YEAR 10", 18250, 26438)]
T0 = 0.4
TURN = T0 + 5 * PH + 0.4      # year 10 reveal ≈ 11.8
SPEND_TALK = [(T0 + 1.3, "I deserve this."), (T0 + PH + 1.3, "It's only $5."), (T0 + 3 * PH + 1.3, "Still only $5!")]


def phase(t):
    k = int(clamp((t - T0) / PH, 0, 5.999)); return k, (t - T0) - k * PH


def money(t, which):
    """animated counter value (1 = spent, 2 = invested)"""
    if t < T0 + 0.9: return 0 if t < T0 + 0.6 else PHASES[0][which]
    k, u = phase(t)
    prev = PHASES[k - 1][which] if k > 0 else 0
    return lerp(prev, PHASES[k][which], seg(u, 0.2, 1.4))


# ------------------------------------------------------------------ characters
def hold(): return dict(stand(), arm_f=40, elb_f=-75)
def drink(): return dict(stand(), arm_f=22, elb_f=148, head=-14)
def reach(): return dict(stand(), lean=8, arm_f=82, elb_f=-8)


def spender(t):
    if t < T0: return dict(x=XS, p=stand(), f=-1)
    k, u = phase(t)
    if t >= TURN - 0.3:   # year 10: checks the empty wallet
        kk = seg(t, TURN, TURN + 0.6)
        return dict(x=XS, p=mix(stand(), dict(slump(), arm_f=55, elb_f=-60, head=30), kk), f=1, wallet=kk > 0.3)
    if u < 0.75: return dict(x=lerp(XS, KX + 70, ease(u / 0.75)), p=walk(t * 10), f=-1, walk=True)
    if u < 1.05: return dict(x=KX + 70, p=reach(), f=-1)
    if u < 1.75: return dict(x=lerp(KX + 70, XS, ease((u - 1.05) / 0.7)), p=dict(walk(t * 10), arm_f=40, elb_f=-75), f=1, cup=True, walk=True)
    return dict(x=XS, p=drink() if u < 2.05 else hold(), f=1, cup=True)


def investor(t):
    if t >= TURN:
        return dict(x=XI, p=cheer(t), f=1)
    if t < T0: return dict(x=XI, p=stand(), f=1)
    k, u = phase(t)
    if u < 0.5: return dict(x=XI, p=hold(), f=1, mug=True)
    if u < 0.9: return dict(x=XI, p=drink(), f=1, mug=True)
    if u < 1.4: return dict(x=XI, p=reach(), f=1, coin=seg(u, 1.0, 1.35))
    return dict(x=XI, p=stand(), f=1)


# ------------------------------------------------------------------ props
def cup(c, x, y, a=1.0, s=1.0):
    r = skia.Path(); r.moveTo(x - 11 * s, y - 26 * s); r.lineTo(x + 11 * s, y - 26 * s); r.lineTo(x + 8 * s, y); r.lineTo(x - 8 * s, y); r.close()
    c.drawPath(r, P((250, 246, 238), a)); c.drawPath(r, P(INK, a, stroke=4))
    c.drawRect(skia.Rect.MakeXYWH(x - 10 * s, y - 18 * s, 20 * s, 8 * s), P((150, 100, 60), a))
    c.drawRect(skia.Rect.MakeXYWH(x - 13 * s, y - 31 * s, 26 * s, 6 * s), P((60, 50, 46), a))


def mug(c, x, y):
    c.drawRect(skia.Rect.MakeXYWH(x - 11, y - 22, 22, 22), P((110, 170, 210))); c.drawRect(skia.Rect.MakeXYWH(x - 11, y - 22, 22, 22), P(INK, stroke=4))
    c.drawCircle(x + 14, y - 11, 6, P(INK, stroke=4))


def coin(c, x, y, r=11, a=1.0):
    c.drawCircle(x, y, r + 2, P(INK, a)); c.drawCircle(x, y, r, P((250, 200, 70), a))
    c.drawCircle(x, y, r * 0.55, P((255, 230, 140), a * 0.8, stroke=2))


def kiosk(c, u):
    c.drawRect(skia.Rect.MakeLTRB(-200, G - 300, KX - 10, G), P(lerpc((150, 100, 80), (175, 115, 80), u)))
    c.drawRect(skia.Rect.MakeLTRB(-200, G - 300, KX - 10, G), P(INK, stroke=6))
    for i in range(6):   # striped awning
        x0 = -200 + i * 70
        c.drawPath(poly([(x0, G - 330), (x0 + 70, G - 330), (x0 + 70, G - 290), (x0, G - 290)]), P((230, 90, 80) if i % 2 else (250, 240, 230)))
    c.drawPath(poly([(-200, G - 330), (KX + 40, G - 330), (KX + 40, G - 290), (-200, G - 290)]), P(INK, stroke=6))
    c.drawRect(skia.Rect.MakeLTRB(-200, G - 160, KX + 10, G - 130), P((110, 70, 50))); c.drawRect(skia.Rect.MakeLTRB(-200, G - 160, KX + 10, G - 130), P(INK, stroke=5))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(150, G - 272, KX - 20, G - 200), 10, 10), P(INK))
    text(c, "COFFEE", (150 + KX - 20) / 2, G - 242, F_CAP, 26, (255, 220, 120), 1.0)
    text(c, "$5", (150 + KX - 20) / 2, G - 210, F_CAP, 30, (255, 220, 120), 1.0)


def trash(c, n):
    bx = XS + 100
    for i in range(n):   # pile of empty cups on top of the bin
        ang = (i * 37 % 60) - 30
        c.save(); c.translate(bx - 30 + (i * 23) % 60, G - 92 - (i // 3) * 20); c.rotate(ang); cup(c, 0, 0, 1.0, 0.9); c.restore()
    r = skia.Path(); r.moveTo(bx - 40, G - 95); r.lineTo(bx + 40, G - 95); r.lineTo(bx + 32, G); r.lineTo(bx - 32, G); r.close()
    c.drawPath(r, P((90, 100, 110))); c.drawPath(r, P(INK, stroke=6))
    for dx in (-15, 0, 15): c.drawLine(bx + dx, G - 80, bx + dx * 0.8, G - 12, P(INK, 0.5, stroke=3))


def jar(c, t):
    """glass jar on a small table, coins rise with the invested value; becomes a money tree at the turn"""
    c.drawRect(skia.Rect.MakeXYWH(JX - 55, G - 90, 110, 14), P((140, 95, 60))); c.drawRect(skia.Rect.MakeXYWH(JX - 55, G - 90, 110, 14), P(INK, stroke=5))
    for dx in (-42, 42): c.drawLine(JX + dx, G - 76, JX + dx, G, P(INK, stroke=8))
    fill = clamp(money(t, 2) / 10707) * 0.92
    jt, jb = G - 200, G - 92
    c.drawRect(skia.Rect.MakeLTRB(JX - 34, jb - (jb - jt) * fill, JX + 34, jb), P((250, 200, 70)))
    for i in range(int(fill * 9)):
        c.drawLine(JX - 30, jb - 12 - i * 11, JX + 30, jb - 12 - i * 11, P((200, 150, 40), stroke=3))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(JX - 38, jt, JX + 38, jb), 12, 12), P((220, 240, 255), 0.25))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(JX - 38, jt, JX + 38, jb), 12, 12), P(INK, stroke=5))
    c.drawRect(skia.Rect.MakeLTRB(JX - 30, jt - 14, JX + 30, jt), P((120, 120, 130))); c.drawRect(skia.Rect.MakeLTRB(JX - 30, jt - 14, JX + 30, jt), P(INK, stroke=4))
    # money tree grows out of the jar at year 10
    g = seg(t, TURN - 0.4, TURN + 1.0)
    if g > 0:
        top = jt - 14 - 230 * g
        c.drawLine(JX, jt - 10, JX, top + 40, P(INK, stroke=16)); c.drawLine(JX, jt - 10, JX, top + 40, P((120, 90, 60), stroke=9))
        for dx, dy, r in ((-60, 40, 52), (55, 30, 56), (0, 0, 62), (-30, -40, 46), (40, -35, 44)):
            rr = r * g
            c.drawCircle(JX + dx * g, top + dy * g + 40, rr + 4, P(INK)); c.drawCircle(JX + dx * g, top + dy * g + 40, rr, P((90, 170, 90)))
        for i in range(14):   # coins as fruit
            a = i * 2.4
            coin(c, JX + math.cos(a) * 70 * g * (0.4 + (i % 3) * 0.25), top + 40 + math.sin(a) * 55 * g * (0.4 + (i % 3) * 0.25), 9 * g, g)


def counter(c, x, y, title, val, col, a=1.0):
    text(c, title, x, y, F_SANS, 30, col, a, spacing=3, stroke=6)
    text(c, f"${int(round(val)):,}", x, y + 78, F_CAP, 72, col, a, stroke=14)


# ------------------------------------------------------------------ world
def world(c, t):
    u = seg(t, TURN - 1.6, TURN + 1.0)         # morning -> golden evening at the reveal
    sky(c, t, lerpc((120, 170, 230), (70, 60, 120), u), lerpc((190, 215, 240), (230, 130, 110), u), lerpc((250, 235, 210), (255, 200, 130), u), G)
    sun(c, 700, lerp(760, 980, u), 0.9, r=70)
    rng = np.random.default_rng(5)
    x = -300
    while x < W + 300:   # city skyline
        w = rng.uniform(80, 160); h = rng.uniform(180, 420)
        col = lerpc((150, 165, 190), (120, 90, 120), u)
        c.drawRect(skia.Rect.MakeXYWH(x, G - 40 - h, w, h + 40), P(col)); c.drawRect(skia.Rect.MakeXYWH(x, G - 40 - h, w, h + 40), P(INK, 0.35, stroke=3))
        for wy in range(int(G - h - 20), int(G - 60), 34):
            for wx in range(int(x + 14), int(x + w - 14), 26):
                if rng.random() < 0.4: c.drawRect(skia.Rect.MakeXYWH(wx, wy, 11, 15), P((255, 230, 160), 0.2 + 0.5 * u))
        x += w + rng.uniform(6, 22)
    haze(c, G - 40, lerpc((250, 235, 220), (255, 190, 140), u), 0.45, 240)
    c.drawRect(skia.Rect.MakeLTRB(-300, G, W + 300, H + 300), P(lerpc((170, 165, 160), (150, 120, 110), u)))
    c.drawRect(skia.Rect.MakeLTRB(-300, G, W + 300, G + 22), P(lerpc((200, 195, 190), (190, 160, 140), u)))
    c.drawLine(-300, G, W + 300, G, P(INK, stroke=5))
    return u


def frame(c, t):
    c.save(); c.translate(540, G); c.scale(SC, SC); c.translate(-540, -G)
    u = world(c, t)
    body = (246, 246, 242)
    kiosk(c, u)
    k, uu = phase(t)
    trash(c, 0 if t < T0 + 2.0 else min(15, int(2 + (t - T0) / PH * 2.6)))
    jar(c, t)
    # spender
    s = smooth(spender, t)
    shadow(c, s["x"], G, S)
    js = figure(c, s["x"], G, s["p"], s=S, facing=s["f"], body=body, rim=(lerpc((255, 245, 230), (255, 190, 130), u), 0.4))
    if s.get("cup"): cup(c, js["hand_f"][0] + 4 * s["f"], js["hand_f"][1] + 14)
    if s.get("wallet"):
        hx, hy = js["hand_f"]
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(hx - 22, hy - 14, 44, 30), 6, 6), P((120, 80, 50))); c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(hx - 22, hy - 14, 44, 30), 6, 6), P(INK, stroke=4))
        m = seg(t, TURN + 0.4, TURN + 2.4)   # moth flies out
        if 0 < m < 1:
            mx, my = hx + 60 * m + math.sin(t * 9) * 10, hy - 140 * m
            for sgn in (-1, 1): c.drawOval(skia.Rect.MakeXYWH(mx + sgn * 9 - 7, my - 6 + abs(math.sin(t * 20)) * 4, 14, 10), P((200, 190, 170)))
    plate_label(c, "SPENDER", js["head"][0], js["head"][1] - 52, GREY, 0.9)
    # investor
    i = smooth(investor, t)
    shadow(c, i["x"], G, S)
    ji = figure(c, i["x"], G, i["p"], s=S, facing=1, body=body, rim=(lerpc((255, 230, 180), (255, 200, 120), u), 0.55))
    if i.get("mug"): mug(c, ji["hand_f"][0] + 6, ji["hand_f"][1] + 12)
    if i.get("coin") is not None and i.get("coin") > 0:
        q = i["coin"]
        coin(c, lerp(ji["hand_f"][0], JX, q), lerp(ji["hand_f"][1], G - 205, q) - math.sin(q * math.pi) * 40)
    plate_label(c, "INVESTOR", ji["head"][0], ji["head"][1] - 52, AMBER, 0.95)
    # bubbles
    for ts, txt in SPEND_TALK:
        if ts < t < ts + 1.6:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.3, ts + 1.6))
            bubble(c, max(js["head"][0] + 40, 330), js["head"][1] - 150, txt, a, "speech", tail=(js["head"][0] + 10, js["head"][1] - 40), size=30,
                   pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    if TURN + 0.6 < t < TURN + 2.6:
        a = seg(t, TURN + 0.6, TURN + 0.8) * (1 - seg(t, TURN + 2.3, TURN + 2.6))
        bubble(c, js["head"][0] + 30, js["head"][1] - 150, "Where did it go?", a, "think", tail=(js["head"][0], js["head"][1] - 60), size=30)
    c.restore()
    # counters + time label (screen space)
    a = seg(t, T0 + 0.5, T0 + 0.9) * (1 - seg(t, 14.0, 14.4))
    counter(c, 300, 1340, "SPENT", money(t, 1), (235, 120, 110), a)
    counter(c, 780, 1340, "INVESTED @ 8%", money(t, 2), (140, 220, 130), a)
    if t > T0:
        k, uu = phase(t)
        pa = (1 - seg(t, 14.0, 14.4))
        pop = 1 + 0.1 * (1 - seg(uu, 0, 0.2))
        c.save(); c.translate(540, 560); c.scale(pop, pop)
        text(c, PHASES[k][0], 0, 0, F_CAP, 70, (255, 255, 255), pa, stroke=12)
        c.restore()
    vignette(c, 0.4)
    grain(c, t, 0.03)
    end_text(c, t, 14.4, "Same coffee. Same 10 years.", "One spent $18,250.", "One built $26,438.", y=1430)


def events():
    ev = []
    for k in range(6):
        t0 = T0 + k * PH
        if t0 + 0.75 < TURN - 0.3:
            for j in range(3): ev.append(["step", t0 + 0.1 + j * 0.25, False])
            ev.append(["pop", t0 + 1.0])           # buying
            ev.append(["land", t0 + 1.35])         # coin in the jar
    for ts, _ in SPEND_TALK: ev.append(["pop", ts])
    ev += [["sunrise", TURN - 1.4], ["summit", TURN], ["pop", TURN + 0.6], ["text", 14.4], ["text2", 15.2]]
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still":
        stills(lambda c, t: (frame(c, t + 0.3), series_overlay(c, t, 1, "Is your coffee making you poor?", 15.7, series="MONEY PSYCHOLOGY")),
               [0.5, 2.0, 5.2, 9.5, 12.4, 16.2], os.path.join(HERE, "check_mp1"))
    else:
        finish_v2("MP1_Coffee", frame, T_END, events(), TURN, 1, "Is your coffee making you poor?", 0.3, 16.0, series="MONEY PSYCHOLOGY")
