"""Episode 11: VICTIM vs. OWNER – a leaking attic in a rainstorm, lit by one flickering bare bulb.
Two holes in the roof. Victim stands under his drip and blames the rain. Owner puts a bucket under hers,
climbs the ladder and nails a plank over the hole. Then the storm breaks and a sun shaft falls through the window –
Victim is still standing in his drip: "Must be luck." """
import sys, math
import numpy as np
from lib import *

T_END = 17.2
G = 1240                 # floor
SC = 1.4                 # scene zoom (pivot 540, G)
DY = 60                  # floor sits at screen y 1300
S = 1.0
TURN = 12.2
H1, H2 = 405, 640        # holes in the roof (Owner's / Victim's)
LAD = 340                # ladder x
TOP = G - 280            # ladder standing height (feet)
WIN = (470, 905, 120, 140)   # back window x, y, w, h
BULB = (530, 852)
HITS = [6.3 + 0.55 * k for k in range(6)]
PATCH = 5.9
VICTIM_TALK = [(0.9, "Not again…"), (3.9, "Why always me?"), (6.9, "It's the rain's fault."), (9.9, "Someone fix this!"),
               (TURN + 0.6, "Must be luck.")]

OWN_BODY = (255, 226, 178)
VIC_BODY = (196, 202, 216)


def roof_y(x): return 800 - 0.12 * x
def sunny(t): return seg(t, TURN - 0.9, TURN + 0.7)      # 0 storm … 1 sun
def water_lvl(t): return 6 + 24 * seg(t, 0.0, 11.0)


# ------------------------------------------------------------------ characters
# v2 poses (17.11.2026): elbows/knees only bend the right way, hands and feet grab the ladder rungs (IK),
# the owner turns around instead of flipping, the hammer is handed over hand to hand.
# The uploaded video (Folge11_Owner_EN.mp4) was rendered with the v1 poses (git history).
RUNG0, RUNG = G - 30, 46                     # lowest rung y, rung spacing
def rung_y(k): return RUNG0 - RUNG * k
C_TOP = (G - TOP - 30) / RUNG               # climbing progress (in rungs) when the feet stand at TOP


def carry_bucket(ph):
    p = walk(ph, lean=6)
    p.update(arm_f=8, elb_f=10)              # arm hangs straight down, holding the handle
    return p


def limb_rung(c, off):
    """rung index of a hand/foot while climbing: holds 70 % of the cycle, then moves up (or down) one rung"""
    q = c + off; n = math.floor(q); fr = q - n
    return n + ease(clamp((fr - 0.7) / 0.3))


def climbing(c, up=True):
    """owner on the ladder at climbing progress c (rungs): hip position, hand and foot targets"""
    hip_y = rung_y(c) - 84 * S - 6           # y returned = foot level (smooth() blends it with walking frames)
    reach = {"f": (LAD + 8, rung_y(limb_rung(c, 0.0) + 4) + 2), "b": (LAD + 2, rung_y(limb_rung(c, 0.5) + 3) + 2)}
    plant = {"f": (LAD + 6, rung_y(limb_rung(c, 0.25))), "b": (LAD + 0, rung_y(limb_rung(c, 0.75) - 1))}
    p = dict(lean=-4, head=-18, leg_f=20, leg_b=10, knee_f=40, knee_b=30)
    return dict(x=LAD - 18, y=rung_y(c), p=p, f=1, mode="hip", reach=reach, plant=plant)


def hammer_swing(t):
    """0 = wind-up (hammer behind the head) … 1 = strike on the nail"""
    k = 0.0
    for h in HITS:
        if h - 0.4 < t < h + 0.12: k = ease((t - (h - 0.4)) / 0.4) if t < h else 1 - (t - h) / 0.12
    return clamp(k)


def owner(t):
    if t < 1.4:                                  # carries the bucket to the drip
        x = lerp(190, 378, seg(t, 0.0, 1.4))
        return dict(x=x, y=G, p=carry_bucket(t * 8), f=1, bucket=True)
    if t < 2.0:                                  # sets it down under the drip
        k = seg(t, 1.4, 1.7) if t < 1.85 else 1 - seg(t, 1.85, 2.0)
        return dict(x=378, y=G, p=mix(stand(), dict(crouch(), arm_f=30, elb_f=20), k), f=1, bucket=t < 1.75)
    if t < 2.7:                                  # back to the ladder
        x = lerp(378, LAD + 6, seg(t, 2.0, 2.7))
        return dict(x=x, y=G, p=walk(t * 8, lean=6), f=-1)
    if t < 3.2:                                  # picks up the plank, turns to the ladder
        k = seg(t, 2.7, 2.95)
        f = -1 if t < 2.95 else lerp(-1, 1, seg(t, 2.95, 3.2))
        return dict(x=LAD + 6 - 24 * seg(t, 2.95, 3.2), y=G, p=mix(stand(), dict(stand(), lean=14, head=10), k), f=f,
                    reach={"b": (LAD - 40, G - 70 - 30 * seg(t, 2.95, 3.2))}, plank=t > 2.95)
    if t < 5.6:                                  # climbs, rung by rung
        o = climbing(C_TOP * seg(t, 3.2, 5.6))
        o["reach"]["b"] = (LAD + 14, o["y"] - 210)      # the plank hand stays up, carrying the plank
        return dict(o, plank=True)
    if t < 9.6:                                  # holds the plank to the hole and nails it
        o = climbing(C_TOP)
        o["reach"] = {"b": (H1 - 40, roof_y(H1) + 46)}
        if t > PATCH:
            k = hammer_swing(t)
            wind, strike = (LAD + 4, o["y"] - 240), (H1 - 30, roof_y(H1) + 52)
            o["reach"]["f"] = (lerp(wind[0], strike[0], k), lerp(wind[1], strike[1], k))
        else:
            o["reach"]["f"] = (H1 - 10, roof_y(H1) + 50)
        o["p"] = dict(o["p"], head=-28)
        return dict(o, hammer=t > PATCH, plank=t < PATCH)
    if t < 11.0:                                 # climbs down
        return dict(climbing(C_TOP * (1 - seg(t, 9.6, 11.0)), up=False))
    if t < TURN:                                 # steps off, looks up at the patch
        x = lerp(LAD, 470, seg(t, 11.0, 11.7))
        return dict(x=x, y=G, p=dict(stand(), head=-26, lean=-3) if t > 11.7 else walk(t * 8), f=1)
    if t < 14.7:                                 # jumps for joy in the sun
        ph = (t - TURN) / 0.62
        hop = max(0.0, math.sin(ph * math.pi)) if int(ph) % 2 == 0 else 0.0
        return dict(x=470, y=G - 46 * hop, p=cheer(t) if hop < 0.2 else dict(airborne(), arm_f=150, arm_b=-150), f=1)
    if t < 15.5:                                 # walks over …
        return dict(x=lerp(470, 505, seg(t, 14.7, 15.5)), y=G, p=walk(t * 8), f=1, hammer=True)
    return dict(x=505, y=G, p=offer(), f=1, hammer=True, reach={"f": (566, G - 112)})   # … and holds the hammer out


def victim(t):
    base = arms_crossed(head=-6)
    for ts, _ in VICTIM_TALK[:4]:
        if ts < t < ts + 1.8:    # complains: palms up, shrugging
            k = seg(t, ts, ts + 0.25) * (1 - seg(t, ts + 1.5, ts + 1.8))
            return dict(x=650, y=G, p=mix(base, shrug(1.0), k), f=-1)
    if t > 15.5:                  # … and finally takes the hammer
        k = seg(t, 15.5, 16.2)
        o = dict(x=650 - 14 * k, y=G, p=mix(dict(base, lean=-2, head=8), dict(stand(), lean=6, head=6), k), f=-1)
        if k > 0.05:
            grab = (574, G - 108)
            o["reach"] = {"f": (lerp(640, grab[0], k), lerp(G - 70, grab[1], k))}
        return o
    if t > TURN + 0.3:            # looks over at the dry, sunny side – hands on hips
        k = seg(t, TURN + 0.3, TURN + 0.8)
        return dict(x=650, y=G, p=mix(base, dict(hands_on_hips(), head=8), k), f=-1)
    return dict(x=650, y=G, p=dict(base, lean=-4 + math.sin(t * 2) * 2), f=-1)


# ------------------------------------------------------------------ world
def rain(c, t, x0, x1, y0, y1, a, n=120, seed=2):
    if a <= 0: return
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(x0, x1); sp = rng.uniform(900, 1300); off = rng.uniform(0, 2000)
        y = y0 + (off + t * sp) % (y1 - y0)
        c.drawLine(x, y, x - 8, y + 30, P((205, 218, 238), 0.55 * a, stroke=2.5))


def bulb_light(t, u):
    """storm: flickers; sun: steady and softer"""
    fl = 1.0
    if u < 1:
        fl = 0.82 + 0.18 * math.sin(t * 23) * math.sin(t * 7.3)
        if 0.45 < t < 0.6 or 6.0 < t < 6.12: fl = 0.35          # flicker with the thunder
    return lerp(fl, 0.75, u)


def bulb_pos(t, u):
    ang = math.radians(7 * math.sin(t * 1.9) * (1 - u))
    top = (BULB[0], roof_y(BULB[0]))
    ln = BULB[1] - top[1]
    return top, (top[0] + math.sin(ang) * ln, top[1] + math.cos(ang) * ln)


def window(c, t, u):
    x, y, w, h = WIN
    sk = skia.GradientShader.MakeLinear([(0, y), (0, y + h)], [C(lerpc((92, 104, 128), (255, 200, 120), u)), C(lerpc((120, 130, 150), (255, 226, 160), u))])
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), skia.Paint(Shader=sk))
    if u > 0: c.drawCircle(x + w * 0.7, y + h * 0.35, 30, P((255, 240, 200), u))
    c.save(); c.clipRect(skia.Rect.MakeXYWH(x, y, w, h)); rain(c, t, x - 20, x + w + 20, y - 40, y + h, 1 - u, n=18, seed=9); c.restore()
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), P((92, 62, 44), stroke=12))
    c.drawLine(x + w / 2, y, x + w / 2, y + h, P((92, 62, 44), stroke=8)); c.drawLine(x, y + h / 2, x + w, y + h / 2, P((92, 62, 44), stroke=8))
    c.drawRect(skia.Rect.MakeXYWH(x - 6, y - 6, w + 12, h + 12), P(INK, stroke=4))


def world(c, t):
    u = sunny(t)
    # outside (above the roof): storm sky → golden afternoon
    sky(c, t, lerpc((70, 80, 104), (120, 150, 210), u), lerpc((104, 112, 132), (255, 190, 130), u), lerpc((130, 136, 150), (255, 220, 160), u), 820)
    for i in range(6):   # clouds racing past outside (storm) / drifting (after)
        cx = (i * 330 + t * lerp(140, 110, u)) % 2000 - 500
        for dx, dy, r in ((-60, 10, 46), (-10, -14, 58), (50, 6, 44)):
            c.drawCircle(cx + dx * 1.3, 560 + (i % 3) * 50 + dy * 1.3, r * 1.3, P(lerpc((88, 96, 118), (255, 232, 196), u), 0.9))
    rain(c, t, -300, W + 300, 300, 820, 1 - u, n=150, seed=3)
    # back wall: warm wooden boards
    wall = poly([(-300, roof_y(-300) + 30), (W + 300, roof_y(W + 300) + 30), (W + 300, G), (-300, G)])
    c.drawPath(wall, P(lerpc((112, 86, 70), (150, 112, 82), u)))
    for i, bx in enumerate(range(-300, W + 300, 58)):
        c.drawLine(bx, roof_y(bx) + 30, bx, G, P((70, 50, 40), 0.55, stroke=3))
        if i % 3 == 0: c.drawCircle(bx + 22, 1010 + (i * 37) % 160, 4, P((70, 50, 40), 0.5))
    # old shelf + boxes for silhouette interest (left)
    c.drawRect(skia.Rect.MakeXYWH(150, 1130, 110, 110), P((150, 112, 74))); c.drawRect(skia.Rect.MakeXYWH(150, 1130, 110, 110), P(INK, stroke=5))
    c.drawLine(150, 1185, 260, 1185, P(INK, 0.6, stroke=3))
    c.drawRect(skia.Rect.MakeXYWH(170, 1070, 74, 60), P((176, 138, 92))); c.drawRect(skia.Rect.MakeXYWH(170, 1070, 74, 60), P(INK, stroke=5))
    # chest under the window (right) – far from the UI column, it is just decor
    c.drawRect(skia.Rect.MakeXYWH(820, 1140, 150, 100), P((128, 86, 60))); c.drawRect(skia.Rect.MakeXYWH(820, 1140, 150, 100), P(INK, stroke=5))
    window(c, t, u)
    # roof: thick slanted boards with two holes
    rp = poly([(-300, roof_y(-300) - 4), (W + 300, roof_y(W + 300) - 4), (W + 300, roof_y(W + 300) + 32), (-300, roof_y(-300) + 32)])
    c.drawPath(rp, P(lerpc((84, 62, 52), (110, 80, 62), u)))
    c.drawLine(-300, roof_y(-300) + 32, W + 300, roof_y(W + 300) + 32, P(INK, stroke=6))
    c.drawLine(-300, roof_y(-300) - 4, W + 300, roof_y(W + 300) - 4, P(INK, stroke=6))
    for bx in range(-200, W + 300, 170):   # rafters
        c.drawRect(skia.Rect.MakeXYWH(bx, roof_y(bx) + 30, 22, 26), P((70, 50, 42))); c.drawRect(skia.Rect.MakeXYWH(bx, roof_y(bx) + 30, 22, 26), P(INK, stroke=4))
    for hx in (H1, H2):
        hole = skia.Path(); hole.addOval(skia.Rect.MakeXYWH(hx - 34, roof_y(hx) - 8, 68, 44))
        sh = lerpc((120, 130, 150), (255, 214, 150), u)
        c.drawPath(hole, P(sh)); c.drawPath(hole, P(INK, stroke=5))
        for k in (-1, 1):  # splintered edge
            c.drawPath(poly([(hx + k * 30, roof_y(hx) + 30), (hx + k * 18, roof_y(hx) + 46), (hx + k * 12, roof_y(hx) + 30)]), P((84, 62, 52)))
    # floor
    c.drawRect(skia.Rect.MakeLTRB(-300, G, W + 300, H + 300), P(lerpc((96, 72, 56), (128, 96, 70), u)))
    for i in range(6):
        c.drawLine(-300, G + 30 + i * 46, W + 300, G + 30 + i * 46, P((60, 44, 36), 0.5, stroke=3))
    c.drawLine(-300, G, W + 300, G, P(INK, stroke=5))
    return u


def bucket(c, x, y, fill):
    pth = poly([(x - 30, y - 56), (x + 30, y - 56), (x + 23, y), (x - 23, y)])
    c.drawPath(pth, P((150, 170, 190))); c.drawPath(pth, P(INK, stroke=5))
    if fill > 0:
        c.drawLine(x - 26, y - 56 + 6, x + 26, y - 56 + 6, P((110, 150, 200), clamp(fill * 2), stroke=6))
    c.drawLine(x - 30, y - 42, x + 30, y - 42, P((120, 140, 160), stroke=3))
    hp = skia.Path(); hp.addArc(skia.Rect.MakeXYWH(x - 30, y - 82, 60, 52), 180, 180)
    c.drawPath(hp, P(INK, stroke=4))


def plank(c, x, y, ang=0.0):
    c.save(); c.translate(x, y); c.rotate(ang)
    r = skia.Rect.MakeXYWH(-50, -10, 100, 20)
    c.drawRect(r, P((206, 160, 104))); c.drawRect(r, P(INK, stroke=5))
    c.drawLine(-38, -2, 30, -2, P((150, 110, 70), stroke=2)); c.restore()


def hammer(c, hx, hy, ang):
    c.save(); c.translate(hx, hy); c.rotate(ang)
    c.drawLine(0, 6, 0, -40, P(INK, stroke=10)); c.drawLine(0, 6, 0, -40, P((180, 130, 80), stroke=5))
    c.drawRect(skia.Rect.MakeXYWH(-16, -54, 32, 16), P((90, 96, 110))); c.drawRect(skia.Rect.MakeXYWH(-16, -54, 32, 16), P(INK, stroke=4))
    c.restore()


def ladder(c):
    top = roof_y(LAD) + 30
    for rx in (LAD - 26, LAD + 26):
        c.drawLine(rx, G + 2, rx, top, P(INK, stroke=12)); c.drawLine(rx, G + 2, rx, top, P((170, 128, 84), stroke=6))
    for ry in range(int(G - 30), int(top), -46):
        c.drawLine(LAD - 26, ry, LAD + 26, ry, P(INK, stroke=9)); c.drawLine(LAD - 26, ry, LAD + 26, ry, P((190, 146, 96), stroke=4))


def drips(c, t, x, y0, y1, a=1.0, rate=1.0, seed=1):
    """falling drops from a roof hole"""
    if a <= 0: return
    rng = np.random.default_rng(seed)
    for i in range(7):
        ph = rng.uniform(0, 1); sp = 1.3 * rate
        k = (t * sp + ph) % 1.0
        y = lerp(y0, y1, k * k)
        c.drawOval(skia.Rect.MakeXYWH(x - 5 + rng.uniform(-3, 3), y - 9, 10, 18), P((170, 205, 240), 0.85 * a))
    k = (t * 2.6) % 1.0   # splash at the bottom
    for s in (-1, 1):
        c.drawLine(x + s * 6, y1 - 4, x + s * (10 + 16 * k), y1 - 14 - 10 * math.sin(k * 3.1), P((190, 220, 245), 0.7 * a * (1 - k), stroke=3))


def floodwater(c, t, u):
    lv = water_lvl(t)
    path = skia.Path(); path.moveTo(-300, G - lv)
    for x in range(-300, W + 320, 30): path.lineTo(x, G - lv + 3 * math.sin(x * 0.04 + t * 3))
    path.lineTo(W + 300, G + 40); path.lineTo(-300, G + 40); path.close()
    c.drawPath(path, P(lerpc((90, 120, 160), (140, 160, 190), u), 0.55))
    c.drawPath(poly([(-300, G - lv), (W + 300, G - lv)], close=False), P((200, 220, 240), 0.5, stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(-300, G, W + 300, G + 60), P((90, 120, 160), 0.25))


def frame(c, t):
    c.save(); c.translate(540, G + DY); c.scale(SC, SC); c.translate(-540, -G)
    u = world(c, t)
    lit = bulb_light(t, u)
    top, bp = bulb_pos(t, u)
    # warm bulb glow on the wall
    c.drawCircle(bp[0], bp[1], 420, P((255, 190, 110), 0.20 * lit, blur=90))
    # sun shaft through the window after the storm
    if u > 0:
        x, y, w, h = WIN
        beam = poly([(x + w, y), (x, y + 20), (330, G), (560, G)])
        sh = skia.GradientShader.MakeLinear([(x + w / 2, y), (450, G)], [C((255, 220, 150), 0.55 * u), C((255, 200, 120), 0.15 * u)])
        c.drawPath(beam, skia.Paint(AntiAlias=True, Shader=sh))
        c.drawOval(skia.Rect.MakeXYWH(340, G - 14, 230, 30), P((255, 220, 150), 0.35 * u, blur=10))
        rng = np.random.default_rng(7)
        for i in range(40):   # dust dancing in the light
            k = (rng.uniform(0, 1) + t * rng.uniform(0.08, 0.2)) % 1.0
            px = lerp(lerp(530, 470, rng.uniform(0, 1)), lerp(330, 560, rng.uniform(0, 1)), k) + 12 * math.sin(t * 2 + i)
            c.drawCircle(px, lerp(y + 40, G - 20, k), 2.5, P((255, 240, 200), 0.7 * u))
    ladder(c)
    if t < 2.95: plank(c, LAD - 52, G - 60, -78)    # leaning against the ladder
    # Owner's bucket
    o = smooth(owner, t)
    dry = seg(t, PATCH + 0.6, HITS[-1])            # her hole stops dripping once it is nailed shut
    fill = seg(t, 1.9, 9.0)
    # Owner
    rim_o = (lerpc((255, 196, 110), (255, 214, 150), u), 0.6)
    lo = (1, -0.4) if t < TURN else (1, -1)
    shadow(c, o["x"], o["y"], S, 0.3)
    jo = figure(c, o["x"], o["y"] - (84 * S + 6 if o.get("mode") == "hip" else 0), o["p"], s=S, facing=o["f"], body=OWN_BODY, rim=rim_o, light=lo,
                mode=o.get("mode", "feet"), reach=o.get("reach"), plant=o.get("plant"))
    if o.get("bucket"): bucket(c, jo["hand_f"][0] + 4, jo["hand_f"][1] + 46, 0)
    elif t > 1.7: bucket(c, H1 + 8, G, fill)
    if o.get("plank"):
        plank(c, jo["hand_b"][0] + 8, jo["hand_b"][1] - 4, -80 if t < 5.6 else -7)
    if t >= PATCH:  # plank nailed under the hole
        plank(c, H1 + 6, roof_y(H1) + 42, -7)
        for k in range(min(6, sum(1 for h in HITS if t > h))):
            c.drawCircle(H1 - 36 + k * 15, roof_y(H1) + 42 + k * 1.8, 3.5, P((60, 60, 70)))
    def draw_hammer():
        hx, hy = jo["hand_f"]; sx, sy = jo["el_f"]
        hammer(c, hx, hy, math.degrees(math.atan2(hx - sx, -(hy - sy))))
    if o.get("hammer") and t < 14.7: draw_hammer()
    drips(c, t, H1, roof_y(H1) + 30, G - 58 if t > 1.9 else G - water_lvl(t), 1 - dry, seed=2)
    for h in HITS:     # dust puffs from the hammer
        if h < t < h + 0.35:
            k = (t - h) / 0.35
            c.drawCircle(H1 + 6, roof_y(H1) + 40, 10 + 30 * k, P((230, 210, 180), 0.5 * (1 - k)))
    # Victim
    v = smooth(victim, t)
    lv = (-1, -0.4) if t < TURN else (-1, -0.8)
    shadow(c, v["x"], v["y"], S, 0.3)
    jv = figure(c, v["x"], v["y"], v["p"], s=S, facing=v["f"], body=VIC_BODY, rim=((170, 200, 255), 0.5), light=lv,
                reach=v.get("reach"))
    drips(c, t, H2, roof_y(H2) + 30, jv["head"][1] - 18, lerp(1.0, 0.75, u), rate=1.1, seed=4)
    # wet sheen on the victim's head
    c.drawCircle(jv["head"][0], jv["head"][1] - 8, 14, P((180, 210, 240), 0.35))
    if o.get("hammer") and t >= 14.7: draw_hammer()   # in front of the victim when offered
    floodwater(c, t, u)
    # the bulb (in front of the wall, under the roof)
    c.drawLine(top[0], top[1] + 30, bp[0], bp[1] - 14, P(INK, stroke=4))
    c.drawCircle(bp[0], bp[1], 60, P((255, 210, 140), 0.45 * lit, blur=24))
    c.drawCircle(bp[0], bp[1], 15, P(lerpc((150, 130, 100), (255, 236, 180), lit)))
    c.drawCircle(bp[0], bp[1], 15, P(INK, stroke=4))
    c.drawRect(skia.Rect.MakeXYWH(bp[0] - 8, bp[1] - 26, 16, 12), P((120, 120, 130))); c.drawRect(skia.Rect.MakeXYWH(bp[0] - 8, bp[1] - 26, 16, 12), P(INK, stroke=3))
    # labels
    sep = 26 * seg(t, 14.7, 15.3)                 # keep the two labels apart when they stand close
    plate_label(c, "OWNER", max(jo["head"][0], 250) - sep, jo["head"][1] - 52, AMBER, 0.95)
    plate_label(c, "VICTIM", jv["head"][0] + sep, jv["head"][1] - 52, GREY, 0.9)
    for ts, txt in VICTIM_TALK:
        if ts < t < ts + 1.9:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.6, ts + 1.9))
            bubble(c, 600, jv["head"][1] - 170, txt, a, "speech", tail=(jv["head"][0] - 10, jv["head"][1] - 60), size=32,
                   pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    if 0.45 < t < 0.9:   # lightning through the window/holes
        c.drawRect(skia.Rect.MakeWH(W, H), P((235, 240, 255), 0.30 * (1 - seg(t, 0.55, 0.9))))
    if u > 0:  # warm grade after the turn
        c.drawRect(skia.Rect.MakeWH(W, H), P((255, 190, 110), 0.06 * u))
    vignette(c, 0.42)
    grain(c, t, 0.035)
    end_text(c, t, 14.6, "It's not your fault it rained.", "But it's your roof.", "Own it.", y=1430)


HOOK = "If you blame the rain, you never fix the roof.\nWatch what 2 people do before it floods."


def events():
    ev = [["rain", 0.0, TURN - 0.4], ["thunder", 0.5], ["thunder", 6.0], ["land", 1.75], ["slide", 2.9]]
    for ts, _ in VICTIM_TALK: ev.append(["pop", ts])
    for k in range(5): ev.append(["step", 0.15 + k * 0.28, False])
    for k in range(6): ev.append(["step", 3.3 + k * 0.4, True])
    ev.append(["thud", PATCH])
    for h in HITS: ev.append(["thud", h])
    for k in range(4): ev.append(["step", 9.7 + k * 0.35, True])
    ev += [["sunrise", TURN - 1.4], ["summit", TURN], ["text", 14.6], ["text2", 15.4]]
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still":
        import lib
        ts = [float(a) for a in sys.argv[2:]] or [0.5, 2.4, 4.4, 7.3, 12.9, 15.9]
        def ov(c, t):   # same as the final cut: off = 0.3, overlays in video time
            frame(c, t + 0.3); lib.series_overlay(c, t, 11, HOOK, 16.2 - 0.3, 380, None)
        stills(ov, ts, "check/ep11")
    else:
        finish_v2("Folge11_Owner", frame, T_END, events(), TURN, 11, HOOK, 0.3, 16.2)
