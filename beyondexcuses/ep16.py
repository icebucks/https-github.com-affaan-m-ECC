"""Episode 16 (TikTok: Part 13): FEAR OF FAILURE vs COURAGE – promised by the Part 12 cliffhanger ("the one who never jumps").
Outdoor pool with two 10 m diving towers, bright midday summer light: turquoise water, sparkles, palms (new place + light).
Both stand at the edge and look down. The fearful one says "Nope", walks back to the ladder and climbs all the way down
(hands and feet on the rungs, IK as in ep11). The courageous one is scared too – and jumps. She comes up laughing."""
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 13                     # TikTok part number (internal episode 16)
G = 1240                       # pool deck
WATER = G + 26                 # water surface
SC = 1.4
DY = 60
S = 1.0
TURN = 9.8                     # she jumps
TOP = G - 285                  # platform height (10 m board)
LAD = 300                      # ladder on the left side of the fearful one's tower
P_EDGE, A0, A_EDGE = 448, 528, 640       # his platform runs LAD..P_EDGE, hers A0..A_EDGE
RUNG0, RUNG = G - 30, 46
def rung_y(k): return RUNG0 - RUNG * k
C_TOP = (G - TOP - 30) / RUNG
TALK = [(2.8, "fear", "That's... 10 meters."), (5.0, "brave", "Scared. Jumping anyway."), (6.6, "fear", "Nope. Next summer."),
        (TURN + 2.1, "brave", "Again! AGAIN!")]
F_BODY = (196, 202, 216)
B_BODY = (255, 226, 178)
HOOK = "10 meters up. Then back down.\nWatch who actually jumps."
FOCUS = (420, 820)
CTA = "Part 14 tomorrow:\nthe one who keeps looking sideways"
SPLASH = TURN + 0.95
SWIM_X = 732


def limb_rung(c, off):
    q = c + off; n = math.floor(q); fr = q - n
    return n + ease(clamp((fr - 0.7) / 0.3))


def climbing(c):
    reach = {"f": (LAD + 8, rung_y(limb_rung(c, 0.0) + 3) + 2), "b": (LAD + 2, rung_y(limb_rung(c, 0.5) + 2.5) + 2)}
    kf, kb = limb_rung(c, 0.5), limb_rung(c, 0.0)
    plant = {"f": (LAD + 6, rung_y(kf) if kf >= 0 else G), "b": (LAD + 0, rung_y(kb) if kb >= 0 else G)}
    p = dict(lean=-4, head=-18, leg_f=20, leg_b=10, knee_f=40, knee_b=30)
    return dict(x=LAD - 24, y=rung_y(c) + 40, p=p, f=1, mode="hip", reach=reach, plant=plant)


# ------------------------------------------------------------------ characters
def fear(t):
    if t < 0.6:
        return dict(x=372, y=TOP, p=dict(stand(), head=-4), f=1)
    if t < 2.4:
        x = lerp(372, P_EDGE - 22, seg(t, 0.6, 2.4))
        return dict(x=x, y=TOP, p=walk(t * 6, lean=-2, stride=14, arm=14) if t < 2.3 else stand(), f=1)
    if t < 6.8:                                            # looks down, knees shaking, arms tight
        sh = 3 * math.sin(t * 38) * seg(t, 3.2, 3.6)
        p = dict(arms_crossed(head=24), lean=-6, leg_f=6 + sh, leg_b=-6 - sh, knee_f=10 + abs(sh), knee_b=10 + abs(sh))
        if t > 6.3: p = mix(p, dict(stand(), head=0), seg(t, 6.3, 6.8))
        return dict(x=P_EDGE - 22, y=TOP, p=p, f=1)
    if t < 7.2:                                            # turns around
        return dict(x=P_EDGE - 22, y=TOP, p=stand(), f=1 - 2 * seg(t, 6.8, 7.2))
    if t < 8.4:                                            # walks back to the ladder
        x = lerp(P_EDGE - 22, LAD + 14, seg(t, 7.2, 8.4))
        return dict(x=x, y=TOP, p=walk(t * 7, lean=4, stride=16, arm=16), f=-1)
    if t < 8.8:                                            # turns to face the ladder and grabs it
        return dict(x=LAD + 14, y=TOP, p=dict(stand(), head=-6), f=-1 + 2 * seg(t, 8.4, 8.8),
                    reach={"f": (LAD + 8, rung_y(C_TOP + 3) + 2), "b": (LAD + 2, rung_y(C_TOP + 2.5) + 2)} if t > 8.6 else None)
    if t < 11.4:                                           # climbs all the way down
        return climbing(C_TOP * (1 - seg(t, 8.8, 11.4)))
    k = seg(t, 11.4, 11.9)                                 # at the bottom: steps back, looks over at the pool
    x = lerp(LAD - 24, LAD - 30, k)
    return dict(x=x, y=G, p=mix(stand(), arms_crossed(head=6), seg(t, 11.9, 12.4)), f=1)


def brave(t):
    if t < 0.6:
        return dict(x=560, y=TOP, p=dict(stand(), head=-4), f=1)
    if t < 2.0:
        x = lerp(560, A_EDGE - 20, seg(t, 0.6, 2.0))
        return dict(x=x, y=TOP, p=walk(t * 7, lean=4) if t < 1.9 else stand(), f=1)
    if t < TURN - 0.6:                                     # looks down too – scared, breathes
        br = math.sin(t * 2.2)
        return dict(x=A_EDGE - 20, y=TOP, p=dict(stand(), head=22 - 18 * seg(t, 5.4, 6.0), lean=2 + br, arm_f=10, arm_b=-10), f=1)
    if t < TURN:                                           # crouches, arms swing back
        return dict(x=A_EDGE - 20, y=TOP, p=mix(stand(), dict(crouch(), arm_f=-40, arm_b=-50), seg(t, TURN - 0.6, TURN)), f=1)
    if t < SPLASH:                                         # the jump: pencil dive into the pool
        k = (t - TURN) / (SPLASH - TURN)
        x = lerp(A_EDGE - 20, SWIM_X, k)
        y = TOP - 90 * math.sin(math.pi * min(1, k * 1.6)) * (1 - k) + (WATER + 60 - TOP) * k ** 2
        p = mix(airborne(), dict(stand(), arm_f=170, elb_f=8, arm_b=-172, elb_b=8, leg_f=4, leg_b=-4), seg(t, TURN + 0.3, SPLASH))
        return dict(x=x, y=y, p=p, f=1)
    if t < TURN + 1.6:                                     # under water
        return dict(x=SWIM_X, y=WATER + 200, p=stand(), f=1, under=True)
    up = seg(t, TURN + 1.6, TURN + 2.0)                   # comes up laughing, arms in the air
    return dict(x=SWIM_X, y=WATER + lerp(200, 96, up), p=cheer(t), f=1 - 2 * seg(t, TURN + 2.6, TURN + 3.0), swim=True)


# ------------------------------------------------------------------ world
def palm(c, x, y, sc, col, t):
    c.drawPath(poly([(x - 6 * sc, y), (x + 6 * sc, y), (x + 14 * sc, y - 220 * sc), (x + 4 * sc, y - 220 * sc)]), P((120, 90, 60)))
    for k in range(6):
        a = math.radians(-160 + k * 28 + 4 * math.sin(t * 1.5 + k))
        tx, ty = x + 9 * sc + 110 * sc * math.cos(a), y - 220 * sc + 70 * sc * math.sin(a) + 30 * sc
        c.drawPath(poly([(x + 9 * sc, y - 222 * sc), (tx, ty), (x + 9 * sc + 30 * sc * math.cos(a), y - 214 * sc)]), P(col))


def tower(c, x0, x1, pillar, sign):
    c.drawRect(skia.Rect.MakeLTRB(pillar[0], TOP + 14, pillar[1], G + 4), P((210, 214, 222)))
    c.drawRect(skia.Rect.MakeLTRB(pillar[0], TOP + 14, pillar[0] + 10, G + 4), P((170, 176, 190)))
    r = skia.Rect.MakeLTRB(x0, TOP, x1, TOP + 18)
    c.drawRect(r, P((236, 238, 244))); c.drawRect(r, P(INK, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(x0, TOP - 34, x0 + 6, TOP), P((150, 155, 168)))       # back railing post
    plate = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((pillar[0] + pillar[1]) / 2 - 34, TOP + 60, 68, 40), 6, 6)
    c.drawRRect(plate, P((30, 90, 160))); label(c, sign, (pillar[0] + pillar[1]) / 2, TOP + 89, (255, 255, 255), 1.0)


def world(c, t):
    sky(c, t, (40, 120, 210), (110, 190, 245), (200, 236, 255), 1000)
    c.drawCircle(760, 640, 210, P((255, 250, 220), 0.35, blur=70)); c.drawCircle(760, 640, 64, P((255, 252, 236), 0.95))
    # apartment blocks + palms behind the pool
    for i, (x, w, h) in enumerate(((60, 160, 300), (260, 120, 220), (840, 180, 340))):
        c.drawRect(skia.Rect.MakeLTRB(x, G - h - 40, x + w, G), P((222, 196, 180) if i % 2 else (188, 204, 222)))   # not near-white: TikTok-button zone
        for wy in range(int(G - h), int(G - 60), 46):
            for wx in range(int(x + 16), int(x + w - 24), 34): c.drawRect(skia.Rect.MakeXYWH(wx, wy, 18, 24), P((120, 160, 200), 0.6))
    for i, (x, sc) in enumerate(((150, 1.0), (420, 0.8), (900, 1.15))): palm(c, x, G - 30, sc, (60, 150, 90), t)
    # deck and pool
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 30, W + 300, H + 300), P((236, 228, 210)))
    c.drawLine(-300, G - 30, W + 300, G - 30, P(INK, stroke=4))
    pool = skia.Rect.MakeLTRB(462, WATER, W + 300, H + 300)
    sh = skia.GradientShader.MakeLinear([(0, WATER), (0, WATER + 300)], [C((60, 200, 225)), C((20, 120, 190))], [0, 1])
    c.drawRect(pool, skia.Paint(Shader=sh))
    c.drawLine(462, WATER, W + 300, WATER, P((230, 250, 255), stroke=5))
    for k in range(26):                                    # caustic sparkles drifting on the surface
        rng = np.random.default_rng(k)
        x = 470 + (rng.uniform(0, 300) + t * rng.uniform(10, 30)) % 300          # left half only (right half = TikTok buttons)
        y = WATER + 14 + rng.uniform(0, 200)
        c.drawLine(x, y, x + 26, y + 2 * math.sin(t * 3 + k), P((230, 255, 255), 0.45 + 0.3 * math.sin(t * 4 + k), stroke=3))
    for y in (WATER + 80, WATER + 170):                   # lane ropes
        for x in range(480, 1100, 26): c.drawCircle(x, y + 3 * math.sin(t * 2 + x * 0.05), 6, P((220, 60, 60) if (x // 26) % 3 else (40, 90, 200)))
    c.drawRect(skia.Rect.MakeLTRB(LAD - 10, TOP - 30, LAD + 14, G), P((0, 0, 0), 0))
    tower(c, LAD, P_EDGE, (LAD + 8, LAD + 80), "10 M")
    tower(c, A0, A_EDGE, (A0, A0 + 66), "10 M")
    # ladder on his tower
    for xx in (LAD - 2, LAD + 12): c.drawLine(xx, TOP - 40, xx, G - 30, P((150, 155, 168), stroke=6))
    k = 0
    while rung_y(k) > TOP - 20:
        c.drawLine(LAD - 4, rung_y(k), LAD + 14, rung_y(k), P((150, 155, 168), stroke=5)); k += 1


def frame(c, t):
    sway = 1 + 0.018 * math.sin(t * 0.9) + 0.06 * seg(t, 13.6, T_END)
    c.save(); c.translate(540 + 10 * math.sin(t * 0.6), G + DY); c.scale(SC * sway, SC * sway); c.translate(-540, -G)
    world(c, t)
    lo = (-0.6, -1)
    fe = smooth(fear, t)
    if fe.get("mode") != "hip": shadow(c, fe["x"], fe["y"] + 2, S, 0.25)
    jf = figure(c, fe["x"], fe["y"] - (84 * S + 6 if fe.get("mode") == "hip" else 0), fe["p"], s=S, facing=fe["f"], body=F_BODY, rim=((200, 230, 255), 0.5), light=lo,
                mode=fe.get("mode", "feet"), reach=fe.get("reach"), plant=fe.get("plant"))
    br = brave(t)                                          # not smoothed through the dive: the jump is ballistic
    if not br.get("under"):
        if br.get("swim") or t > SPLASH - 0.25:
            c.save(); c.clipRect(skia.Rect.MakeLTRB(-300, -500, W + 300, WATER + 2))
        if t < TURN: shadow(c, br["x"], br["y"] + 2, S, 0.25)
        jb = figure(c, br["x"], br["y"], br["p"], s=S, facing=br["f"], body=B_BODY, rim=((255, 240, 200), 0.6), light=lo)
        if br.get("swim") or t > SPLASH - 0.25:
            c.restore()
        if br.get("swim"):
            for r in range(3):                             # ripples round her
                rr = 40 + ((t * 40 + r * 25) % 75)
                c.drawOval(skia.Rect.MakeXYWH(br["x"] - rr, WATER - rr * 0.18, 2 * rr, rr * 0.36), P((240, 255, 255), 0.6 * (1 - (rr - 40) / 75), stroke=3))
    else:
        jb = {"head": (SWIM_X, WATER - 40)}
    # splash
    if SPLASH <= t < SPLASH + 1.2:
        k = (t - SPLASH) / 1.2
        rng = np.random.default_rng(3)
        for i in range(30):
            a = rng.uniform(-2.7, -0.4); v = rng.uniform(150, 420)
            px = SWIM_X + math.cos(a) * v * k; py = WATER + math.sin(a) * v * k + 420 * k * k
            if py < WATER + 4: c.drawCircle(px, py, 7 * (1 - k) + 2, P((235, 252, 255), 0.9 * (1 - k)))
        c.drawOval(skia.Rect.MakeXYWH(SWIM_X - 90 * k - 20, WATER - 10, 180 * k + 40, 20), P((240, 255, 255), 0.8 * (1 - k), stroke=5))
    # labels
    plate_label(c, "FEAR", jf["head"][0], jf["head"][1] - 56, GREY, 0.9)
    if t < TURN - 0.1 or t > TURN + 2.0:
        plate_label(c, "COURAGE", jb["head"][0] - (40 if t > TURN else 0), jb["head"][1] - 56 - (10 if t > TURN else 0), AMBER, 0.95)
    for ts, who, txt in TALK:
        if ts < t < ts + 1.9:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.6, ts + 1.9))
            hd = jf["head"] if who == "fear" else jb["head"]
            bx = clamp(hd[0] + (40 if who == "fear" else -30), 300, 600)
            bubble(c, bx, hd[1] - 140, txt, a, "speech", tail=(hd[0], hd[1] - 60), size=30, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    vignette(c, 0.3)
    grain(c, t, 0.03)
    end_text(c, t, 13.6, "He walked back down.", "She jumped scared.", "Jump scared. Laugh after.", y=1430)


def events():
    ev = []
    for ts, _, _ in TALK: ev.append(["pop", ts])
    for k in range(4): ev.append(["step", 0.7 + k * 0.42, False])
    ev += [["jump", TURN], ["splash", SPLASH], ["summit", TURN + 1.7], ["sunrise", TURN + 1.6], ["text", 13.6], ["text2", 14.4]]
    return ev


def overlay(c, t):
    series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 0.6, 2.0, 3.4, 5.4, 7.6, 9.2, 9.9, 10.4, 11.0, 12.2, 13.0, 14.4, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore(); overlay(c, t)
        stills(opening, ts, "check/ep16")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs))
    else:
        finish_v2("Folge16_Courage", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
