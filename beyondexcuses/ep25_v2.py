"""Episode 25 v2 (TikTok: Part 22): IDEA HOARDER vs SHIPPER – rebuilt to Retention-Standard v2 (episodes.md).
A garage at night. Frame 0: he slaps a sticky note on the wall (new idea!), she tightens the first screw of ONE desk lamp.
Time-lapse DAY 1 → DAY 30: the wall fills with notes (IDEAS 1 → 100), half-built things pile up around him; her lamp grows.
TURN 6.4 s: click – her lamp lights up, the parcel gets the SHIPPED stamp (DONE 1).
Second turn: the light falls on his wall – "Pick one. Finish it." – he tears the notes down and keeps ONE.
Loop: he slaps that one note back on the empty wall → frame 0."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 22                     # TikTok part number (internal episode 25)
TURN = 6.4                     # lamp lights up + SHIPPED
LAPSE0, LAPSE1 = 2.2, 5.2      # DAY 1 -> DAY 30
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
HX = 40                        # his spot
SX = 318                       # her spot (facing left)
BENCH = (172, 286)
BENCH_H = 120
LAMP = (204, G - BENCH_H)
BOX = (258, G - BENCH_H)
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Same garage. Same 30 days.\nWho ships something?"
CTA = "Part 23 next:\nthe one who saves $1 a day"
END_TXT = "Finish one. Then start two."
TALK = [(1.15, "h", "Wait, better idea!"), (5.3, "h", "I'll finish... someday."), (7.5, "s", "Pick one. Finish it.")]
SLAPS = [0.0, 1.1, 1.8] + [LAPSE0 + 0.4 * i for i in range(8)] + [12.49]


def ideas(t):
    if t >= 8.5: return 1
    if t >= LAPSE1: return 100
    if t >= LAPSE0: return 3 + int(97 * seg(t, LAPSE0, LAPSE1) ** 1.3)
    return sum(1 for s in SLAPS[:3] if t >= s)


def slap_k(t):
    """0..1 arm up to the wall for each slap (starts 0.25 s before, lands on the slap)"""
    k = 0.0
    for s in SLAPS:
        k = max(k, seg(t, s - 0.25, s) * (1 - seg(t, s + 0.1, s + 0.3)))
    return k


def h_x(t):
    if LAPSE0 < t < LAPSE1: return HX + 30 * math.sin((t - LAPSE0) * 4)        # hops between half-built things
    return HX


# ------------------------------------------------------------------ characters
def hoarder(t):
    x = h_x(t)
    p = stand()
    if LAPSE0 < t < LAPSE1: p = walk(t * 9, stride=14, arm=16)
    f = -1 if math.cos((t - LAPSE0) * 4) >= 0 or not (LAPSE0 < t < LAPSE1) else -0.99
    p = mix(p, dict(stand(), lean=-6, head=-24, arm_f=150, elb_f=14, arm_b=-10, elb_b=12), slap_k(t))
    if LAPSE1 <= t < 7.4: p = mix(p, dict(stand(), lean=10, head=10, arm_f=10, elb_f=30, arm_b=-6, elb_b=20), seg(t, LAPSE1, LAPSE1 + 0.3))   # tired
    if 6.6 < t < 8.2: p = mix(p, dict(stand(), lean=0, head=-8), seg(t, 6.6, 6.9) * (1 - seg(t, 7.9, 8.2)))    # looks at the light
    if 8.1 < t < 8.9:                                                       # tears the notes down
        sw = math.sin((t - 8.1) * 14)
        p = mix(p, dict(stand(), lean=-4, head=-18, arm_f=110 + 30 * sw, elb_f=20, arm_b=60 - 30 * sw, elb_b=30), seg(t, 8.1, 8.25) * (1 - seg(t, 8.7, 8.9)))
    if 9.0 < t < 11.6:                                                      # works on ONE thing: the robot
        sw = 0.5 + 0.5 * math.sin((t - 9.0) * 8)
        p = mix(p, dict(crouch(), arm_f=55 + 25 * sw, elb_f=30, arm_b=50, elb_b=30, head=-10), seg(t, 9.0, 9.4) * (1 - seg(t, 11.2, 11.6)))
    return dict(x=x, p=p, f=f)


def shipper(t):
    p = dict(stand(), lean=16, head=14, arm_f=70 + 14 * math.sin(t * (8 if t < LAPSE0 else 16)), elb_f=40, arm_b=60, elb_b=50)
    if 5.4 < t < TURN: p = dict(p, arm_f=lerp(p["arm_f"], 95, seg(t, 5.4, 5.8)), elb_f=20)                    # reaches for the switch
    if TURN < t < 7.4: p = mix(p, cheer(t), seg(t, TURN + 0.1, TURN + 0.4) * (1 - seg(t, 7.1, 7.4)))
    if 7.4 < t < 9.0: p = mix(p, dict(offer(), arm_f=100, elb_f=10, head=-6), seg(t, 7.4, 7.7) * (1 - seg(t, 8.7, 9.0)))   # points at his wall
    if t > 9.0: p = dict(p, arm_f=70 + 14 * math.sin(t * 8))                # next project
    return dict(x=SX, p=p, f=-1)


# ------------------------------------------------------------------ world
def robot(c, x, a=1.0, done=0.0):
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 22, G - 52, 44, 52), 6, 6)
    c.drawRRect(r, P((150, 160, 175), a)); c.drawRRect(r, P(INK, a, stroke=3))
    for k in range(3): c.drawLine(x - 12 + k * 12, G - 52, x - 18 + k * 16, G - 68, P((200, 80, 70), a, stroke=2))


def bike(c, x, a=1.0):
    c.drawCircle(x - 22, G - 18, 17, P(INK, a, stroke=4))
    c.drawPath(poly([(x - 22, G - 18), (x, G - 44), (x + 22, G - 18), (x - 4, G - 18)]), P((60, 120, 180), a, stroke=5))


def drone(c, x, a=1.0):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 18, G - 24, 36, 18), 5, 5), P((80, 80, 90), a))
    for dx in (-32, 32): c.drawLine(x, G - 18, x + dx, G - 30, P(INK, a, stroke=3))
    c.drawOval(skia.Rect.MakeXYWH(x - 48, G - 36, 30, 8), P((120, 200, 230), a))


def lamp(c, t):
    x, y = LAMP
    arm = 0.15 + 0.85 * seg(t, LAPSE0, LAPSE1 - 0.2)
    on = seg(t, TURN, TURN + 0.12)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 24, y - 11, 48, 11), 4, 4), P((60, 60, 70)))
    ax, ay = x + 26 * arm, y - 11 - 84 * arm
    c.drawLine(x, y - 11, ax, ay, P((70, 70, 80), stroke=6))
    if t > LAPSE1 - 0.1:                                                   # shade
        sh = poly([(ax - 34, ay + 10), (ax + 8, ay - 6), (ax + 22, ay + 12), (ax - 18, ay + 32)])
        c.drawPath(sh, P(AMBER)); c.drawPath(sh, P(INK, stroke=3))
        if on > 0:
            c.drawPath(poly([(ax - 26, ay + 26), (ax - 2, ay + 28), (ax + 20, y), (ax - 90, y)]), P((255, 230, 150), 0.35 * on))
            c.drawCircle(ax - 12, ay + 26, 60, P((255, 220, 140), 0.5 * on, blur=26))
            # the light spills over to his wall (second turn)
            c.drawCircle(0, G - 330, 230, P((255, 220, 140), 0.18 * on * seg(t, 6.7, 7.3), blur=70))


def parcel(c, t):
    if t < TURN: return
    x, y = BOX
    k0 = seg(t, TURN, TURN + 0.15)
    c.save(); c.translate(x, y); c.scale(k0, k0)
    c.drawRect(skia.Rect.MakeXYWH(-22, -36, 44, 36), P((190, 150, 100))); c.drawRect(skia.Rect.MakeXYWH(-22, -36, 44, 36), P(INK, stroke=3))
    c.restore()


def stamp(c, t):
    x, y = BOX[0] - 40, BOX[1]
    k = seg(t, TURN + 0.1, TURN + 0.3)
    if t > TURN and k > 0:
        c.save(); c.translate(x, y - 58); c.rotate(-12); sc = 1 + 0.6 * (1 - k); c.scale(sc, sc)
        c.drawRect(skia.Rect.MakeXYWH(-46, -15, 92, 30), P((250, 240, 230), 0.92)); c.drawRect(skia.Rect.MakeXYWH(-46, -15, 92, 30), P((220, 60, 50), stroke=3))
        text(c, "SHIPPED", 0, 9, F_CAP, 23, (220, 60, 50), 1.0)
        c.restore()


def notes(c, t):
    n = ideas(t) if t < 8.2 else 100
    rng = np.random.default_rng(5)
    for i in range(min(n, 100)):
        x = -50 + rng.uniform(0, 250) if i else 10; y = G - 470 + rng.uniform(0, 200) if i else G - 400
        rot = rng.uniform(-14, 14)
        if i == 0 and t > 8.3 and t < 12.49: continue                     # the one note he keeps (in his hand)
        fall = seg(t, 8.25 + (i % 7) * 0.05, 8.9 + (i % 7) * 0.05) if i else 0
        a = 1 - seg(t, 9.6, 10.2) if fall > 0 else 1
        if a <= 0: continue
        y += (G - 8 - y) * fall ** 2; rot += 70 * fall * (1 if i % 2 else -1)
        col = [(255, 230, 120), (255, 170, 190), (150, 220, 255), (180, 240, 160)][i % 4]
        pop = 1 + 0.6 * (1 - seg(t, s_of(i), s_of(i) + 0.15)) if t < s_of(i) + 0.15 else 1
        c.save(); c.translate(x, y); c.rotate(rot); c.scale(pop, pop)
        c.drawRect(skia.Rect.MakeXYWH(-11, -11, 22, 22), P(col, 0.95 * a)); c.drawRect(skia.Rect.MakeXYWH(-11, -11, 22, 22), P(INK, 0.5 * a, stroke=1.5)); c.restore()


def s_of(i):
    return SLAPS[i] if i < 3 else -1


def world(c, t):
    sh = skia.GradientShader.MakeLinear([(0, G - 800), (0, G)], [C((86, 80, 96)), C((138, 118, 108))])
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, 700, G), skia.Paint(Shader=sh))
    c.drawRect(skia.Rect.MakeLTRB(210, G - 520, 420, G - 300), P((170, 138, 104)))           # pegboard
    for gx in range(222, 420, 26):
        for gy in range(G - 508, G - 310, 26): c.drawCircle(gx, gy, 2.5, P((110, 86, 64)))
    c.drawLine(250, G - 480, 250, G - 400, P((90, 90, 100), stroke=7)); c.drawCircle(380, G - 440, 24, P((90, 90, 100), stroke=5))
    c.drawLine(120, G - 900, 120, G - 508, P((40, 30, 30), stroke=3)); c.drawCircle(120, G - 500, 11, P((255, 220, 150)))
    c.drawCircle(120, G - 500, 240, P((255, 200, 130), 0.12, blur=70))
    notes(c, t)
    c.drawRect(skia.Rect.MakeLTRB(-300, G, 700, G + 500), P((110, 104, 100)))
    for k in range(-300, 700, 90): c.drawLine(k, G, k - 50, G + 400, P((90, 84, 80), 0.5, stroke=3))
    # his half-built things pile up during the time-lapse
    robot(c, -20)
    n = int(5 * seg(t, LAPSE0, LAPSE1)) if t < LAPSE1 else 5
    for i, (x, fn) in enumerate([(100, bike), (-60, drone), (130, robot), (70, drone), (-40, bike)][:n]):
        a = 1 - seg(t, 9.0, 9.6) * (i > 0)                                 # pushed aside (fade) once he picks ONE
        fn(c, x, a)
    x0, x1 = BENCH; top = G - BENCH_H
    c.drawRect(skia.Rect.MakeLTRB(x0, top, x1, top + 14), P((150, 104, 70))); c.drawRect(skia.Rect.MakeLTRB(x0, top, x1, top + 14), P(INK, stroke=3))
    for px in (x0 + 8, x1 - 8): c.drawLine(px, top + 14, px, G, P((110, 76, 52), stroke=9))
    lamp(c, t); parcel(c, t)


def to_screen(p): return (470 + (p[0] - 160) * K, 1440 + (p[1] - G) * K)


def frame(c, t):
    c.save(); c.translate(470, 1440); c.scale(K, K); c.translate(-160, -G)
    world(c, t)
    lo = (1, -0.6)
    h = hoarder(t)
    jh = figure(c, h["x"], G, h["p"], s=S, facing=h["f"], body=H_BODY, rim=((210, 220, 255), 0.5), light=lo)
    if 8.3 < t < 12.49:                                                    # the one note he keeps
        hx, hy = jh["hand_f"]
        c.drawRect(skia.Rect.MakeXYWH(hx - 11, hy - 11, 22, 22), P((255, 230, 120))); c.drawRect(skia.Rect.MakeXYWH(hx - 11, hy - 11, 22, 22), P(INK, 0.5, stroke=1.5))
    sp = shipper(t)
    js = figure(c, sp["x"], G, sp["p"], s=S, facing=sp["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo)
    stamp(c, t)
    c.restore()
    heads = {"h": to_screen(jh["head"]), "s": to_screen(js["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "IDEA HOARDER", GREY, size=28, a=na)
        chip(c, 720, 720, "SHIPPER", AMBER, size=28, a=na)
    vignette(c, 0.3)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    d = 1 + int(29 * seg(t, LAPSE0, LAPSE1))
    chip(c, 470, 640, f"DAY {d}" + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=34 + 16 * lapse)
    n = ideas(t)
    tear = 1 - seg(t, 8.5, 8.75) if 8.5 <= t else 0
    chip(c, 250, 545, f"IDEAS {n} · DONE 0", GREY, size=34, pop=1 + 0.25 * tear)
    k = seg(t, TURN, TURN + 0.25)
    chip(c, 715, 545, f"IDEAS 1 · DONE {1 if t >= TURN else 0}", AMBER, size=34, pop=1 + 0.3 * (1 - k) * (t > TURN))
    for ts, who, txt in TALK:
        if ts < t < ts + 1.35:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.15, ts + 1.35))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 220 if who == "h" else hx_ - 220, 300, 600)
            bubble(c, bx_, 722, txt, a, "speech", tail=(hx_ + (40 if who == "h" else -40), hy_ - 50), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", min(s, 12.4), "pop-medium-in" if s < 2 or s > 11 else "pop-small-in", -8 if s < 2 or s > 11 else -13] for s in SLAPS]
    ev += [["sfx", LAPSE0, "riser-2s-soft", -12], ["sfx", LAPSE0, "data-countup-medium", -12]]
    ev += [["sfx", 0.1 + 0.6 * i, "data-tick", -16] for i in range(3)]
    ev += [["sfx", TURN, "tone-ding-high", -6], ["thud", TURN + 0.2], ["summit", TURN + 0.2],
           ["slide", 8.2], ["sfx", 8.3, "whoosh-fast-medium", -10], ["text", END_T0]]
    return ev


if __name__ == "__main__":
    main("Folge25_Shipper_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep25_v2",
         [0.0, 0.3, 1.3, 3.5, 5.5, 6.6, 7.8, 8.5, 10.0, 11.5, 12.1, 12.45])
