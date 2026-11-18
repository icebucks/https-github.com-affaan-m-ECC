"""Episode 15 (TikTok: Part 12): TALKER vs WALKER – promised by the Part 11 cliffhanger.
Alpine trailhead below a snow-capped peak, blue pre-dawn mist -> pink alpenglow -> sunrise breaking over the summit.
The talker films himself at the trailhead with his back to the mountain ("Big climb today, guys!"). The walker just
shoulders her pack and goes – up the switchbacks, smaller and smaller. When the sun breaks over the peak she plants a
flag at the top. He turns around: he has not taken a single step."""
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 12                     # TikTok part number (internal episode 15)
G = 1240
SC = 1.4
DY = 60
S = 1.0
TURN = 10.2                    # she plants the flag, the sun breaks over the peak, he turns around
TX = 300                       # the talker never leaves this spot
TALK = [(0.9, "Big climb today, guys!"), (3.6, "Day 1 of my summit era!"), (6.2, "First, a gear review…"),
        (8.4, "Okay… tomorrow. For real."), (TURN + 0.6, "Wait… she's up there?!")]
TK_BODY = (196, 202, 216)
WK_BODY = (255, 226, 178)
HOOK = "He's told everyone. 0 steps.\nWatch who reaches the top."
FOCUS = (200, 1100)            # opening close-up: the talker filming himself, the walker setting off
CTA = "Part 13 tomorrow:\nthe one who never jumps"
PEAK = (600, 800)
# switchback trail up the face: (x, y, scale) – she gets smaller as she climbs away from us
TRAIL = [(x, 1240 - (1240 - y) * 432 / 496, s) for x, y, s in
         [(420, 1240, 1.0), (480, 1214, 0.9), (562, 1160, 0.78), (440, 1100, 0.68), (566, 1030, 0.6),
          (470, 962, 0.53), (572, 884, 0.47), (548, 822, 0.43), (600, 744, 0.4)]]
T0, T1 = 0.5, TURN - 0.45      # she walks from T0 to T1


def light(t): return seg(t, 3.0, TURN + 1.5)        # 0 = blue dawn, 1 = sunrise


def _trail_lengths():
    d = [0.0]
    for (x0, y0, s0), (x1, y1, s1) in zip(TRAIL, TRAIL[1:]):
        d.append(d[-1] + math.hypot(x1 - x0, y1 - y0) / (0.5 * (s0 + s1)))   # "true" distance: far away = longer
    return d


DIST = _trail_lengths()


def on_trail(u):
    """position, scale and walking direction at fraction u of the trail"""
    D = u * DIST[-1]
    for i in range(len(TRAIL) - 1):
        if D <= DIST[i + 1] or i == len(TRAIL) - 2:
            k = clamp((D - DIST[i]) / (DIST[i + 1] - DIST[i]))
            (x0, y0, s0), (x1, y1, s1) = TRAIL[i], TRAIL[i + 1]
            return lerp(x0, x1, k), lerp(y0, y1, k), lerp(s0, s1, k), (1 if x1 >= x0 else -1)


# ------------------------------------------------------------------ characters
def talker(t):
    x, y = TX, G
    if t < TURN + 0.2:                                   # back to the mountain, filming himself
        g = math.sin(t * 5.0)
        p = dict(stand(), lean=-2, head=-6 + 3 * math.sin(t * 2.3), arm_b=38 + 22 * g, elb_b=58 + 18 * g)
        if 6.0 < t < 8.2: p.update(arm_b=24, elb_b=96 + 10 * math.sin(t * 7))            # points at his own gear
        if 8.2 < t < TURN: p.update(arm_b=12, elb_b=84, lean=-4, head=-10)                # palm up: "tomorrow"
        q = seg(t, TURN - 0.5, TURN + 0.1)              # phone comes down to the chest before he turns
        return dict(x=x, y=y, p=p, f=-1, reach={"f": (x - lerp(56, 18, q), y - lerp(176, 138, q))})
    k = seg(t, TURN + 0.2, TURN + 0.7)                   # turns around, phone sinks, stares up at the peak
    p = dict(stand(), lean=-6, head=-28, arm_b=4, elb_b=14, leg_f=4, leg_b=-4)
    return dict(x=x, y=y, p=p, f=1, reach={"f": (x + lerp(14, 34, k), y - lerp(138, 118, k))})


def walker(t):
    if t < T0:
        x, y, s, d = on_trail(0.0)
        return dict(x=x, y=y, s=s, p=dict(stand(), head=-8), f=1)
    if t < T1:
        u = (t - T0) / (T1 - T0)
        u = 0.12 * ease(clamp(u / 0.12)) + max(0.0, u - 0.12) if u < 0.12 else u    # gentle start
        x, y, s, d = on_trail(u)
        return dict(x=x, y=y, s=s, p=walk(t * 7.5, lean=10, stride=22, arm=26), f=d)
    x, y, s, d = on_trail(1.0)
    k = seg(t, TURN, TURN + 0.5)
    return dict(x=x, y=y, s=s, p=mix(dict(stand(), head=-10), cheer(t), k), f=-1 if t > T1 + 0.3 else 1)


# ------------------------------------------------------------------ world
def pine(c, x, y, sc, col):
    c.drawRect(skia.Rect.MakeXYWH(x - 6 * sc, y - 30 * sc, 12 * sc, 30 * sc), P((40, 34, 40)))
    for k in range(4):
        w = (60 - 11 * k) * sc; yy = y - (24 + 34 * k) * sc
        c.drawPath(poly([(x - w, yy), (x + w, yy), (x, yy - 62 * sc)]), P(col))


def world(c, t):
    u = light(t)
    sky(c, t, lerpc((40, 56, 104), (86, 120, 190), u), lerpc((92, 110, 170), (250, 170, 160), u),
        lerpc((150, 160, 200), (255, 214, 160), u), 1000)
    # sun rising behind the peak, glow spreading
    sy = lerp(940, 790, seg(t, TURN - 1.8, TURN + 3.0))
    c.drawCircle(PEAK[0] + 70, sy, 240, P((255, 200, 140), 0.35 * u, blur=60))
    c.drawCircle(PEAK[0] + 70, sy, 62, P((255, 240, 200), 0.95))
    # far ridge
    c.drawPath(poly([(-300, 1000), (60, 900), (250, 960), (420, 860), (820, 940), (1000, 870), (W + 300, 960), (W + 300, G), (-300, G)]),
               P(lerpc((88, 100, 150), (170, 120, 150), u)))
    # the peak: shadow side + alpenglow side + snow cap
    px, py = PEAK
    c.drawPath(poly([(px, py), (180, 1150), (180, G + 10), (px, G + 10)]), P(lerpc((78, 86, 128), (128, 92, 120), u)))
    c.drawPath(poly([(px, py), (px, G + 10), (990, G + 10), (990, 1100)]), P(lerpc((100, 110, 156), (214, 132, 130), u)))
    c.drawPath(poly([(px, py), (px - 64, py + 64), (px - 40, py + 56), (px - 20, py + 78), (px + 6, py + 58), (px + 34, py + 82),
                     (px + 70, py + 72)]), P(lerpc((210, 220, 240), (255, 226, 214), u)))
    # the trail: pale dashes zig-zagging up the face
    path = skia.Path(); path.moveTo(*TRAIL[0][:2])
    for x, y, _ in TRAIL[1:]: path.lineTo(x, y)
    pt = P(lerpc((150, 150, 180), (255, 214, 180), u), 0.7, stroke=5)
    pt.setPathEffect(skia.DashPathEffect.Make([14, 10], 0)); c.drawPath(path, pt)
    # drifting mist bands (keep every second alive)
    for i in range(5):
        mx = (i * 260 + t * (22 + 6 * i)) % 1500 - 300
        my = 1010 + 46 * i + 10 * math.sin(t * 0.7 + i)
        c.drawOval(skia.Rect.MakeXYWH(mx, my, 420, 46), P(lerpc((190, 200, 230), (255, 220, 210), u), 0.22 * (1 - 0.5 * u), blur=18))
    # pines on both sides of the trailhead
    for i, (x, sc) in enumerate(((150, 1.2), (215, 0.95), (760, 1.1), (835, 1.3), (900, 1.0))):
        pine(c, x, G + 6, sc, lerpc((40, 60, 70), (60, 74, 66), u))
    # meadow
    c.drawRect(skia.Rect.MakeLTRB(-300, G, W + 300, H + 300), P(lerpc((60, 80, 80), (96, 112, 70), u)))
    c.drawLine(-300, G, W + 300, G, P(INK, stroke=5))
    tufts(c, G, lerpc((70, 96, 84), (120, 140, 80), u))
    # trailhead sign
    c.drawLine(430, G, 430, G - 104, P(INK, stroke=12)); c.drawLine(430, G, 430, G - 104, P((150, 104, 64), stroke=7))
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(350, G - 140, 176, 44), 8, 8)
    c.drawRRect(r, P((190, 140, 84))); c.drawRRect(r, P(INK, stroke=4))
    label(c, "SUMMIT", 426, G - 108, INK, 1.0)
    c.drawPath(poly([(494, G - 106), (504, G - 128), (514, G - 106)]), P(INK))
    return u


def phone(c, hand, f, live):
    c.save(); c.translate(*hand); c.rotate(-12 * f)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-13, -24, 26, 46), 6, 6)
    c.drawRRect(r, P((30, 34, 44))); c.drawRRect(r, P(INK, stroke=4))
    c.drawRect(skia.Rect.MakeXYWH(-9, -19, 18, 34), P((150, 200, 255), 0.85))
    c.restore()
    if live > 0:
        c.drawCircle(hand[0] - 30, hand[1] - 60, 70, P((150, 200, 255), 0.10 * live, blur=30))     # screen glow on his face


def flag(c, x, y, s, k):
    if k <= 0: return
    h = 120 * s * ease(k)
    c.drawLine(x, y, x, y - h, P(INK, stroke=8 * s + 2)); c.drawLine(x, y, x, y - h, P((220, 220, 230), stroke=4 * s + 1))
    w = 56 * s * ease(clamp(k * 1.4 - 0.4)); wv = 6 * s * math.sin(NOW_T[0] * 9)
    c.drawPath(poly([(x, y - h), (x + w, y - h + 18 * s + wv), (x, y - h + 38 * s)]), P(AMBER))


NOW_T = [0.0]


def frame(c, t):
    NOW_T[0] = t
    sway = 1 + 0.018 * math.sin(t * 0.9) + 0.06 * seg(t, 13.6, T_END)   # handheld drift, slow push-in at the end
    c.save(); c.translate(540 + 10 * math.sin(t * 0.6), G + DY); c.scale(SC * sway, SC * sway); c.translate(-540, -G)
    u = world(c, t)
    lo = (1, -0.6)
    # the walker on the mountain
    wk = smooth(walker, t)
    ws = wk["s"]
    shadow(c, wk["x"], wk["y"], S * ws, 0.25)
    jw = figure(c, wk["x"], wk["y"], wk["p"], s=S * ws, facing=wk["f"], body=WK_BODY, rim=((255, 210, 170), 0.4 + 0.4 * u), light=lo)
    c.save(); c.translate(jw["sh"][0] - 16 * ws * wk["f"], jw["sh"][1] + 26 * ws); c.scale(ws, ws)
    bp = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-22, -26, 44, 52), 10, 10)
    c.drawRRect(bp, P((230, 170, 80))); c.drawRRect(bp, P(INK, stroke=4)); c.restore()
    flag(c, PEAK[0] + 22, PEAK[1] + 8, 0.9, seg(t, TURN - 0.2, TURN + 0.5))
    # the talker in front, back to the mountain
    tk = smooth(talker, t)
    shadow(c, tk["x"], tk["y"], S, 0.3)
    jt = figure(c, tk["x"], tk["y"], tk["p"], s=S, facing=tk["f"], body=TK_BODY, rim=((190, 210, 255), 0.5), light=lo, reach=tk.get("reach"))
    phone(c, jt["hand_f"], tk["f"], 1 - seg(t, TURN, TURN + 0.5))
    if t < TURN:
        plate_label(c, "LIVE", jt["hand_f"][0] + 14, jt["hand_f"][1] - 44, (255, 110, 100), 0.9 * (0.75 + 0.25 * math.sin(t * 6)) * (1 - seg(t, TURN - 0.8, TURN - 0.5)))
    # labels: talker always; walker until she is far up, then again on the summit
    plate_label(c, "TALKER", jt["head"][0], jt["head"][1] - 56, GREY, 0.9)
    wa = 0.95 * (1 - seg(t, 2.6, 3.2)) + 0.95 * seg(t, TURN + 0.6, TURN + 1.1) * (1 - seg(t, 14.3, 14.7))   # clear for the cliffhanger
    plate_label(c, "WALKER", jw["head"][0], jw["head"][1] - 22 - 34 * ws - 30 * (1 - seg(t, 1.2, 1.8)), AMBER, wa)
    for ts, txt in TALK:
        if ts < t < ts + 2.0:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.7, ts + 2.0))
            hy = jt["head"][1] - 150
            bubble(c, clamp(jt["head"][0] + 50, 370, 600), hy, txt, a, "speech", tail=(jt["head"][0] + 6, jt["head"][1] - 70), size=30,
                   pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), P((255, 170, 120), 0.05 * u))
    vignette(c, 0.4)
    grain(c, t, 0.035)
    end_text(c, t, 13.6, "He told everyone.", "She told no one.", "Talk less. Walk more.", y=1430)


def events():
    ev = []
    for ts, _ in TALK: ev.append(["pop", ts])
    for k in range(int((T1 - T0) / 0.5)): ev.append(["step", T0 + k * 0.5, False])
    ev += [["sunrise", TURN - 0.6], ["summit", TURN], ["slide", TURN + 0.3], ["text", 13.6], ["text2", 14.4]]
    return ev


def overlay(c, t):
    series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 0.6, 2.0, 4.0, 6.6, 8.6, 9.8, 10.4, 11.2, 12.6, 14.2, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore(); overlay(c, t)
        stills(opening, ts, "check/ep15")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs))
    else:
        finish_v2("Folge15_TalkerWalker", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
