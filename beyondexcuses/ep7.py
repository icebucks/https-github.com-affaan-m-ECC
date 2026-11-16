"""Folge 7: PEOPLE PLEASER vs. GRENZEN – Herbstwald-Wanderung, alle geben ihm ihren Rucksack. Kamera fährt mit."""
import sys, math
import numpy as np
from lib import *

T_END = 18.8
G = 1250
S = 0.9
SCROLL = 150.0
BAGCOLS = [(90, 140, 200), (200, 80, 80), (110, 170, 100), (170, 120, 200)]
# others: name, keyframes (t, x), ask text, reply text, bag transfer time
OTHERS = [
    ("KOLLEGE", [(0.3, -120), (2.0, 660), (3.9, 660), (4.5, 300), (5.4, 300), (7.6, 1250)], "Und du?", "Klar!", 5.0),
    ("CHEF", [(5.4, -120), (6.9, 260), (8.0, 260), (9.8, 1250)], "Machst du das noch?", "Kein Problem!", 7.6),
    ("FREUND", [(8.2, -120), (9.4, 205), (10.4, 205), (12.2, 1250)], "Nimmst du meins?", "Na klar!", 10.0),
    ("FAMILIE", [(10.4, -120), (11.4, 165), (12.3, 165), (14.2, 1250)], "Du schaffst das doch.", "…okay.", 12.0),
]


def kf(keys, t):
    if t <= keys[0][0]: return keys[0][1], 0
    for (t0, x0), (t1, x1) in zip(keys, keys[1:]):
        if t0 <= t < t1: return lerp(x0, x1, (t - t0) / (t1 - t0)), (x1 > x0) - (x1 < x0)
    return keys[-1][1], 0


def n_bags(t): return sum(1 for o in OTHERS if t > o[4] + 0.4)


def pp(t):
    n = n_bags(t)
    if t < 12.8:
        x = lerp(470, 310, seg(t, 4.5, 12.6))
        return dict(x=x, p=walk(t * 7.5, lean=6 + 8 * n, stride=24 - 3 * n, arm=20 - 3 * n), rot=0)
    if t < 13.4:
        return dict(x=305, p=mix(walk(t * 7.5, lean=38), crouch(), seg(t, 12.8, 13.3)), rot=0)
    k = seg(t, 13.4, 14.0)
    return dict(x=305 + 30 * k, p=crouch(), rot=78 * k, down=k)


def grenzen(t):
    if t < 13.6: return dict(x=820, p=walk(t * 7.5), f=1)
    if t < 14.2: return dict(x=820, p=stand(), f=1)
    return dict(x=820, p=dict(stand(), head=10), f=-1)


def tree(c, x, y, sc, col, trunk, seed):
    rng = np.random.default_rng(seed)
    blobs = [(x + rng.uniform(-70, 70) * sc, y - (230 + rng.uniform(-40, 70)) * sc, rng.uniform(55, 85) * sc, rng.uniform(0, 0.4)) for _ in range(6)]
    c.drawLine(x, y, x, y - 230 * sc, P(INK, stroke=26 * sc)); c.drawLine(x, y, x, y - 230 * sc, P(trunk, stroke=18 * sc))
    for cx, cy, r, _ in blobs: c.drawCircle(cx, cy, r + 4, P(INK))
    for cx, cy, r, k in blobs: c.drawCircle(cx, cy, r, P(lerpc(col, (255, 220, 120), k)))


def world(c, t):
    u = seg(t, 3.0, 16.0)
    sky(c, t, lerpc((120, 170, 220), (60, 50, 100), u), lerpc((240, 200, 150), (230, 120, 90), u), lerpc((255, 230, 170), (255, 170, 100), u), G)
    sun(c, 860, lerp(560, 1150, u), 1.0, r=68)
    off = t * SCROLL
    # far trees (parallax 0.45)
    for i in range(12):
        x = (i * 160 - off * 0.45) % 1920 - 420
        tree(c, x, G - 30, 0.75, lerpc((200, 110, 70), (120, 60, 70), u), (70, 50, 50), i)
    c.drawRect(skia.Rect.MakeLTRB(-300, -400, W + 300, G), P(lerpc((255, 220, 180), (80, 50, 90), u), 0.25))
    ground(c, G, lerpc((150, 110, 70), (90, 60, 60), u), lerpc((70, 50, 40), (30, 20, 26), u), (255, 220, 170))
    c.drawRect(skia.Rect.MakeLTRB(-300, G + 2, W + 300, G + 52), P(lerpc((190, 150, 100), (120, 84, 70), u)))
    # stones on the path scroll by
    for i in range(14):
        x = (i * 137 - off) % 1900 - 400
        c.drawOval(skia.Rect.MakeXYWH(x, G + 14 + (i % 3) * 10, 18 + (i % 4) * 6, 8), P(INK, 0.35))
    # near trees (parallax 1.0) – in front band lower
    for i in range(5):
        x = (i * 420 + 200 - off) % 2100 - 500
        tree(c, x, G + 4, 1.0, lerpc((230, 120, 50), (160, 70, 60), u), (90, 60, 50), 50 + i)
    return u


def leaves(c, t):
    rng = np.random.default_rng(8)
    for i in range(30):
        x0 = rng.uniform(-200, W + 200); sp = rng.uniform(80, 160); ph = rng.uniform(0, 6.3); off = rng.uniform(0, 1600)
        y = (off + t * sp) % 1500 - 200
        x = (x0 - t * SCROLL * 0.8 + math.sin(t * 1.5 + ph) * 40) % (W + 300) - 150
        c.save(); c.translate(x, y); c.rotate(math.degrees(t * 2 + ph))
        c.drawOval(skia.Rect.MakeXYWH(-9, -5, 18, 10), P([(240, 130, 50), (250, 190, 70), (210, 80, 50)][i % 3], 0.9))
        c.restore()


def bag_rect(c, cx, cy, ang, col, a=1.0):
    c.save(); c.translate(cx, cy); c.rotate(ang)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-26, -20, 52, 40), 9, 9)
    c.drawRRect(rr, P(col, a)); c.drawRRect(rr, P(INK, a, stroke=5))
    c.drawLine(-14, -4, 14, -4, P(INK, 0.6 * a, stroke=3))
    c.restore()


def stack_slot(J, i, s):
    hx, hy = J["hip"]; sx, sy = J["sh"]
    ux, uy = sx - hx, sy - hy; n = math.hypot(ux, uy); ux, uy = ux / n, uy / n
    bx, by = uy, -ux                       # backwards (figure faces right)
    cx = hx + ux * (30 + i * 40) * s / 0.9 + bx * 34
    cy = hy + uy * (30 + i * 40) * s / 0.9 + by * 34
    return cx, cy, math.degrees(math.atan2(uy, ux)) + 90


def frame(c, t):
    c.save(); c.translate(540, G); c.scale(1.1, 1.1); c.translate(-540, -G)
    u = world(c, t)
    body = lerpc((248, 248, 244), (255, 232, 214), u)
    g = grenzen(t)
    jg = figure(c, g["x"], G, g["p"], s=S, facing=g["f"], body=body)
    label(c, "GRENZEN", jg["head"][0], jg["head"][1] - 50, AMBER, 0.95)
    # people pleaser
    p = pp(t)
    jp = figure(c, p["x"], G, p["p"], s=S, facing=1, rot=p["rot"], body=body)
    n = n_bags(t)
    for i in range(n): bag_rect(c, *stack_slot(jp, i, S), BAGCOLS[i])
    lab_y = min(jp["head"][1], stack_slot(jp, max(n - 1, 0), S)[1]) - 60
    label(c, "PEOPLE PLEASER", jp["head"][0], lab_y if p["rot"] < 30 else jp["head"][1] - 70, (235, 235, 245), 0.9)
    # others
    for k, (name, keys, ask, reply, tb) in enumerate(OTHERS):
        x, moving = kf(keys, t)
        if x < -110 or x > 1240: continue
        pose = walk(t * 9) if moving else stand()
        jo = figure(c, x, G, pose, s=S * 0.95, facing=-1 if moving < 0 else 1, body=lerpc(body, (190, 190, 200), 0.45))
        label(c, name, jo["head"][0], jo["head"][1] - 48, GREY, 0.8)
        # bag on their back until transfer
        own = stack_slot(jo, 0, S * 0.95)
        if t < tb: bag_rect(c, *own, BAGCOLS[k])
        elif t < tb + 0.4:
            dst = stack_slot(jp, k, S); v = ease((t - tb) / 0.4)
            bag_rect(c, lerp(own[0], dst[0], v), lerp(own[1], dst[1], v) - 80 * math.sin(math.pi * v), lerp(own[2], dst[2], v), BAGCOLS[k])
        # dialogue
        ta = keys[-2][0] - (1.1 if k else 1.4) if k else 4.6
        if k == 0 and 2.0 < t < 3.4:
            bubble(c, jo["head"][0] - 40, jo["head"][1] - 130, "Trägst du meinen?", seg(t, 2.0, 2.15) * (1 - seg(t, 3.1, 3.4)), "speech", tail=(jo["head"][0], jo["head"][1] - 40), size=28)
        if k == 0 and 2.8 < t < 4.3:
            bubble(c, jg["head"][0] - 30, jg["head"][1] - 220, "Nein. Das schaffst du.", seg(t, 2.8, 2.95) * (1 - seg(t, 4.0, 4.3)), "speech", tail=(jg["head"][0], jg["head"][1] - 40), size=28)
        ta = tb - 0.9
        if ta < t < tb + 0.3:
            bubble(c, max(230, jo["head"][0] - 50), jo["head"][1] - 135, ask, seg(t, ta, ta + 0.15) * (1 - seg(t, tb, tb + 0.3)), "speech", tail=(jo["head"][0], jo["head"][1] - 40), size=28)
        if tb - 0.3 < t < tb + 0.9:
            bubble(c, jp["head"][0] + 110, lab_y - 75, reply, seg(t, tb - 0.3, tb - 0.15) * (1 - seg(t, tb + 0.6, tb + 0.9)), "speech", tail=(jp["head"][0], jp["head"][1] - 40), size=28)
    if 14.4 < t < 15.6:
        bubble(c, jg["head"][0], jg["head"][1] - 130, "…", seg(t, 14.4, 14.55) * (1 - seg(t, 15.3, 15.6)), "think", tail=(jg["head"][0], jg["head"][1] - 40), size=30)
    leaves(c, t)
    c.restore()
    vignette(c, 0.45)
    end_text(c, t, 15.6, "Du kannst nicht", "jeden tragen.", "Nein ist ein ganzer Satz.", y=1460)
    if t > T_END - 0.5: c.drawRect(skia.Rect.MakeWH(W, H), P((0, 0, 0), (t - (T_END - 0.5)) / 0.5))


def events():
    ev = [["pop", 2.0], ["pop", 2.8], ["thud", 13.9], ["text", 15.6], ["text2", 16.4]]
    for (_, _, _, _, tb) in OTHERS: ev += [["pop", tb - 0.9], ["pop", tb - 0.3], ["land", tb + 0.4]]
    last = None
    for f in range(int(13.3 * FPS)):
        tt = f / FPS; k = math.floor(tt * 7.5 / math.pi)
        if last is not None and k != last: ev.append(["step", tt, False])
        last = k
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still": stills(frame, [2.4, 5.0, 7.6, 10.0, 12.2, 14.6], "/home/claude/mind/ep7")
    else: finish_v2("Folge7_PeoplePleaser", frame, T_END, events(), 30.0, 7, "Sagst du auch zu allem Ja?", 0.5, 17.0)
