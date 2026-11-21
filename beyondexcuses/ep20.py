"""Episode 20 (TikTok: Part 17): BLAMER vs LEARNER – promised by the Part 16 cliffhanger ("the one who blames the oven").
A kitchen in the evening, warm pendant lamps, smoke alarm blinking. Both cakes come out burnt.
Blamer (grey, left oven): "This oven is garbage!" – "The recipe is wrong." – "I'm just not a baker." – at the end: "Her oven is just better."
Learner (amber, right oven): checks the recipe card ("250°? It says 180°!"), turns the knob down, tries again (one hour later) and
pulls out a golden cake: "Second try. Perfect." """
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 17                     # TikTok part number (internal episode 20)
G = 1300                       # kitchen floor
S = 1.3
TURN = 10.0                    # golden cake comes out
B_BODY = (196, 202, 216)
L_BODY = (255, 226, 178)
OVEN_L = (170, 285)            # x range; front faces right (towards the blamer)
OVEN_R = (650, 765)            # front faces left (towards the learner)
TOP = G - 160                  # oven / counter top
BX, LX = 370, 595              # where the two stand
KNOB = (OVEN_R[0] + 22, G - 128)
MOUTH = (OVEN_R[0] - 8, G - 70)  # where a tray slides out of the right oven
SKIP0, SKIP1 = 5.6, 9.4        # "one hour later" time skip
TALK = [(0.9, "b", "This oven is garbage!"), (2.2, "l", "Hmm. What went wrong?"), (3.5, "l", "It says 180, not 250!"),
        (5.0, "b", "The recipe is wrong."), (7.3, "b", "I'm just not a baker."), (TURN + 0.9, "l", "Second try. Perfect."),
        (TURN + 2.3, "b", "Her oven is just better.")]
HOOK = "Both cakes burned.\nOnly one blamed the oven."
FOCUS = (540, 1180)
CAM = (465, G - 180, 1.3)    # world point at the screen centre (540, 1150), zoom
COVER = False                  # covers.py sets True: scene without speech bubbles
CTA = "Part 18 tomorrow:\nthe one who sits down at mile 20"


# ------------------------------------------------------------------ helpers
def hip_of(x, p, f):
    """world hip of a feet-mode figure standing on G"""
    J = pose_points(p, S, f)
    low = max(J["foot_f"][1], J["foot_b"][1])
    return x, G - low - 6 * S, J


def free_hands(x, p, f):
    hx, hy, J = hip_of(x, p, f)
    return {s: (hx + J[f"hand_{s}"][0], hy + J[f"hand_{s}"][1]) for s in ("f", "b")}


def blend(a, b, k):
    return {s: (lerp(a[s][0], b[s][0], k), lerp(a[s][1], b[s][1], k)) for s in a}


LEAN = dict(lean=14, head=6, arm_f=40, elb_f=20, arm_b=30, elb_b=20, leg_f=8, leg_b=-8)


# ------------------------------------------------------------------ characters
def blamer(t):
    """no props: points at the oven, shrugs, crosses arms, looks over at the end"""
    f = -1.0
    if t < 0.6:
        p = mix(stand(), dict(stand(), head=-10, lean=-4), seg(t, 0.0, 0.6))
    elif t < 2.4:                                                         # points at his oven
        p = mix(stand(), dict(offer(), arm_f=95, elb_f=6, head=-6, lean=-6), seg(t, 0.6, 0.9) * (1 - seg(t, 2.1, 2.4)))
    elif t < 4.6:
        p = stand()
    elif t < 6.6:                                                         # turns to the room, shrugs
        f = -1 + 2 * seg(t, 4.4, 4.9)
        p = mix(stand(), shrug(1.0), seg(t, 4.8, 5.1) * (1 - seg(t, 6.2, 6.6)))
    else:                                                                 # sulks with folded arms
        f = 1.0
        p = mix(stand(), dict(arms_crossed(-6), lean=-4), seg(t, 6.6, 7.0))
        if t > TURN + 0.4: p = dict(p, head=lerp(-6, -12, seg(t, TURN + 0.4, TURN + 0.8)))
    return dict(x=BX, p=p, f=f)


def learner_tray(t):
    """golden tray: inside the oven until TURN, then pulled out and held up"""
    if t < TURN + 0.35: return None
    k = seg(t, TURN + 0.35, TURN + 0.95)
    up = seg(t, TURN + 0.9, TURN + 1.5)
    x = lerp(MOUTH[0], LX + 58, k)
    y = lerp(MOUTH[1], G - 130, k)
    return (lerp(x, LX + 60, up), lerp(y, G - 215, up) + 4 * math.sin(t * 5) * up)


def learner(t):
    f = 1.0
    reach = None
    if t < 1.6:                                                           # waves the smoke away
        p = mix(stand(), dict(stand(), arm_f=120 + 25 * math.sin(t * 12), elb_f=30, head=-6), seg(t, 0.3, 0.6) * (1 - seg(t, 1.3, 1.6)))
    elif t < 4.6:                                                         # looks up at the recipe card, thinks
        p = mix(stand(), dict(think(t), head=-22), seg(t, 1.6, 2.0) * (1 - seg(t, 4.2, 4.6)))
    elif t < SKIP0:                                                       # turns the knob down
        base = dict(LEAN)
        k = seg(t, 4.6, 4.95) * (1 - seg(t, 5.3, 5.6))
        free = free_hands(LX, base, f)
        tw = 10 * seg(t, 4.95, 5.25)
        knob = (KNOB[0] - 4 + 0.15 * tw, KNOB[1] + 0.3 * tw)
        reach = {"f": (lerp(free["f"][0], knob[0], k), lerp(free["f"][1], knob[1], k)), "b": free["b"]}
        p = base
    elif t < TURN:                                                        # one hour later: waits, taps the foot
        p = mix(stand(), dict(hands_on_hips(), leg_f=6 + 5 * max(0, math.sin(t * 9)) * seg(t, SKIP1, SKIP1 + 0.2)), seg(t, SKIP0, SKIP0 + 0.3))
    else:                                                                 # pulls the golden cake out and holds it up
        crouch_k = seg(t, TURN, TURN + 0.25) * (1 - seg(t, TURN + 0.7, TURN + 1.1))
        p = mix(dict(LEAN), dict(crouch(), head=-8), crouch_k)
        tr_ = learner_tray(t)
        hold = {"f": (tr_[0] + 24, tr_[1] - 6), "b": (tr_[0] - 22, tr_[1] - 6)} if tr_ else None
        free = free_hands(LX, p, f)
        k = seg(t, TURN + 0.1, TURN + 0.35)
        if hold is None: hold = {"f": (MOUTH[0] + 24, MOUTH[1] - 6), "b": (MOUTH[0] - 22, MOUTH[1] - 6)}
        reach = blend(free, hold, k)
    return dict(x=LX, p=p, f=f, reach=reach)


# ------------------------------------------------------------------ world
def lamp(c, x, t, a=1.0):
    c.drawLine(x, 0, x, 380, P((40, 30, 30), stroke=4))
    c.drawPath(poly([(x - 60, 440), (x + 60, 440), (x + 34, 380), (x - 34, 380)]), P((60, 44, 40)))
    c.drawCircle(x, 452, 26, P((225, 150, 105), 0.95 * a))      # warm but below the audit's gold/white thresholds
    c.drawCircle(x, 460, 260, P((255, 190, 120), 0.16 * a, blur=90))


def oven(c, x0, x1, t, glow=0.0, door_open=0.0, label=None, needle=250):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, TOP, x1, G), 10, 10), P((200, 196, 190)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, TOP, x1, G), 10, 10), P(INK, stroke=5))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 6, TOP + 8, x1 - 6, TOP + 44), P((60, 60, 70)))            # control strip
    for k, kx in enumerate((x0 + 30, x0 + 65, x1 - 30)):
        c.drawCircle(kx, TOP + 26, 11, P((230, 230, 235))); c.drawCircle(kx, TOP + 26, 11, P(INK, stroke=3))
    w = skia.Rect.MakeLTRB(x0 + 16, TOP + 60, x1 - 16, G - 22)
    c.drawRRect(skia.RRect.MakeRectXY(w, 8, 8), P(lerpc((40, 34, 34), (255, 150, 60), glow)))
    c.drawRRect(skia.RRect.MakeRectXY(w, 8, 8), P(INK, stroke=4))
    if glow > 0: c.drawRect(w, P((255, 170, 80), 0.35 * glow, blur=20))
    c.drawLine(x0 + 24, TOP + 54, x1 - 24, TOP + 54, P((120, 120, 130), stroke=6))                 # handle


def smoke(c, x, y, t, a):
    if a <= 0: return
    rng = np.random.default_rng(int(x))
    for k in range(9):
        ph = (t * 0.6 + k / 9) % 1
        sx = x + 30 * math.sin(ph * 6 + k) + rng.uniform(-20, 20)
        c.drawCircle(sx, y - 260 * ph, 18 + 40 * ph, P((70, 66, 70), a * 0.55 * (1 - ph), blur=6))


def cake(c, x, y, burnt, a=1.0, w=96):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2 - 8, y - 6, w + 16, 12), 4, 4), P((150, 150, 160), a))
    col = (40, 30, 30) if burnt else (240, 176, 80)
    top = (24, 20, 20) if burnt else (255, 214, 130)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y - 38, w, 34), 10, 10), P(col, a))
    c.drawOval(skia.Rect.MakeXYWH(x - w / 2, y - 46, w, 18), P(top, a))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y - 46, w, 42), 10, 10), P(INK, a, stroke=4))
    if not burnt:
        c.drawCircle(x, y - 30, 70, P((255, 210, 120), 0.25 * a, blur=26))


def world(c, t):
    later = seg(t, SKIP0, SKIP0 + 0.6)
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, G)], [C((70, 50, 60)), C((120, 82, 70)), C((168, 116, 88))], [0, 0.55, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    # window: dusk -> night after the skip
    wx0, wy0, wx1, wy1 = 355, 800, 575, 990
    c.drawRect(skia.Rect.MakeLTRB(wx0, wy0, wx1, wy1), P(lerpc((240, 150, 110), (40, 44, 90), later)))
    for k in range(7):
        bx = wx0 + 10 + k * 34; bh = 40 + 30 * ((k * 37) % 5)
        c.drawRect(skia.Rect.MakeLTRB(bx, wy1 - bh, bx + 26, wy1), P(lerpc((110, 70, 80), (24, 26, 50), later)))
        if later > 0.5 and k % 2: c.drawRect(skia.Rect.MakeXYWH(bx + 8, wy1 - bh + 12, 6, 8), P((255, 220, 140), later))
    c.drawRect(skia.Rect.MakeLTRB(wx0, wy0, wx1, wy1), P((80, 56, 50), stroke=12))
    c.drawLine((wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1, P((80, 56, 50), stroke=8))
    # tiles + floor
    for yy in range(int(TOP) - 120, G, 40):
        c.drawLine(40, yy, 1040, yy, P((255, 255, 255), 0.05, stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(0, G, W, H), P((88, 60, 50)))
    for k in range(0, W, 90): c.drawLine(k, G, k - 60, H, P((60, 40, 34), 0.6, stroke=3))
    lamp(c, 250, t); lamp(c, 680, t)
    # wall clock: spins during the time skip
    cx, cy, r = 465, 690, 40
    c.drawCircle(cx, cy, r, P((240, 232, 220))); c.drawCircle(cx, cy, r, P(INK, stroke=5))
    ang = 2 * math.pi * (seg(t, SKIP0, SKIP1) * 1.0) - math.pi / 2
    c.drawLine(cx, cy, cx + 30 * math.cos(ang * 12), cy + 30 * math.sin(ang * 12), P(INK, stroke=4))
    c.drawLine(cx, cy, cx + 20 * math.cos(ang), cy + 20 * math.sin(ang), P(INK, stroke=6))
    # smoke alarm on the ceiling
    al = (t < 2.6) and (int(t * 4) % 2 == 0)
    c.drawOval(skia.Rect.MakeXYWH(435, 760, 60, 18), P((230, 230, 230))); c.drawOval(skia.Rect.MakeXYWH(435, 760, 60, 18), P(INK, stroke=3))
    if al: c.drawCircle(465, 778, 9, P((255, 60, 60))); c.drawCircle(465, 778, 40, P((255, 60, 60), 0.3, blur=14))
    # recipe card above the right oven
    c.save(); c.translate(694, G - 420); c.rotate(4)
    c.drawRect(skia.Rect.MakeXYWH(-64, -50, 128, 100), P((232, 214, 176))); c.drawRect(skia.Rect.MakeXYWH(-64, -50, 128, 100), P(INK, stroke=3))   # cream, not white: audit
    text(c, "CAKE", 0, -18, F_CAP, 28, (120, 60, 40), 1.0)
    text(c, "180°", 0, 30, F_CAP, 44, (200, 60, 40), 1.0)
    c.restore()
    # ovens
    oven(c, *OVEN_L, t, glow=0.5 * (1 - seg(t, 0.0, 2.0)))
    gl = seg(t, SKIP0 + 0.2, SKIP0 + 0.6) * (1 - seg(t, TURN + 0.1, TURN + 0.4))
    oven(c, *OVEN_R, t, glow=0.7 * gl + 0.5 * (1 - seg(t, 0.0, 2.0)))
    # knob needle on the right oven (250 -> 180)
    kk = seg(t, 4.95, 5.25)
    a = math.radians(-60 + 120 * (1 - kk) - 40)
    c.drawLine(KNOB[0], KNOB[1], KNOB[0] + 9 * math.cos(a), KNOB[1] + 9 * math.sin(a), P((200, 40, 40), stroke=3))
    # burnt cakes on top (right one goes away in the skip – she cleaned up)
    cake(c, 228, TOP, True)
    cake(c, 708, TOP, True, a=1 - later)
    smoke(c, 228, TOP - 40, t, 1 - seg(t, 4.0, 6.0) * 0.5)
    smoke(c, 708, TOP - 40, t, 1 - later)
    return later


def frame(c, t):
    sway = 1 + 0.015 * math.sin(t * 0.8) + 0.05 * seg(t, 13.6, T_END) + 0.05 * seg(t, TURN + 1.4, 13.6)
    c.save(); c.translate(540 + 6 * math.sin(t * 0.6), 1150); c.scale(CAM[2] * sway, CAM[2] * sway); c.translate(-CAM[0], -CAM[1])
    world(c, t)
    lo = (-1, -0.6)
    heads = {}
    b = blamer(t)
    jb = figure(c, b["x"], G, b["p"], s=S, facing=b["f"], body=B_BODY, rim=((210, 220, 255), 0.5), light=lo)
    heads["b"] = jb["head"]
    l = learner(t)
    tr_ = learner_tray(t)
    jl = figure(c, l["x"], G, l["p"], s=S, facing=l["f"], body=L_BODY, rim=((255, 220, 170), 0.6), light=lo, reach=l["reach"])
    heads["l"] = jl["head"]
    if tr_:                                                               # golden cake in her hands
        cake(c, tr_[0] + 8, tr_[1] + 16, False, w=90)
    if TURN + 1.4 < t < TURN + 2.4:                                       # sparkle around the golden cake
        k = seg(t, TURN + 1.4, TURN + 2.4)
        for i in range(10):
            ang = i / 10 * 2 * math.pi
            r_ = 60 + 90 * k
            c.drawCircle(tr_[0] + 8 + r_ * math.cos(ang), tr_[1] - 10 + r_ * math.sin(ang), 6 * (1 - k) + 1, P((255, 220, 120), 1 - k))
    plate_label(c, "BLAMER", heads["b"][0], heads["b"][1] - 80, GREY, 0.9)
    plate_label(c, "LEARNER", heads["l"][0], heads["l"][1] - 80, AMBER, 0.95)
    for ts, who, txt in ([] if COVER else TALK):
        if ts < t < ts + 1.6:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.3, ts + 1.6))
            hd = heads[who]
            bx = clamp(hd[0] + 40, 300, 510) if who == "b" else clamp(hd[0] - 150, 300, 440)   # learner bubbles stay left of the recipe card
            bubble(c, bx, hd[1] - 150, txt, a, "speech", tail=(hd[0], hd[1] - 50), size=30, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    vignette(c, 0.3)
    if SKIP0 - 0.1 < t < SKIP0 + 1.8:                                     # "one hour later" chip
        a = seg(t, SKIP0 - 0.1, SKIP0 + 0.2) * (1 - seg(t, SKIP0 + 1.4, SKIP0 + 1.8))
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(320, 610, 440, 64), 32, 32)
        c.drawRRect(rr, P((20, 20, 30), 0.85 * a)); c.drawRRect(rr, P(AMBER, a, stroke=3))
        text(c, "TRY #2 · 1 HOUR LATER", 540, 654, F_SANS, 30, AMBER, a)
    grain(c, t, 0.03)
    end_text(c, t, 13.6, "He blamed the oven.", "She read the recipe again.", "Every mistake is a lesson.", y=1430)


def events():
    ev = []
    for ts, _, _ in TALK: ev.append(["pop", ts])
    ev += [["thud", 0.4], ["slip", 4.9], ["sunrise", SKIP0], ["land", TURN], ["summit", TURN + 1.2], ["text", 13.6], ["text2", 14.4]]
    return ev


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 0.9, 2.2, 3.6, 4.9, 6.2, 7.6, 9.6, 10.4, 11.6, 12.8, 14.4, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore()
            series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)
        stills(opening, ts, "check/ep20")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs[:40]))
    else:
        finish_v2("Folge20_Learner", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
