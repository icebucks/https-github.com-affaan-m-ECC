"""Episode 13 (TikTok: Part 10): PERFECTIONIST vs. FINISHER – a woodworking shop, cold blue dawn through a skylight → golden noon.
The perfectionist sands the same chair for weeks ("Not perfect yet…"). Next to him the finisher builds chair after chair –
a little crooked, but done. At noon the sun hits her stack: every chair gets a SOLD tag. He blows off the dust and starts again."""
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 10                     # TikTok part number (internal episode 13)
G = 1240
SC = 1.4
DY = 60
S = 1.0
TURN = 11.2                    # sun through the skylight, SOLD tags
PX, PCHAIR = 290, 335          # perfectionist and his chair
FX, FCHAIR = 575, 650          # finisher and the chair she is building
STACK = 735                    # her finished chairs
CYCLE, BUILD0 = 1.15, 0.5      # one chair per 1.15 s
N_CHAIRS = 9
TALK = [(1.0, "Not perfect yet…"), (4.8, "Almost…"), (8.3, "One more coat."), (TURN + 1.0, "Tomorrow it's perfect.")]
PER_BODY = (196, 202, 216)
FIN_BODY = (255, 226, 178)
HOOK = "3 weeks. 1 chair.\nShe already finished 9."
FOCUS = (230, 1150)            # opening close-up: the perfectionist sanding
CTA = "Part 11 tomorrow:\nthe one who carries everyone's bags"


def light(t): return seg(t, TURN - 0.9, TURN + 0.7)
def chairs_done(t): return int(clamp((t - BUILD0) / CYCLE, 0, N_CHAIRS))
def cycle_u(t): return ((t - BUILD0) / CYCLE) % 1.0 if BUILD0 < t < BUILD0 + N_CHAIRS * CYCLE else 0.0


# ------------------------------------------------------------------ characters
def perfectionist(t):
    base = dict(stand(), lean=40, head=10, leg_f=34, leg_b=10, knee_f=40, knee_b=34)
    stroke = math.sin(t * 9)                                   # sanding back and forth
    p = dict(x=PX, y=G, p=base, f=1, reach={"f": (PCHAIR - 8 + 24 * stroke, G - 76), "b": (PCHAIR - 22, G - 74)})
    for ts, _ in TALK[:3]:                                     # straightens up, squints at it
        if ts < t < ts + 1.4:
            k = seg(t, ts, ts + 0.25) * (1 - seg(t, ts + 1.1, ts + 1.4))
            p["p"] = mix(base, dict(think(t), head=10), k)
            if k > 0.12: p["reach"] = None
    if TURN < t < TURN + 1.0:                                  # looks over at her sold stack
        k = seg(t, TURN, TURN + 0.3) * (1 - seg(t, TURN + 0.7, TURN + 1.0))
        p["p"] = mix(base, dict(stand(), head=-6), k)
        if k > 0.12: p["reach"] = None
    if TURN + 1.0 < t < TURN + 1.6:                            # blows the dust off – and starts again
        p["p"] = dict(base, lean=34, head=24)
    return p


def finisher(t):
    base = dict(stand(), lean=38, head=8, leg_f=32, leg_b=8, knee_f=38, knee_b=32)
    if t < TURN and BUILD0 < t < BUILD0 + N_CHAIRS * CYCLE:
        u = cycle_u(t)
        if u < 0.75:                                           # three hammer hits per chair
            k = (u / 0.25) % 1.0
            s_ = ease(clamp(k / 0.7)) if k < 0.7 else 1 - (k - 0.7) / 0.3
            wind, strike = (FX + 6, G - 170), (FCHAIR - 6, G - 74)
            hand = (lerp(wind[0], strike[0], s_), lerp(wind[1], strike[1], s_))
        else:                                                  # pushes the finished chair to the stack
            hand = (lerp(FCHAIR - 6, FCHAIR - 2, ease((u - 0.75) / 0.25)), G - 78)
        return dict(x=FX, y=G, p=base, f=1, hammer=True, reach={"f": hand, "b": (FCHAIR - 24, G - 72)})
    if t >= TURN:                                              # all sold: cheers
        ph = (t - TURN - 0.3) / 0.62
        hop = max(0.0, math.sin(ph * math.pi)) if t > TURN + 0.3 and int(ph) % 2 == 0 else 0.0
        return dict(x=FX, y=G - 34 * hop, p=cheer(t), f=1)
    end = BUILD0 + N_CHAIRS * CYCLE
    return dict(x=FX, y=G, p=mix(base, dict(stand(), lean=6, head=-4), seg(t, end + 0.15, end + 0.45)), f=1, hammer=True)


# ------------------------------------------------------------------ world
def chair(c, x, y, s=1.0, a=1.0, crooked=0.0, polish=0.0, build=1.0, col=(176, 128, 84)):
    """side view, back on the right. build 0..1: legs → seat → back appear"""
    if a <= 0: return
    c.saveLayerAlpha(skia.Rect.MakeXYWH(x - 80 * s, y - 180 * s, 160 * s, 200 * s), int(255 * a)) if a < 1 else c.save()
    dark = tuple(int(v * 0.72) for v in col)
    legs = [(x - 24 * s, 0), (x + 24 * s, crooked * 5 * s)]
    if build > 0:
        for lx_, d in legs:
            h = 70 * s * clamp(build / 0.35)
            c.drawLine(lx_, y, lx_ + d, y - h, P(INK, stroke=11 * s)); c.drawLine(lx_, y, lx_ + d, y - h, P(dark, stroke=6 * s))
    if build > 0.35:
        k = clamp((build - 0.35) / 0.3)
        r = skia.Rect.MakeXYWH(x - 32 * s, y - 78 * s, 64 * s * k, 12 * s)
        c.drawRect(r, P(col)); c.drawRect(r, P(INK, stroke=4 * s))
    if build > 0.65:
        k = clamp((build - 0.65) / 0.35)
        bx = x + 24 * s + crooked * 4 * s
        c.drawLine(bx, y - 74 * s, bx + 8 * s * crooked, y - (74 + 66 * k) * s, P(INK, stroke=11 * s))
        c.drawLine(bx, y - 74 * s, bx + 8 * s * crooked, y - (74 + 66 * k) * s, P(col, stroke=6 * s))
    if polish > 0:   # the perfectionist's chair shines
        c.drawLine(x - 24 * s, y - 75 * s, x + 20 * s, y - 75 * s, P((255, 245, 220), 0.6 * polish, stroke=3 * s))
    c.restore()


def sold_tag(c, x, y, a, pop):
    if a <= 0: return
    c.save(); c.translate(x, y); c.scale(pop, pop)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-36, -15, 72, 30), 8, 8)
    c.drawRRect(rr, P(AMBER, a)); c.drawRRect(rr, P(INK, a, stroke=3))
    text(c, "SOLD", 0, 9, F_CAP, 22, INK, a)
    c.restore()


def calendar(c, t):
    day = 19 + (1 if t > 4.0 else 0) + (1 if t > 8.0 else 0)
    x, y = 262, 930
    c.drawRect(skia.Rect.MakeXYWH(x, y, 92, 96), P((236, 232, 222))); c.drawRect(skia.Rect.MakeXYWH(x, y, 92, 96), P(INK, stroke=4))
    c.drawRect(skia.Rect.MakeXYWH(x, y, 92, 24), P((200, 80, 70)))
    text(c, "DAY", x + 46, y + 52, F_CAP, 23, INK, 1.0)
    text(c, str(day), x + 46, y + 84, F_CAP, 34, INK, 1.0)
    for d0 in (4.0, 8.0):                                      # page flips away
        if d0 < t < d0 + 0.4:
            k = (t - d0) / 0.4
            c.drawRect(skia.Rect.MakeXYWH(x + 30 * k, y + 60 * k, 92 * (1 - k), 96 * (1 - k)), P((236, 232, 222), 1 - k))


def board(c, t):
    n = chairs_done(t)
    x, y = 450, 870
    c.drawRect(skia.Rect.MakeXYWH(x, y, 130, 84), P((44, 56, 52))); c.drawRect(skia.Rect.MakeXYWH(x, y, 130, 84), P((120, 86, 60), stroke=8))
    text(c, "DONE", x + 65, y + 31, F_CAP, 24, (230, 232, 220), 0.95, spacing=2)
    land = BUILD0 + n * CYCLE
    k = 1 + 0.35 * math.exp(-max(0, t - land) * 8) if n > 0 else 1
    c.save(); c.translate(x + 65, y + 72); c.scale(k, k)
    text(c, str(n), 0, 0, F_CAP, 40, AMBER, 1.0)
    c.restore()


def world(c, t):
    u = light(t)
    wall = lerpc((84, 92, 116), (150, 112, 82), u)
    c.drawRect(skia.Rect.MakeLTRB(-300, 0, W + 300, G), P(wall))
    for i, bx in enumerate(range(-300, W + 300, 58)):
        c.drawLine(bx, 760, bx, G, P((40, 36, 44), 0.35, stroke=3))
    # slanted roof with a skylight
    roof = poly([(-300, 760), (W + 300, 690), (W + 300, 730), (-300, 800)])
    c.drawPath(roof, P(lerpc((60, 64, 84), (110, 80, 62), u))); c.drawPath(roof, P(INK, stroke=6))
    sk = poly([(380, 745), (470, 739), (470, 777), (380, 783)])
    c.drawPath(sk, P(lerpc((120, 150, 200), (255, 226, 160), u))); c.drawPath(sk, P(INK, stroke=5))
    # light from the skylight: faint blue → golden shaft onto her stack
    beam = poly([(380, 783), (470, 777), (790, G), (560, G)])
    sh = skia.GradientShader.MakeLinear([(425, 780), (680, G)], [C(lerpc((160, 190, 255), (255, 214, 140), u), 0.18 + 0.4 * u), C((255, 200, 120), 0.04 + 0.12 * u)])
    c.drawPath(beam, skia.Paint(AntiAlias=True, Shader=sh))
    rng = np.random.default_rng(11)                          # dust dancing in the light – the shop is never still
    for i in range(46):
        k = (rng.uniform(0, 1) + t * rng.uniform(0.06, 0.16)) % 1.0
        px = lerp(lerp(390, 470, rng.uniform(0, 1)), lerp(560, 790, rng.uniform(0, 1)), k) + 14 * math.sin(t * 1.7 + i)
        c.drawCircle(px, lerp(790, G - 20, k), 2.6, P(lerpc((210, 225, 255), (255, 240, 200), u), 0.55 + 0.25 * u))
    # pegboard with tools (left) and a workbench
    c.drawRect(skia.Rect.MakeXYWH(120, 900, 120, 110), P((150, 118, 84))); c.drawRect(skia.Rect.MakeXYWH(120, 900, 120, 110), P(INK, stroke=4))
    for i in range(3):
        c.drawLine(142 + i * 36, 920, 142 + i * 36, 980, P((70, 70, 80), stroke=6))
    c.drawRect(skia.Rect.MakeXYWH(-40, 1150, 200, 18), P((140, 100, 66))); c.drawRect(skia.Rect.MakeXYWH(-40, 1150, 200, 18), P(INK, stroke=4))
    c.drawLine(0, 1168, 0, G, P(INK, stroke=8)); c.drawLine(140, 1168, 140, G, P(INK, stroke=8))
    calendar(c, t)
    board(c, t)
    # floor
    c.drawRect(skia.Rect.MakeLTRB(-300, G, W + 300, H + 300), P(lerpc((70, 64, 66), (128, 96, 70), u)))
    for i in range(6): c.drawLine(-300, G + 30 + i * 46, W + 300, G + 30 + i * 46, P((40, 34, 34), 0.5, stroke=3))
    c.drawLine(-300, G, W + 300, G, P(INK, stroke=5))
    # sawdust piles grow under his chair
    pile = 6 + 10 * seg(t, 0, 11)
    c.drawOval(skia.Rect.MakeXYWH(PCHAIR - 50, G - pile * 0.6, 100, pile), P((226, 200, 150), 0.9))
    return u


def frame(c, t):
    sway = 1 + 0.018 * math.sin(t * 0.9)                    # slow handheld drift: the shot is never frozen
    c.save(); c.translate(540 + 10 * math.sin(t * 0.6), G + DY); c.scale(SC * sway, SC * sway); c.translate(-540, -G)
    u = world(c, t)
    # his chair: always the same one, polished
    chair(c, PCHAIR, G, 1.0, polish=0.6 + 0.4 * math.sin(t * 3), col=(196, 150, 100))
    # her stack: one chair per cycle, a little crooked; SOLD tags at the turn
    n = chairs_done(t)
    for k in range(n):
        land = BUILD0 + (k + 1) * CYCLE
        slide = ease(clamp((t - land + 0.3) / 0.3))
        y = G - k * 34
        x = lerp(FCHAIR, STACK, slide) if k == n - 1 else STACK
        chair(c, x + (k % 2) * 6, y if slide >= 1 or k < n - 1 else lerp(G, y, slide), 0.86, crooked=0.6 + 0.4 * ((k * 7) % 3) / 2)
    if t < TURN and n < N_CHAIRS:                              # the one she is building
        chair(c, FCHAIR, G, 0.86, crooked=0.7, build=clamp(cycle_u(t) / 0.75))
    for k in range(n):
        t0 = TURN + 0.1 * k
        if t > t0:
            pop = 1 + 0.4 * math.exp(-(t - t0) * 9)
            sold_tag(c, STACK - 48, G - k * 34 - 70, min(1.0, (t - t0) / 0.1), pop)
    # figures
    pf = smooth(perfectionist, t); fn = smooth(finisher, t)
    lo = (1, -0.6) if t < TURN else (1, -1)
    shadow(c, pf["x"], pf["y"], S, 0.3); shadow(c, fn["x"], G, S, 0.3)
    jp = figure(c, pf["x"], pf["y"], pf["p"], s=S, facing=pf["f"], body=PER_BODY, rim=((170, 200, 255), 0.5), light=lo, reach=pf.get("reach"))
    jf = figure(c, fn["x"], fn["y"], fn["p"], s=S, facing=fn["f"], body=FIN_BODY, rim=(lerpc((255, 196, 110), (255, 214, 150), u), 0.6), light=lo,
                reach=fn.get("reach"))
    if fn.get("hammer"):
        hx, hy = jf["hand_f"]; sx, sy = jf["el_f"]
        c.save(); c.translate(hx, hy); c.rotate(math.degrees(math.atan2(hx - sx, -(hy - sy))))
        c.drawLine(0, 6, 0, -40, P(INK, stroke=10)); c.drawLine(0, 6, 0, -40, P((180, 130, 80), stroke=5))
        c.drawRect(skia.Rect.MakeXYWH(-16, -54, 32, 16), P((90, 96, 110))); c.drawRect(skia.Rect.MakeXYWH(-16, -54, 32, 16), P(INK, stroke=4))
        c.restore()
    # sanding dust
    if t < TURN and not any(ts < t < ts + 1.4 for ts, _ in TALK[:3]):
        rng = np.random.default_rng(int(t * 10))
        for i in range(6):
            k = (t * 3 + i / 6) % 1.0
            c.drawCircle(PCHAIR + rng.uniform(-30, 30), G - 80 - 40 * k, 3 + 3 * k, P((236, 214, 170), 0.6 * (1 - k)))
    if TURN + 1.0 < t < TURN + 1.6:                            # he blows the dust off
        k = (t - TURN - 1.0) / 0.6
        c.drawCircle(PCHAIR, G - 80, 20 + 40 * k, P((236, 214, 170), 0.5 * (1 - k)))
    # labels + bubbles
    plate_label(c, "PERFECTIONIST", jp["head"][0], jp["head"][1] - 52, GREY, 0.9)
    plate_label(c, "FINISHER", jf["head"][0], jf["head"][1] - 52, AMBER, 0.95)
    for ts, txt in TALK:
        if ts < t < ts + 1.9:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.6, ts + 1.9))
            bubble(c, 330, jp["head"][1] - 170, txt, a, "speech", tail=(jp["head"][0] + 8, jp["head"][1] - 60), size=32,
                   pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    if u > 0: c.drawRect(skia.Rect.MakeWH(W, H), P((255, 190, 110), 0.05 * u))
    vignette(c, 0.4)
    grain(c, t, 0.035)
    end_text(c, t, 13.6, "Perfect never got sold.", "Done got better.", "Finish it. Then improve it.", y=1430)


def events():
    ev = []
    for ts, _ in TALK: ev.append(["pop", ts])
    for k in range(N_CHAIRS):
        for h in range(3): ev.append(["thud", BUILD0 + k * CYCLE + (h + 0.7) * 0.25 * CYCLE])
        ev.append(["slide", BUILD0 + (k + 1) * CYCLE - 0.25])
    for k in range(N_CHAIRS): ev.append(["pop", TURN + 0.1 * k])
    ev += [["sunrise", TURN - 1.0], ["summit", TURN], ["text", 13.6], ["text2", 14.4]]
    return ev


def overlay(c, t):
    series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 0.6, 2.0, 4.6, 6.4, 8.8, 10.5, 11.4, 12.4, 14.0, 15.2, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore(); overlay(c, t)
        stills(opening, ts, "check/ep13")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs))
    else:
        finish_v2("Folge13_Finisher", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
