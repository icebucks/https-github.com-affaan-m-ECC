"""Episode 19 (TikTok: Part 16): LONE WOLF vs TEAM PLAYER – promised by the Part 15 cliffhanger ("the one who won't ask for help").
One grassy hill at golden hour, a flag on the summit. Two boulders, one on each slope.
Lone Wolf (left) pushes alone – "I don't need help." – and is rolled back down twice.
Team Player (right) stops, calls two friends; they throw a rope from the summit and the boulder goes up. He ends at the bottom."""
import sys, math
import numpy as np
import lib
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 16                     # TikTok part number (internal episode 19)
G = 1250                       # ground at the foot of the hill
CX = 470                       # summit centre (left of 540: keeps the right pusher out of TikTok's button column)
PLAT = 75                      # half width of the summit plateau
SLW = 190                      # horizontal length of each slope
RISE = 150
XL0, XR0 = CX - PLAT - SLW, CX + PLAT + SLW   # feet of the two slopes
K = RISE / SLW
A = math.atan(K)
TOP = G - RISE
S = 0.9
R = 54                         # boulder radius
LEG = 84 * S
HH = 0.70 * LEG                # hip height above the ground at the hip while pushing
SC = 1.05
MID = 500                      # world x shown at the screen centre
TURN = 9.6                     # the team's boulder reaches the top
LW_BODY = (196, 202, 216)
TP_BODY = (255, 226, 178)
F_BODIES = [(255, 206, 160), (236, 214, 190)]
TALK = [(0.9, "l", "I don't need help."), (2.9, "t", "Can you guys help?"), (3.9, "f", "On our way!"),
        (6.3, "l", "I can do it alone!"), (TURN + 0.4, "t", "Made it. Together!"), (TURN + 1.9, "l", "Why is it so heavy?!")]
HOOK = "Pushed alone. Rolled back twice.\nWatch who reaches the top."
FOCUS = (300, 1150)
CTA = "Part 17 tomorrow:\nthe one who blames the oven"


def h(x):
    """ground height (y) of the hill"""
    if x <= XL0 or x >= XR0: return G
    if x < CX - PLAT: return G - K * (x - XL0)
    if x > CX + PLAT: return G - K * (XR0 - x)
    return TOP


# ------------------------------------------------------------------ boulders
def lw_u(t):
    """lone wolf: up, stuck, rolled back – twice"""
    if t < 0.6: return 0.2
    if t < 3.8: return lerp(0.2, 0.62, seg(t, 0.6, 3.8))
    if t < 4.6: return 0.62 + 0.012 * math.sin(t * 30) * seg(t, 3.8, 4.0)
    if t < 5.4: return lerp(0.62, 0.16, ((t - 4.6) / 0.8) ** 1.6)
    if t < 5.9: return 0.16
    if t < 8.6: return lerp(0.16, 0.58, seg(t, 5.9, 8.6))
    if t < 9.0: return 0.58 + 0.012 * math.sin(t * 30) * seg(t, 8.6, 8.75)
    if t < 9.8: return lerp(0.58, 0.14, ((t - 9.0) / 0.8) ** 1.6)
    return 0.14


def tp_u(t):
    """team player: a little alone, holds, then pulled up by the friends' rope (u > 1 = rolling onto the plateau)"""
    if t < 0.6: return 0.3
    if t < 2.6: return lerp(0.3, 0.42, seg(t, 0.6, 2.6))
    if t < 5.0: return 0.42
    if t < TURN: return lerp(0.42, 1.0, seg(t, 5.0, TURN))
    return 1.0 + 0.3 * seg(t, TURN, TURN + 0.6)


def centre(u, side):
    """boulder centre for slope position u (0 = foot, 1 = plateau edge); side -1 = left slope, +1 = right slope"""
    if side < 0:
        x = XL0 + min(u, 1) * SLW
        cx, cy = x - R * math.sin(A), h(x) - R * math.cos(A)
    else:
        x = XR0 - min(u, 1) * SLW
        cx, cy = x + R * math.sin(A), h(x) - R * math.cos(A)
    if u > 1:   # rolls onto the plateau
        k = (u - 1) / 0.3
        tx, ty = CX + PLAT - 30 if side > 0 else CX - PLAT + 30, TOP - R
        cx, cy = lerp(cx, tx, k), lerp(cy, ty, k)
    return cx, cy


def boulder(c, cx, cy, ang, col=(150, 140, 130)):
    shadow(c, cx, cy + R * 0.95, s=0.9, a=0.25, w=0.9)
    c.save(); c.translate(cx, cy); c.rotate(ang)
    p = skia.Path()
    for i in range(14):
        a = i / 14 * 2 * math.pi; r = R * (1 + 0.06 * math.sin(i * 2.3))
        (p.moveTo if i == 0 else p.lineTo)(r * math.cos(a), r * math.sin(a))
    p.close()
    c.drawPath(p, P(col)); c.drawPath(p, P(INK, stroke=5))
    c.drawCircle(-R * 0.25, -R * 0.3, R * 0.5, P((255, 255, 255), 0.10, blur=6))
    for (x0, y0, x1, y1) in ((-20, -10, 4, 6), (10, 18, 26, 4), (-12, 22, -4, 34)):   # cracks show the rolling
        c.drawLine(x0, y0, x1, y1, P(INK, 0.55, stroke=4))
    c.restore()


# ------------------------------------------------------------------ people
PUSH = dict(lean=46, head=-22, arm_f=70, elb_f=20, arm_b=60, elb_b=20)


def pusher(C, facing, t, moving, pose=None):
    """figure behind boulder C, pushing towards `facing`; hip solved so both hands reach the boulder"""
    p = dict(pose or PUSH)
    J = pose_points(p, S, facing)
    lo, hi = R, R + 160
    for _ in range(26):     # hip distance so the shoulder is R + 0.72 arm from the centre
        D = (lo + hi) / 2
        hx = C[0] - facing * D; hy = hip_y(hx, facing)
        sx, sy = hx + J["sh"][0], hy + J["sh"][1]
        if math.hypot(sx - C[0], sy - C[1]) > R + 0.72 * 76 * S: hi = D
        else: lo = D
    d = math.atan2(sy - C[1], sx - C[0])
    reach = {"f": (C[0] + R * math.cos(d - 0.22), C[1] + R * math.sin(d - 0.22)),
             "b": (C[0] + R * math.cos(d + 0.22), C[1] + R * math.sin(d + 0.22))}
    ph = t * 7 if moving else 0.0
    plant = {}
    for side, q in (("f", ph), ("b", ph + math.pi)):
        fx = hx + facing * (FOOT0 + FOOTA * math.sin(q)) * S
        lift = 7 * max(0.0, math.cos(q)) if moving else 0.0
        plant[side] = (fx, h(fx) - lift)
    return dict(x=hx, y=hy, p=p, f=facing, mode="hip", reach=reach, plant=plant)


FOOT0, FOOTA = -2, 16         # feet: from 18 behind to 14 in front of the hip (x S)


def hip_y(hx, facing):
    """hip as high as possible (0.84 leg) while the rearmost foot can still reach the ground behind"""
    y = h(hx) - 0.84 * LEG
    for dx in (FOOT0 - FOOTA, FOOT0 + FOOTA):
        fx = hx + facing * dx * S
        y = max(y, h(fx) - 6 * S - math.sqrt(max(1.0, (0.95 * LEG) ** 2 - (dx * S) ** 2)))
    return y


def stand_on_slope(x, facing, p):
    """hip-mode figure standing on the hill with both feet planted"""
    hy = h(x) - LEG * 0.93
    plant = {"f": (x + facing * 9 * S, h(x + facing * 9 * S)), "b": (x - facing * 9 * S, h(x - facing * 9 * S))}
    return dict(x=x, y=hy, p=p, f=facing, mode="hip", plant=plant)


def hands_of(fig, pose):
    """world hand points of `pose` for a figure dict (to blend reach targets into a free pose without a snap)"""
    J = pose_points(pose, S, fig["f"])
    return {"f": (fig["x"] + J["hand_f"][0], fig["y"] + J["hand_f"][1]), "b": (fig["x"] + J["hand_b"][0], fig["y"] + J["hand_b"][1])}


def blend_reach(fig, pose, k):
    """k = 0: hands on the reach targets, k = 1: hands where `pose` puts them"""
    if k <= 0: return fig
    free = hands_of(fig, pose)
    fig = dict(fig); fig["p"] = pose
    fig["reach"] = None if k >= 1 else {s: (lerp(fig["reach"][s][0], free[s][0], k), lerp(fig["reach"][s][1], free[s][1], k)) for s in ("f", "b")}
    return fig


def lone_wolf(t):
    C = centre(lw_u(t), -1)
    moving = (0.6 < t < 3.8) or (5.9 < t < 8.6)
    sliding = (4.6 < t < 5.4) or (9.0 < t < 9.8)
    p = dict(PUSH)
    if sliding: p.update(lean=10, head=-20)                         # pushed back, upright, heels dragging
    elif t > 9.8: p.update(lean=44, head=26)                         # exhausted, head down on the rock
    fig = pusher(C, 1, t, moving, p)
    if t > TURN + 1.6: fig = dict(fig, p=dict(fig["p"], head=-24))   # looks up at the summit
    return fig, C


def team_player(t):
    u = tp_u(t)
    C = centre(u, 1)
    moving = (0.6 < t < 2.6) or (5.0 < t < TURN)
    fig = pusher(C, -1, t, moving)
    if 2.7 < t < 3.9: fig["p"] = dict(fig["p"], head=-26)            # calls up to the summit
    if t > TURN:   # lets go and cheers where she stands: body, hip, feet and hands all blend together
        hold = pusher(centre(1.0, 1), -1, t, False)
        k = seg(t, TURN + 0.1, TURN + 0.7)
        pose = mix(hold["p"], cheer(t), k)
        st = stand_on_slope(hold["x"], -1, pose)
        fig = dict(st, y=lerp(hold["y"], st["y"], k ** 1.5),
                   plant={s_: (lerp(hold["plant"][s_][0], st["plant"][s_][0], k), lerp(hold["plant"][s_][1], st["plant"][s_][1], k)) for s_ in ("f", "b")})
        free = hands_of(fig, pose)
        fig["reach"] = None if k >= 1 else {s_: (lerp(hold["reach"][s_][0], free[s_][0], k), lerp(hold["reach"][s_][1], free[s_][1], k)) for s_ in ("f", "b")}
    return fig, C


def friends(t):
    """two friends walk up behind the summit, throw a rope and pull hand over hand"""
    C = centre(tp_u(t), 1)
    k = seg(t, 5.0, TURN + 0.6)
    start = (CX + 50, CX - 20); end = (CX - 25, CX - 95)
    out = []
    for i in range(2):
        a = seg(t, 3.3 + 0.2 * i, 3.7 + 0.2 * i)
        if t < 4.4:   # walk in
            x = lerp(CX - 150 - 40 * i, start[i], seg(t, 3.3 + 0.2 * i, 4.3))
            p = walk(t * 8, lean=4) if t < 4.3 else stand()
            out.append(dict(x=x, y=h(x), p=p, f=1, a=a, reach=None))
            continue
        x = lerp(start[i], end[i], k)
        pulling = 5.0 < t < TURN
        ph = t * 6 + i
        p = dict(lean=-10, head=10, leg_f=22, leg_b=-14, knee_f=12, knee_b=8)
        if pulling: p.update(walk(-ph, lean=-8, stride=12, arm=0)); p.update(lean=-10 + 2 * math.sin(ph), head=10)
        out.append(dict(x=x, y=h(x), p=p, f=1, a=1.0, reach="rope"))
    return out, C


def shoulder(f):
    """world shoulder of a feet-mode friend"""
    J = pose_points(f["p"], S, f["f"])
    low = max(J["foot_f"][1], J["foot_b"][1]); hy = f["y"] - low - 6 * S
    return f["x"] + J["sh"][0], hy + J["sh"][1]


def rope_line(fr, C, t):
    """rope polyline: boulder → front friend's grip → back friend's grip → slack tail on the ground.
    returns (points, grips, grow 0..1); after the summit the rope drops to the ground"""
    grips = []
    for f in fr:
        sh = shoulder(f); grips.append((sh[0] + 30 * S, sh[1] + 46 * S))
    d = math.atan2(grips[0][1] - C[1], grips[0][0] - C[0])
    att = (C[0] + R * math.cos(d), C[1] + R * math.sin(d))
    tx = fr[1]["x"] - 46
    pts = [att, grips[0], grips[1], (tx, h(tx) - 2)]
    k = seg(t, TURN + 1.1, TURN + 1.5)
    if k > 0: pts = [pts[0]] + [(x, lerp(y, h(x) - 3, k)) for x, y in pts[1:]]
    return pts, grips, seg(t, 4.4, 4.9)


def toward(a, b, d):
    l = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    return (a[0] + (b[0] - a[0]) * d / l, a[1] + (b[1] - a[1]) * d / l)


# ------------------------------------------------------------------ world
def world(c, t):
    u = seg(t, 0, T_END)
    sky(c, t, lerpc((90, 120, 190), (110, 110, 180), u), (255, 196, 150), (255, 222, 170), 1100)
    sun(c, CX + 20, 860 - 30 * u, 0.85, r=70)
    hills(c, 1110, (150, 140, 170), amp=30, off=0.4, a=0.85, height=110)
    hills(c, G + 4, (120, 140, 120), amp=26, off=2.0, a=1.0, height=150)   # covers the bright horizon band (audit: gold edge under the buttons)
    ground(c, G, (110, 150, 90), (70, 105, 70), (60, 90, 60))
    # the hill
    hp = poly([(XL0 - 60, G + 2), (XL0, G), (CX - PLAT, TOP), (CX + PLAT, TOP), (XR0, G), (XR0 + 60, G + 2)])
    c.drawPath(hp, P((126, 164, 96))); c.drawPath(poly([(XL0, G), (CX - PLAT, TOP), (CX + PLAT, TOP), (XR0, G)], close=False), P((80, 110, 70), stroke=5))
    c.drawPath(poly([(CX - PLAT + 10, TOP + 6), (CX + PLAT - 10, TOP + 6), (CX + 40, TOP + 60), (CX - 50, TOP + 70)]), P((150, 186, 110), 0.5))
    tufts(c, G, (70, 110, 60), seed=5, n=30, a=0.7)
    # flag
    fx = CX - PLAT + 14
    c.drawLine(fx, TOP, fx, TOP - 200, P(INK, stroke=7)); c.drawLine(fx, TOP, fx, TOP - 200, P((230, 220, 200), stroke=3))
    wv = math.sin(t * 4)
    c.drawPath(poly([(fx, TOP - 200), (fx + 90, TOP - 182 + 6 * wv), (fx, TOP - 150)]), P(AMBER))
    c.drawPath(poly([(fx, TOP - 200), (fx + 90, TOP - 182 + 6 * wv), (fx, TOP - 150)]), P(INK, stroke=4))
    if t > TURN:   # summit burst
        b = seg(t, TURN, TURN + 0.4) * (1 - seg(t, TURN + 1.2, TURN + 2.0))
        for i in range(10):
            a_ = i / 10 * 2 * math.pi + 0.3
            c.drawLine(fx + 120 * math.cos(a_) * 0.6, TOP - 120 + 120 * math.sin(a_) * 0.6, fx + 150 * math.cos(a_), TOP - 120 + 150 * math.sin(a_), P((255, 226, 150), 0.8 * b, stroke=5))
    return u


def frame(c, t):
    sway = 1 + 0.015 * math.sin(t * 0.9) + 0.06 * seg(t, 13.6, T_END)
    c.save(); c.translate(540 + 6 * math.sin(t * 0.6), G); c.scale(SC * sway, SC * sway); c.translate(-MID, -G)
    world(c, t)
    lo = (-1, -0.6)
    heads = {}
    # boulders
    lw, CL = lone_wolf(t)
    tp, CT = team_player(t)
    boulder(c, *CL, math.degrees(lw_u(t) * SLW / R) * 1.0)
    boulder(c, *CT, -math.degrees(tp_u(t) * SLW / R) * 1.0, col=(156, 146, 132))
    # friends + rope (behind the boulder plane)
    fr, _ = friends(t)
    pts, grips, grow = rope_line(fr, CT, t) if t >= 4.4 else (None, None, 0)
    if grow > 0:   # thrown from the front friend's hands down to the rock
        g0 = pts[1]
        end = (lerp(g0[0], pts[0][0], grow), lerp(g0[1], pts[0][1], grow))
        rp = skia.Path(); rp.moveTo(*pts[3]); rp.lineTo(*pts[2]); rp.lineTo(*pts[1]); rp.lineTo(*end)
        c.drawPath(rp, P(INK, stroke=8)); c.drawPath(rp, P((214, 180, 120), stroke=4))
    for i, f in enumerate(fr):
        reach = None
        if f["reach"] == "rope":
            g = pts[1 + i]; prev = pts[i]
            hold = {"f": toward(g, prev, 15 * S), "b": g}
            free = None
            k = seg(t, 4.4, 4.75)                                         # hands go from the sides to the rope
            if k < 1:
                J = pose_points(f["p"], S, 1)
                low = max(J["foot_f"][1], J["foot_b"][1]); hy = f["y"] - low - 6 * S
                free = {s: (f["x"] + J[f"hand_{s}"][0], hy + J[f"hand_{s}"][1]) for s in ("f", "b")}
                hold = {s: (lerp(free[s][0], hold[s][0], k), lerp(free[s][1], hold[s][1], k)) for s in ("f", "b")}
            reach = hold
            if t > TURN + 0.6:                                             # let go and cheer
                kk = seg(t, TURN + 0.6, TURN + 1.1)
                if kk > 0: f = dict(f, p=mix(f["p"], cheer(t), kk))
                J = pose_points(f["p"], S, 1)
                low = max(J["foot_f"][1], J["foot_b"][1]); hy = f["y"] - low - 6 * S
                ch = {s: (f["x"] + J[f"hand_{s}"][0], hy + J[f"hand_{s}"][1]) for s in ("f", "b")}
                reach = {s: (lerp(hold[s][0], ch[s][0], kk), lerp(hold[s][1], ch[s][1], kk)) for s in ("f", "b")} if kk < 1 else None
        c.saveLayerAlpha(None, int(255 * f["a"]))
        j = figure(c, f["x"], f["y"], f["p"], s=S, facing=f["f"], body=F_BODIES[i], rim=((255, 220, 170), 0.6), light=lo, reach=reach)
        c.restore()
        if i == 0: heads["f"] = j["head"]
    # the two pushers
    jl = figure(c, lw["x"], lw["y"], lw["p"], s=S, facing=lw["f"], body=LW_BODY, rim=((210, 220, 255), 0.5), light=lo,
                mode="hip", reach=lw.get("reach"), plant=lw.get("plant"))
    jt = figure(c, tp["x"], tp["y"], tp["p"], s=S, facing=tp["f"], body=TP_BODY, rim=((255, 220, 170), 0.6), light=lo,
                mode="hip", reach=tp.get("reach"), plant=tp.get("plant"))
    heads["l"], heads["t"] = jl["head"], jt["head"]
    plate_label(c, "LONE WOLF", clamp(heads["l"][0], 170, 760), heads["l"][1] - 62, GREY, 0.9)
    plate_label(c, "TEAM PLAYER", clamp(heads["t"][0], 170, 705), heads["t"][1] - 62, AMBER, 0.95)
    for ts, who, txt in TALK:
        if ts < t < ts + 1.7:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.4, ts + 1.7))
            hd = heads[who]
            bx = clamp(hd[0] + (60 if who == "l" else -40), 290, 640)
            bubble(c, bx, hd[1] - 150, txt, a, "speech", tail=(hd[0], hd[1] - 44), size=30, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    vignette(c, 0.32)
    grain(c, t, 0.03)
    end_text(c, t, 13.6, "He pushed alone. Twice.", "She asked once.", "Asking for help is strength.", y=1430)


def events():
    ev = []
    for ts, _, _ in TALK: ev.append(["pop", ts])
    ev += [["slip", 4.6], ["slide", 4.7], ["thud", 5.4], ["slip", 9.0], ["slide", 9.1], ["thud", 9.8],
           ["rope", 4.4], ["land", TURN], ["summit", TURN + 0.3], ["text", 13.6], ["text2", 14.4]]
    return ev


def overlay(c, t):
    series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 0.9, 2.2, 3.4, 4.3, 5.1, 6.4, 8.0, 9.3, 10.2, 11.6, 14.4, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore(); overlay(c, t)
        stills(opening, ts, "check/ep19")
    elif cmd == "full":   # full-resolution scene crops for close inspection
        from PIL import Image
        ims = []
        for tt in [float(a) for a in sys.argv[2:]]:
            lib.NOW = tt + OFF
            surf = skia.Surface(W, H); c = surf.getCanvas(); frame(c, tt + OFF); overlay(c, tt)
            ims.append(Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]).crop((0, 760, 1080, 1460)))
        sh = Image.new("RGB", (1080, 700 * len(ims)))
        for i, im in enumerate(ims): sh.paste(im, (0, 700 * i))
        sh.save("check/ep19_full.jpg", quality=85)
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs[:40]))
    else:
        finish_v2("Folge19_LoneWolf", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
