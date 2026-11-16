"""Folge 6: KOMFORTZONE vs. WACHSTUM – warme Blase im Schneesturm; wer rausgeht, wächst; die Blase schrumpft."""
import sys, math
import numpy as np
from lib import *

T_END = 18.8
G = 1250
BX = 300                     # bubble centre x
ICE = (170, 205, 245)


def storm(t): return 1 - seg(t, 8.5, 12.0)


def bubble_r(t): return lerp(270, 150, seg(t, 3.0, 15.0))


def wachstum(t):
    if t < 1.4: return dict(x=390, p=sit(t), s=0.80, f=1, hip=True, y=G - 40 - 32)
    if t < 2.0: return dict(x=400, p=mix(sit(t), stand(), seg(t, 1.4, 2.0)), s=0.80, f=1, y=G)
    if t < 12.0:
        u = (t - 2.0) / 10.0
        x = lerp(400, 820, 1 - (1 - u) ** 1.4)
        st = storm(t)
        p = walk(t * 6.5, lean=lerp(8, 26, st), stride=lerp(24, 16, st), arm=14)
        if st > 0.3: p.update(arm_f=lerp(p["arm_f"], 120, st * 0.7), elb_f=lerp(18, 60, st))  # shields face
        return dict(x=x, p=p, s=lerp(0.80, 1.30, seg(t, 3.0, 12.0)), f=1, y=G)
    return dict(x=820, p=mix(stand(), cheer(t), seg(t, 12.0, 12.6)), s=1.30, f=-1 if t > 14 else 1, y=G)


def komfort(t):
    r = bubble_r(t)
    cramped = seg(t, 11.0, 15.0)
    p = sit(t); p.update(arm_f=30, elb_f=50, head=-4 + 3 * math.sin(t))
    if t > 6.0 and t < 11:
        p.update(head=-15, lean=-2)  # looks at the TV
    if cramped > 0:
        p = mix(p, dict(sit(t), lean=40, head=30, arm_f=95, elb_f=40, arm_b=85, elb_b=40), cramped)
    return dict(x=BX - 20, p=p, s=0.80, y=G - 40 - 32)


def draw_room(c, t):
    r = bubble_r(t)
    cy = G
    # warm dome
    c.save()
    dome = skia.Path(); dome.addCircle(BX, cy, r)
    c.clipPath(dome, skia.ClipOp.kIntersect, True)
    sh = skia.GradientShader.MakeRadial((BX, cy - r * 0.4), r * 1.2, [C((255, 214, 150)), C((220, 140, 90))])
    c.drawRect(skia.Rect.MakeLTRB(BX - r, cy - r, BX + r, cy), skia.Paint(Shader=sh))
    # tv glow
    fl = 0.6 + 0.4 * abs(math.sin(t * 9) * math.sin(t * 3.3))
    tvx = BX + 70 * (r / 270)
    c.drawCircle(tvx, cy - 60, 90, P((120, 180, 255), 0.35 * fl, blur=30))
    c.restore()
    # floor rug
    c.drawOval(skia.Rect.MakeXYWH(BX - r * 0.8, cy - 10, r * 1.6, 22), P((180, 70, 60)))
    # tv
    tv = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(tvx - 30, cy - 92, 60, 44), 6, 6)
    c.drawRRect(tv, P((150, 200, 255))); c.drawRRect(tv, P(INK, stroke=5))
    c.drawLine(tvx, cy - 48, tvx, cy, P(INK, stroke=6))
    # armchair
    ax = BX - 40
    c.drawRoundRect(skia.Rect.MakeXYWH(ax - 70, cy - 120, 30, 120), 12, 12, P((150, 70, 70)))
    c.drawRoundRect(skia.Rect.MakeXYWH(ax - 70, cy - 120, 30, 120), 12, 12, P(INK, stroke=5))
    c.drawRoundRect(skia.Rect.MakeXYWH(ax - 60, cy - 50, 120, 50), 12, 12, P((170, 84, 80)))
    c.drawRoundRect(skia.Rect.MakeXYWH(ax - 60, cy - 50, 120, 50), 12, 12, P(INK, stroke=5))
    # bubble glass edge
    c.drawArc(skia.Rect.MakeLTRB(BX - r, cy - r, BX + r, cy + r), 180, 180, False, P(INK, stroke=7))
    c.drawArc(skia.Rect.MakeLTRB(BX - r, cy - r, BX + r, cy + r), 180, 180, False, P((255, 230, 190), 0.8, stroke=3))
    c.drawCircle(BX, cy - r * 0.55, r * 1.05, P((255, 190, 120), 0.18, blur=50))
    return r


def snow(c, t, amt):
    if amt <= 0: return
    rng = np.random.default_rng(5)
    for i in range(int(300 * amt) + 1):
        x0 = rng.uniform(-300, W + 300); sp = rng.uniform(250, 420); off = rng.uniform(0, 2000)
        y = (off + t * sp) % (G + 300) - 250
        x = x0 - (y + 250) * 0.6 * amt + math.sin(t * 2 + i) * 8
        if abs(x - BX) < bubble_r(t) and y > G - bubble_r(t) + abs(x - BX) * 0.3: continue
        ln = 6 + 16 * amt
        c.drawLine(x, y, x - ln * 0.6, y + ln * 0.5, P((240, 246, 255), 0.85 * amt, stroke=3.5 + (i % 3)))


def frame(c, t):
    st = storm(t); dawn = seg(t, 9.0, 13.5)
    sky(c, t, lerpc((20, 26, 44), (90, 140, 210), dawn), lerpc((50, 62, 90), (230, 170, 140), dawn), lerpc((90, 104, 130), (255, 214, 160), dawn), G, stars=0)
    sun(c, 820, lerp(1300, 760, dawn), dawn, r=80)
    hills(c, G, lerpc((60, 74, 100), (190, 200, 225), dawn), amp=40, off=0.4, height=150)
    hills(c, G, lerpc((80, 96, 124), (215, 225, 240), dawn), amp=24, off=2.4, height=70)
    ground(c, G, lerpc((150, 166, 196), (240, 244, 252), dawn), lerpc((60, 70, 96), (170, 186, 214), dawn), (255, 255, 255))
    # footprints of wachstum in the snow
    w = wachstum(t)
    for k in range(int((w["x"] - 430) / 38)):
        fx = 440 + k * 38
        c.drawOval(skia.Rect.MakeXYWH(fx, G + 10 + (k % 2) * 10, 22, 8), P((90, 110, 150), 0.5))
    r = draw_room(c, t)
    body = lerpc((236, 240, 248), (255, 240, 226), dawn)
    k = komfort(t)
    jk = figure(c, k["x"], k["y"], k["p"], s=k["s"], facing=1, body=(255, 236, 214), mode="hip")
    label(c, "KOMFORTZONE", BX, G - r - 30, ICE, 0.95)
    if w.get("hip"):
        jw = figure(c, w["x"], w["y"], w["p"], s=w["s"], facing=w["f"], body=(255, 236, 214), mode="hip")
    else:
        jw = figure(c, w["x"], w["y"], w["p"], s=w["s"], facing=w["f"], body=body)
    label(c, "WACHSTUM", jw["head"][0], jw["head"][1] - 34 - 26 * w["s"], AMBER, 0.95)
    snow(c, t, st)
    # dialogue
    hx, hy = jk["head"]
    for t0, t1, s in ((2.2, 4.4, "Bleib doch hier!"), (5.2, 7.4, "Draußen ist es kalt."), (8.2, 10.4, "Hier ist es sicher.")):
        if t0 < t < t1:
            bubble(c, 330, G - r - 130, s, seg(t, t0, t0 + 0.15) * (1 - seg(t, t1 - 0.3, t1)), "speech", tail=(hx + 10, G - r - 40), size=30)
    if 13.0 < t < 15.5:
        bubble(c, 300, G - r - 130, "Wird's hier enger…?", seg(t, 13.0, 13.15) * (1 - seg(t, 15.2, 15.5)), "think", tail=(hx, hy - 40), size=30)
    # size marker: "wachstum" gets taller
    vignette(c, 0.45)
    end_text(c, t, 15.6, "Die Komfortzone ist gemütlich.", "Aber nichts wächst darin.", "Geh raus.", y=1460)
    if t > T_END - 0.5: c.drawRect(skia.Rect.MakeWH(W, H), P((0, 0, 0), (t - (T_END - 0.5)) / 0.5))


def events():
    ev = [["rain", 0.0, 11.5], ["pop", 2.2], ["pop", 5.2], ["pop", 8.2], ["pop", 13.0], ["sunrise", 9.5], ["summit", 12.0],
          ["text", 15.6], ["text2", 16.4]]
    last = None
    for f in range(int(12 * FPS)):
        tt = f / FPS
        if tt > 2.0:
            k = math.floor(tt * 6.5 / math.pi)
            if last is not None and k != last: ev.append(["step", tt, False])
            last = k
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still": stills(frame, [1.0, 3.0, 6.5, 10.0, 13.5, 17.5], "/home/claude/mind/ep6")
    else: finish_v2("Folge6_Komfortzone", frame, T_END, events(), 10.5, 6, "Wie gemütlich ist deine Blase?", 1.0, 17.0)
