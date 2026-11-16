"""Episode 10: GRUDGE vs. LETTING GO – stormy lake → clear golden dusk.
Both wade in carrying a heavy stone labelled PAST. Letting Go drops it and swims to the island with the lit cabin.
Grudge clings to his stone, stuck in the water – his own little rain cloud keeps raining on him."""
import sys, math
import numpy as np
from lib import *

T_END = 17.2
G = 1240                 # shore level
WL = G - 8               # water surface
SC = 1.3                 # scene zoom
S = 1.0
TURN = 11.6
DROP = 4.6               # Letting Go drops the stone
GRUDGE_TALK = [(3.0, "They hurt me."), (6.3, "I'll never forget."), (8.9, "It's MY stone.")]


SHORE = 330


def bed(x):
    """lake bed under the water (feet height)"""
    if x < SHORE: return G
    if x < 520: return G + 100 * ease((x - SHORE) / 190)
    if x < 690: return G + 100
    if x < 760: return G + 100 - 140 * ease((x - 690) / 70)
    return G - 40          # island


def clear(t): return seg(t, 8.6, TURN + 0.6)   # 0 storm … 1 clear dusk


def carry(): return dict(lean=4, head=6, arm_f=70, elb_f=-75, arm_b=60, elb_b=-70, leg_f=3, leg_b=-3)


def letgo(t):
    if t < DROP:
        x = lerp(430, 540, seg(t, 0.0, 3.6))
        p = dict(carry(), **{k: v for k, v in walk(t * 7, lean=8).items() if k.startswith(("leg", "knee"))})
        if t > 3.6: p = dict(carry(), head=25)  # looks at the stone
        return dict(x=x, y=bed(x), p=p, stone=True)
    if t < DROP + 0.6:
        return dict(x=540, y=bed(540), p=mix(dict(carry(), head=25), dict(stand(), arm_f=20, arm_b=-20, head=10), seg(t, DROP, DROP + 0.3)))
    if t < 10.3:  # swims to the island
        k = seg(t, DROP + 0.6, 10.3)
        x = lerp(560, 770, k)
        ph = t * 7
        p = dict(lean=0, head=-70, arm_f=100 + 80 * math.sin(ph), elb_f=10, arm_b=100 + 80 * math.sin(ph + math.pi), elb_b=10,
                 leg_f=6 * math.sin(ph * 2), leg_b=-6 * math.sin(ph * 2))
        return dict(x=x, y=WL + 12, p=p, rot=-82, swim=True)
    if t < 10.9:
        k = seg(t, 10.3, 10.9)
        return dict(x=lerp(770, 820, k), y=G - 40, p=crouch() if k < 0.5 else stand())
    if t < TURN: return dict(x=820, y=G - 40, p=stand())
    return dict(x=820, y=G - 40, p=cheer(t))


def grudge(t):
    x = lerp(250, 385, seg(t, 0.2, 3.0))
    if t < 3.0:
        p = dict(carry(), **{k: v for k, v in walk(t * 7, lean=8).items() if k.startswith(("leg", "knee"))})
    else:
        sway = math.sin(t * 2.2) * 4
        p = dict(carry(), lean=10 + sway, head=12, arm_f=55, elb_f=-95, arm_b=50, elb_b=-90)
    return dict(x=x, y=bed(x), p=p)


# ------------------------------------------------------------------ world
def cloud(c, x, y, sc, col, a=1.0):
    for dx, dy, r in ((-60, 10, 46), (-10, -14, 58), (50, 6, 44), (10, 22, 40)):
        c.drawCircle(x + dx * sc, y + dy * sc, (r + 4) * sc, P(INK, a))
    for dx, dy, r in ((-60, 10, 46), (-10, -14, 58), (50, 6, 44), (10, 22, 40)):
        c.drawCircle(x + dx * sc, y + dy * sc, r * sc, P(col, a))


def rain(c, t, x0, x1, y0, y1, a, n=120, seed=2):
    if a <= 0: return
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(x0, x1); sp = rng.uniform(900, 1300); off = rng.uniform(0, 2000)
        y = y0 + (off + t * sp) % (y1 - y0)
        c.drawLine(x, y, x - 8, y + 30, P((200, 215, 235), 0.55 * a, stroke=2.5))


def island(c, u):
    c.drawOval(skia.Rect.MakeXYWH(730, G - 70, 420, 120), P(INK))
    c.drawOval(skia.Rect.MakeXYWH(734, G - 66, 412, 112), P(lerpc((60, 70, 60), (110, 150, 80), u)))
    # cabin
    hx, hy = 950, G - 40
    c.drawRect(skia.Rect.MakeXYWH(hx - 70, hy - 110, 140, 110), P(lerpc((80, 70, 70), (160, 110, 80), u)))
    c.drawRect(skia.Rect.MakeXYWH(hx - 70, hy - 110, 140, 110), P(INK, stroke=6))
    roof = poly([(hx - 90, hy - 105), (hx, hy - 180), (hx + 90, hy - 105)])
    c.drawPath(roof, P(lerpc((60, 50, 60), (150, 70, 60), u))); c.drawPath(roof, P(INK, stroke=6))
    glow = 0.6 + 0.4 * u
    c.drawCircle(hx - 20, hy - 60, 160, P((255, 190, 100), 0.25 * glow, blur=50))
    c.drawRect(skia.Rect.MakeXYWH(hx - 42, hy - 82, 40, 36), P((255, 210, 130), glow))
    c.drawRect(skia.Rect.MakeXYWH(hx - 42, hy - 82, 40, 36), P(INK, stroke=5))



def world(c, t):
    u = clear(t)
    sky(c, t, lerpc((50, 56, 70), (70, 60, 130), u), lerpc((90, 96, 110), (250, 140, 110), u), lerpc((120, 126, 136), (255, 200, 130), u), G)
    sun(c, 560, lerp(1300, 1040, u), clamp(u * 1.4), r=80)
    # storm clouds move away
    for i in range(5):
        cloud(c, 120 + i * 260 - u * 1000, 730 + (i % 2) * 60, 1.5, (90, 96, 110), 1 - u)
    hills(c, G, lerpc((60, 66, 76), (90, 70, 110), u), amp=26, off=1.2, a=0.95, height=110)
    haze(c, G, lerpc((120, 126, 136), (255, 190, 140), u), 0.45, 200)
    # shore (left)
    shore = poly([(-300, G), (SHORE, G), (SHORE + 190, G + 100), (SHORE + 190, H + 300), (-300, H + 300)])
    c.drawPath(shore, P(lerpc((80, 74, 66), (150, 120, 80), u)))
    c.drawPath(poly([(-300, G), (SHORE, G), (SHORE + 190, G + 100)], close=False), P(INK, stroke=5))
    c.drawRect(skia.Rect.MakeLTRB(SHORE + 190, G + 100, W + 400, H + 300), P(lerpc((60, 56, 50), (100, 80, 60), u)))
    island(c, u)
    return u


def water(c, t, u):
    """semi-transparent lake over everything below the surface"""
    path = skia.Path(); path.moveTo(SHORE - 10, WL)
    for x in range(SHORE - 10, W + 420, 30):
        path.lineTo(x, WL + 5 * math.sin(x * 0.03 + t * 3))
    path.lineTo(W + 400, H + 300); path.lineTo(SHORE - 10, H + 300); path.close()
    sh = skia.GradientShader.MakeLinear([(0, WL), (0, WL + 500)], [C(lerpc((70, 90, 110), (90, 110, 170), u), 0.62), C(lerpc((20, 30, 46), (30, 30, 70), u), 0.95)])
    c.drawPath(path, skia.Paint(AntiAlias=True, Shader=sh))
    c.drawPath(path, P(lerpc((150, 170, 190), (255, 210, 160), u), 0.7, stroke=3))
    # sun reflection after the storm
    if u > 0:
        for k in range(6):
            c.drawLine(560 - k * 8, WL + 20 + k * 26, 680 + k * 8, WL + 20 + k * 26, P((255, 210, 150), 0.35 * u, stroke=6))


def stone(c, x, y, a=1.0):
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 52, y - 34, 104, 68), 30, 30)
    c.drawRRect(r, P((120, 124, 132), a)); c.drawRRect(r, P(INK, a, stroke=6))
    text(c, "PAST", x, y + 9, F_SANS, 26, (40, 42, 52), a, spacing=3)


def frame(c, t):
    c.save(); c.translate(540, G); c.scale(SC, SC); c.translate(-600, -G)
    u = world(c, t)
    body = lerpc((215, 220, 232), (252, 246, 236), u)
    # Grudge
    g = smooth(grudge, t)
    jg = figure(c, g["x"], g["y"], g["p"], s=S, facing=1, body=body, rim=((170, 200, 255), 0.45))
    sx, sy = (jg["hand_f"][0] + jg["hand_b"][0]) / 2, (jg["hand_f"][1] + jg["hand_b"][1]) / 2
    stone(c, sx + 14, sy - 8)
    # Letting Go
    l = smooth(letgo, t)
    rim_l = (lerpc((170, 200, 255), (255, 200, 130), u), 0.55)
    if not l.get("swim"):
        jl = figure(c, l["x"], l["y"], l["p"], s=S, facing=1, body=body, rim=rim_l)
    if l.get("stone"):
        lx, ly = (jl["hand_f"][0] + jl["hand_b"][0]) / 2, (jl["hand_f"][1] + jl["hand_b"][1]) / 2
        stone(c, lx + 14, ly - 8)
    elif t < DROP + 2.0:  # the dropped stone sinks
        k = seg(t, DROP, DROP + 1.4)
        stone(c, 560, lerp(G - 120, bed(560) - 20, k), 1.0)
    water(c, t, u)
    if l.get("swim"):  # swimmer on the surface: only the part above the water line
        c.save(); c.clipRect(skia.Rect.MakeLTRB(-400, -800, W + 400, WL + 14))
        jl = figure(c, l["x"], WL + 6, l["p"], s=S, facing=1, rot=l["rot"], body=body, mode="hip", rim=rim_l)
        c.restore()
        for k in range(3):  # wake
            c.drawLine(l["x"] - 60 - k * 40, WL + 4, l["x"] - 30 - k * 40, WL + 4, P((240, 245, 250), 0.6 - 0.15 * k, stroke=4))
    if DROP < t < DROP + 1.2:  # splash rings
        k = (t - DROP) / 1.2
        for r in (1, 0.6):
            c.drawOval(skia.Rect.MakeXYWH(560 - 120 * k * r, WL - 10 * k * r, 240 * k * r, 20 * k * r), P((230, 240, 250), 0.8 * (1 - k), stroke=4))
    if l["y"] >= G - 40 and not l.get("swim") and t > 10.3:
        shadow(c, l["x"], G - 40, S)
    # labels after the water so they stay readable
    if l.get("swim"): plate_label(c, "LETTING GO", jl["head"][0] + 110, WL - 120, AMBER, 0.95)
    else: plate_label(c, "LETTING GO", jl["head"][0], jl["head"][1] - 52, AMBER, 0.95)
    plate_label(c, "GRUDGE", jg["head"][0], jg["head"][1] - 52, GREY, 0.9)
    # Grudge's own little storm keeps raining on him
    gc = jg["head"][1] - 230
    cloud(c, jg["head"][0], gc, 0.9, (80, 86, 100), clamp(0.3 + u))
    rain(c, t, -300, W + 300, -400, WL, 1 - u, n=160, seed=3)
    rain(c, t, jg["head"][0] - 70, jg["head"][0] + 70, gc + 20, WL, clamp(0.4 + u), n=26, seed=5)
    if 3.5 < t < 4.6:
        a = seg(t, 3.5, 3.65) * (1 - seg(t, 4.4, 4.6))
        bubble(c, jl["head"][0] + 110, jl["head"][1] - 190, "Why carry this?", a, "think", tail=(jl["head"][0] + 50, jl["head"][1] - 95), size=32)
    for ts, txt in GRUDGE_TALK:
        if ts < t < ts + 1.9:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.6, ts + 1.9))
            bubble(c, max(jg["head"][0] + 30, 300), gc - 110, txt, a, "speech", tail=(jg["head"][0] + 20, gc - 60), size=32,
                   pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    if t < 1.2:  # lightning flash
        c.drawRect(skia.Rect.MakeWH(W, H), P((255, 255, 255), 0.35 * (1 - seg(t, 0.75, 1.2)) * (t > 0.7)))
    vignette(c, 0.45)
    grain(c, t, 0.035)
    end_text(c, t, 14.4, "Holding on", "only hurts you.", "Let it go. Swim.", y=1430)


def events():
    ev = [["rain", 0.0, 11.0], ["thunder", 0.75], ["thunder", 6.0], ["splash", DROP + 0.1], ["pop", 3.5]]
    for ts, _ in GRUDGE_TALK: ev.append(["pop", ts])
    for k in range(int((10.3 - DROP - 0.6) * 2)): ev.append(["splash", DROP + 0.8 + k * 0.5])
    for k in range(7): ev.append(["step", 0.3 + k * 0.45, True])
    ev += [["land", 10.6], ["sunrise", TURN - 1.8], ["summit", TURN], ["text", 14.4], ["text2", 15.2]]
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still":
        stills(frame, [0.8, 3.8, 5.3, 8.0, 12.2, 15.8], "check/ep10")
    else:
        finish_v2("Folge10_LettingGo", frame, T_END, events(), TURN, 10, "What are you still holding onto?", 0.3, 16.0)
