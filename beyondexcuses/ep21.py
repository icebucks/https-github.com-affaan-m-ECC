"""Episode 21 (TikTok: Part 18): QUITTER vs FINISHER – promised by the Part 17 cliffhanger ("the one who sits down at mile 20").
A marathon in the pouring rain, mile 20 sign, wet asphalt, grey city.
Quitter (grey): runs, slows down, "My legs are done." – sits down on the curb – "I'll never make it."
Finisher (amber): slows down too – "Just walk. One more mile." – walks, then jogs again ("6 miles later") and breaks the
finish tape as the rain stops: "Slow is still forward." """
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 18                     # TikTok part number (internal episode 21)
G = 1300                       # road surface
S = 1.3
SKIP0, SKIP1 = 6.0, 8.6        # "6 miles later": camera travels to the finish
TURN = 9.8                     # finish tape breaks
SIGN_X = 330                   # MILE 20 sign / curb where the quitter sits
CURB = (230, 430)              # concrete curb block (x range)
CURB_H = 52
ARCH_X = 2050                  # finish arch
Q_BODY = (196, 202, 216)
F_BODY = (255, 226, 178)
TALK = [(1.4, "q", "My legs are done."), (2.7, "f", "Mine too."), (3.6, "q", "I'll never make it."),
        (4.6, "f", "Just walk. One more mile."), (TURN + 0.9, "f", "Slow is still forward.")]
HOOK = "Mile 20. Pouring rain.\nOnly one sat down."
FOCUS = (540, 1180)
COVER = False                  # covers.py sets True: scene without speech bubbles
CTA = "Part 19 next:\nthe one who waits for a sign"


# ------------------------------------------------------------------ motion
def fin_x(t):
    """finisher world x"""
    if t < 2.6: return lerp(230, 400, t / 2.6)                                    # running, slowing
    if t < SKIP0: return 400 + 40 * (t - 2.6)                                      # walking
    if t < SKIP1: return lerp(400 + 40 * (SKIP0 - 2.6), ARCH_X - 260, seg(t, SKIP0, SKIP1))   # jogs on (skip)
    if t < TURN + 0.6: return lerp(ARCH_X - 260, ARCH_X + 40, (t - SKIP1) / (TURN + 0.6 - SKIP1))
    return ARCH_X + 40 + 30 * seg(t, TURN + 0.6, TURN + 1.4)


def quit_x(t):
    if t < 2.0: return lerp(40, SIGN_X - 10, t / 2.0)
    return SIGN_X - 10 + 6 * seg(t, 2.0, 2.4)


def cam_x(t):
    both = (quit_x(t) + fin_x(t)) / 2 + 40
    follow = fin_x(t) - 60
    k = seg(t, SKIP0 - 0.3, SKIP0 + 0.4)
    return lerp(both, follow, k)


def quitter(t):
    f = 1.0
    if t < 2.0:                                                            # running, getting slower
        ph = t * lerp(11, 6, t / 2.0)
        p = mix(run(ph), walk(ph, lean=10), seg(t, 1.0, 2.0))
        return dict(x=quit_x(t), y=G, p=p, f=f, hip=False)
    k = seg(t, 2.0, 2.6)                                                   # sits down on the curb
    p = mix(dict(stand(), lean=20, head=20), sit(t), k)
    if t > 2.6:                                                            # head in his hands, then hangs
        p = dict(sit(t), lean=30, head=28, arm_f=40, elb_f=120, arm_b=34, elb_b=120)
        if t > 3.4: p = mix(p, dict(sit(t), lean=34, head=30, arm_f=26, elb_f=40, arm_b=20, elb_b=40), seg(t, 5.0, 5.6))
    y = lerp(G, G - CURB_H - 4, k)
    return dict(x=quit_x(t), y=y, p=p, f=f, hip=k > 0.5)


def finisher(t):
    f = 1.0
    if t < 2.6:
        ph = t * lerp(11, 7, t / 2.6)
        p = mix(run(ph), walk(ph, lean=12, stride=18), seg(t, 1.8, 2.6))
    elif t < SKIP0:                                                        # walks, head down, steady
        p = walk(t * 6.5, lean=10, stride=18, arm=24)
        p = mix(p, dict(p, head=-4), seg(t, 4.4, 4.8))
    elif t < TURN + 0.4:                                                   # jogs again, then sprints
        p = run(t * (9 if t < SKIP1 else 12))
    else:                                                                  # arms up through the tape
        p = mix(run(t * 10), cheer(t), seg(t, TURN, TURN + 0.5))
    return dict(x=fin_x(t), y=G, p=p, f=f, hip=False)


# ------------------------------------------------------------------ world
def clear_k(t): return seg(t, TURN - 0.4, TURN + 1.2)                      # rain stops, light comes


def city(c, t, cx):
    k = clear_k(t)
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, G)], [C(lerpc((70, 76, 92), (120, 150, 200), k)), C(lerpc((112, 116, 128), (250, 190, 140), k))])
    c.drawRect(skia.Rect.MakeLTRB(cx - 900, -200, cx + 900, G), skia.Paint(Shader=sh))
    if k > 0: c.drawCircle(cx + 260, 760, 260, P((255, 214, 150), 0.35 * k, blur=90))
    # far buildings (parallax 0.5)
    rng = np.random.default_rng(7)
    for i in range(-6, 40):
        bx = i * 120 + cx * 0.5
        bh = 160 + rng.integers(0, 240)
        col = lerpc((84, 88, 104), (150, 130, 140), k)
        c.drawRect(skia.Rect.MakeLTRB(bx, G - 240 - bh, bx + 104, G - 200), P(col))
        for wy in range(int(G - 220 - bh), int(G - 230), 46):
            for wx in (bx + 16, bx + 58):
                c.drawRect(skia.Rect.MakeXYWH(wx, wy, 26, 22), P((255, 220, 150), 0.18 + 0.1 * ((wx + wy) % 3 == 0)))
    haze(c, G - 220, lerpc((150, 156, 170), (255, 210, 170), k), 0.35)
    # crowd barrier line
    c.drawRect(skia.Rect.MakeLTRB(cx - 900, G - 200, cx + 900, G - 120), P(lerpc((72, 76, 88), (110, 96, 96), k)))
    for x in range(int((cx - 900) // 60 * 60), int(cx + 900), 60):
        c.drawLine(x, G - 120, x, G - 60, P((60, 60, 70), stroke=5))
    c.drawLine(cx - 900, G - 104, cx + 900, G - 104, P((220, 80, 70), stroke=8))
    # road
    c.drawRect(skia.Rect.MakeLTRB(cx - 900, G - 60, cx + 900, H + 200), P((52, 54, 62)))
    for x in range(int((cx - 900) // 140 * 140), int(cx + 900), 140):
        c.drawRect(skia.Rect.MakeXYWH(x, G + 80, 70, 10), P((220, 220, 210), 0.6))
    # wet reflections
    c.drawRect(skia.Rect.MakeLTRB(cx - 900, G - 10, cx + 900, G + 60), P((140, 150, 170), 0.18 * (1 - k) + 0.1, blur=10))


def mile_sign(c):
    X = SIGN_X - 190                                                       # sign left of the curb, clear of the heads
    c.drawLine(X + 60, G - 60, X + 60, G - 490, P((70, 70, 80), stroke=10))
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(X - 40, G - 640, 200, 140), 12, 12)
    c.drawRRect(rr, P((236, 128, 60))); c.drawRRect(rr, P(INK, stroke=5))
    text(c, "MILE", X + 60, G - 592, F_CAP, 34, (255, 255, 255), 1.0)
    text(c, "20", X + 60, G - 520, F_CAP, 66, (255, 255, 255), 1.0)


def curb(c):
    c.drawRect(skia.Rect.MakeLTRB(CURB[0], G - CURB_H, CURB[1], G + 4), P((130, 132, 140)))
    c.drawRect(skia.Rect.MakeLTRB(CURB[0], G - CURB_H, CURB[1], G + 4), P(INK, stroke=4))


def arch(c, t, broke):
    x0, x1 = ARCH_X - 170, ARCH_X + 170
    for x in (x0, x1):
        c.drawRect(skia.Rect.MakeLTRB(x - 22, G - 560, x + 22, G), P((60, 64, 80)))
        c.drawRect(skia.Rect.MakeLTRB(x - 22, G - 560, x + 22, G), P(INK, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 30, G - 620, x1 + 30, G - 520), P((236, 128, 60)))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 30, G - 620, x1 + 30, G - 520), P(INK, stroke=5))
    text(c, "FINISH", ARCH_X, G - 548, F_CAP, 60, (255, 255, 255), 1.0)
    # tape at chest height
    ty = G - 150
    if not broke:
        c.drawLine(x0, ty, x1, ty, P((255, 255, 255), stroke=6))
    else:
        k = seg(t, TURN, TURN + 0.6)
        c.drawLine(x0, ty, lerp(ARCH_X, x0 + 40, k), ty + 80 * k, P((255, 255, 255), stroke=6))
        c.drawLine(x1, ty, lerp(ARCH_X, x1 - 40, k), ty + 80 * k, P((255, 255, 255), stroke=6))


def rain(c, t, a):
    if a <= 0: return
    rng = np.random.default_rng(3)
    xs = rng.uniform(-100, W + 100, 140); ys = rng.uniform(0, H, 140); sp = rng.uniform(1700, 2300, 140)
    for x, y0, v in zip(xs, ys, sp):
        y = (y0 + v * t) % (H + 200) - 100
        xx = x - 0.18 * (y - y0)
        c.drawLine(xx, y, xx - 8, y + 44, P((200, 210, 230), 0.45 * a, stroke=2))


def splashes(c, t, a, cx):
    if a <= 0: return
    for i in range(16):
        ph = (t * 2.3 + i * 0.37) % 1
        x = cx - 520 + (i * 97 + int(t * 2.3 + i * 0.37) * 53) % 1040
        r = 6 + 18 * ph
        c.drawOval(skia.Rect.MakeXYWH(x - r, G + 30 - r * 0.25, 2 * r, r * 0.5), P((210, 220, 235), 0.5 * a * (1 - ph), stroke=2))


def frame(c, t):
    cx = cam_x(t)
    zoom = 1.3 * (1 + 0.015 * math.sin(t * 0.8) + 0.06 * seg(t, TURN + 1.0, 13.6))
    c.save(); c.translate(540 + 4 * math.sin(t * 0.6), 1150); c.scale(zoom, zoom); c.translate(-cx, -(G - 170))
    city(c, t, cx)
    mile_sign(c); curb(c)
    broke = t >= TURN
    arch(c, t, broke)
    lo = (-1, -0.6)
    heads = {}
    q = quitter(t)
    jq = figure(c, q["x"], q["y"], q["p"], s=S, facing=q["f"], body=Q_BODY, rim=((210, 220, 255), 0.5), light=lo,
                mode="hip" if q["hip"] else "feet")
    heads["q"] = jq["head"]
    fn = finisher(t)
    jf = figure(c, fn["x"], fn["y"], fn["p"], s=S, facing=fn["f"], body=F_BODY, rim=((255, 220, 170), 0.6), light=lo)
    heads["f"] = jf["head"]
    # race bibs
    for j, num in ((jq, "214"), (jf, "387")):
        hx, hy = j["head"]
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(hx - 30, hy + 50, 60, 38), 5, 5)
        c.drawRRect(rr, P((250, 250, 245), 0.95)); c.drawRRect(rr, P(INK, stroke=2))
        text(c, num, hx, hy + 80, F_SANS, 28, INK, 1.0)
    if TURN < t < TURN + 3.4:                                              # confetti at the finish
        k = (t - TURN) / 3.4
        rng = np.random.default_rng(11)
        for i in range(40):
            ang = rng.uniform(0, 2 * math.pi); sp = rng.uniform(80, 260)
            x = ARCH_X + sp * k * math.cos(ang); y = G - 560 + sp * k * math.sin(ang) + 260 * k * k
            col = [(255, 196, 90), (255, 110, 100), (120, 200, 255), (160, 230, 140)][i % 4]
            c.drawRect(skia.Rect.MakeXYWH(x, y, 10, 6), P(col, 1 - k * 0.6))
    plate_label(c, "QUITTER", heads["q"][0], heads["q"][1] - 80, GREY, 0.9 * (1 - seg(t, SKIP0, SKIP0 + 0.5)))
    plate_label(c, "FINISHER", heads["f"][0], heads["f"][1] - 80, AMBER, 0.95)
    for ts, who, txt in ([] if COVER else TALK):
        if ts < t < ts + 1.6:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.3, ts + 1.6))
            hd = heads[who]
            bx = hd[0] - 110 if who == "q" else clamp(hd[0] + 40, 0, cx + 120)
            by = hd[1] - (150 if who == "q" else 230)
            bubble(c, bx, by, txt, a, "speech", tail=(hd[0], hd[1] - 50), size=30, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    splashes(c, t, 1 - clear_k(t), cx)
    c.restore()
    rain(c, t, 1 - clear_k(t))
    vignette(c, 0.32)
    if SKIP0 - 0.1 < t < SKIP0 + 1.8:                                     # "6 miles later" chip
        a = seg(t, SKIP0 - 0.1, SKIP0 + 0.2) * (1 - seg(t, SKIP0 + 1.4, SKIP0 + 1.8))
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(320, 610, 440, 64), 32, 32)
        c.drawRRect(rr, P((20, 20, 30), 0.85 * a)); c.drawRRect(rr, P(AMBER, a, stroke=3))
        text(c, "6.2 MILES LATER", 540, 654, F_SANS, 30, AMBER, a)
    grain(c, t, 0.03)
    end_text(c, t, 13.6, "He sat down at mile 20.", "She walked the next mile.", "Slow is still forward.", y=1430)


def events():
    ev = [["rain", 0.0, TURN + 0.8]]
    for ts, _, _ in TALK: ev.append(["pop", ts])
    ev += [["thud", 2.5], ["step", 3.0, 0], ["step", 4.0, 0], ["step", 5.0, 0], ["slide", SKIP0], ["sunrise", TURN - 0.4],
           ["land", TURN], ["summit", TURN + 0.6], ["text", 13.6], ["text2", 14.4]]
    return ev


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 1.4, 2.4, 3.6, 4.8, 6.4, 8.0, 9.4, 10.2, 11.0, 12.6, 14.4, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore()
            series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)
        stills(opening, ts, "check/ep21")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs[:40]))
    else:
        finish_v2("Folge21_Finisher", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
