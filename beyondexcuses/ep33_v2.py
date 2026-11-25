"""Episode 33 v2 (TikTok: Part 30): DISHES TOMORROW vs DISHES NOW – promised by Part 29 ("the roommate and the dishes").
SHAREABLE topic (roommates, episodes.md "Teilbar"). Retention-Standard v2.
Frame 0 (climax first): CRASH – a plate slides off his tower of dirty dishes and smashes.
Time-lapse DAY 1 → DAY 7: his sink tower grows (DIRTY 3 → 41), flies circle; she washes her one plate each evening (sink stays empty).
TURN 6.4 s: DAY 7 – he opens the cupboard for a plate: EMPTY. Every plate he owns is in the tower.
Second turn: she hands him a sponge; he starts washing.
Loop: he lifts a plate off the top – it slips – CRASH (= frame 0)."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 30                     # TikTok part number (internal episode 33)
TURN = 6.4
LAPSE0, LAPSE1 = 2.2, 5.2      # DAY 1 -> DAY 7
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
CAMX = 190
COUNTER_Y = G - 120            # counter top
HSINK = (60, 150)              # his sink (x range)
SSINK = (230, 320)             # her sink
HX, SX = 18, 345                # standing positions (behind the counter)
CUP = (-10, 60)                # his cupboard above the counter (x range)
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Same kitchen. 7 days.\nWho runs out first?"
CTA = "Part 31 next:\nthe all-out sprint start"
END_TXT = "Two minutes now. Or two hours later."
TALK = [(1.0, "h", "I'll do it tomorrow."), (6.75, "h", "Wait... no plates?"), (8.3, "s", "Two minutes. Go.")]


def day(t): return 1 + int(6 * seg(t, LAPSE0, LAPSE1))
def dirty(t):
    if t < TURN + 1.6: return 3 + int(38 * seg(t, LAPSE0, LAPSE1))
    return max(0, 41 - int(8 * seg(t, 8.6, 11.4)))                       # he starts washing


def tower(t):
    """number of plates in his tower (visual)"""
    return 3 + int(13 * seg(t, LAPSE0, LAPSE1)) - (int(3 * seg(t, 8.6, 11.4)) if t > 8.6 else 0)


# ------------------------------------------------------------------ characters
def him(t):
    if t < LAPSE0:                                                         # walks past the sink, drops another plate on top, shrugs
        k = seg(t, 0.3, 1.6)
        p = mix(dict(stand(), arm_f=70, elb_f=30, arm_b=6, elb_b=10), shrug(1.0), seg(t, 1.0, 1.4))
        return dict(x=HX, p=p, f=1)
    if t < LAPSE1:                                                         # time-lapse: on the couch side with his phone, then back
        sw = math.sin(t * 10)
        p = dict(stand(), lean=4, head=16, arm_f=62, elb_f=118, arm_b=30, elb_b=100)
        return dict(x=HX - 30 + 8 * sw, p=p, f=1)
    if t < TURN:                                                           # reaches up to his cupboard
        k = seg(t, LAPSE1, 5.9)
        p = mix(dict(stand(), lean=4, head=16, arm_f=62, elb_f=118, arm_b=30, elb_b=100), dict(stand(), lean=-6, head=-24, arm_f=150, elb_f=20, arm_b=6, elb_b=10), k)
        return dict(x=lerp(HX - 30, 25, k), p=p, f=1)
    if t < 7.9:                                                            # empty cupboard: stares, then turns to the tower
        p = dict(stand(), lean=-6, head=-24, arm_f=150, elb_f=20, arm_b=6, elb_b=10) if t < 7.0 else shrug(1.0)
        return dict(x=25, p=p, f=1)
    if t < 8.6:                                                            # takes the sponge from her (she reaches over)
        return dict(x=lerp(25, HX, seg(t, 7.9, 8.4)), p=dict(stand(), arm_f=60, elb_f=40, arm_b=6, elb_b=10), f=1)
    if t < 11.6:                                                           # washes: scrubbing a plate over the sink
        sc = math.sin(t * 14)
        p = dict(stand(), lean=14, head=18, arm_f=55 + 6 * sc, elb_f=55 + 10 * sc, arm_b=45, elb_b=60)
        return dict(x=HX, p=p, f=1)
    k = seg(t, 11.6, 12.0)                                                 # loop: lifts the top plate – it slips
    p = mix(dict(stand(), lean=14, head=18, arm_f=55, elb_f=55, arm_b=45, elb_b=60), dict(stand(), lean=-4, head=-14, arm_f=120, elb_f=40, arm_b=40, elb_b=40), k)
    return dict(x=HX, p=p, f=1)


def her(t):
    if t < 7.6:                                                            # washes her one plate, dries it, puts it on the rack
        sc = math.sin(t * (16 if LAPSE0 < t < LAPSE1 else 9))
        p = dict(stand(), lean=12, head=16, arm_f=55 + 6 * sc, elb_f=55 + 10 * sc, arm_b=45, elb_b=60)
        if TURN < t: p = mix(p, dict(stand(), lean=2, head=-4, arm_f=20, elb_f=60, arm_b=6, elb_b=10), seg(t, TURN, TURN + 0.4))
        return dict(x=SX, p=p, f=-1)
    if t < 8.6:                                                            # walks over and hands him the sponge
        k = seg(t, 7.6, 7.95)
        p = offer() if t > 7.9 else walk(t * 9)
        return dict(x=lerp(SX, 255, k), p=p, f=-1)                          # tosses the sponge over
    if t < 9.8:
        return dict(x=255, p=hands_on_hips(), f=-1)
    k = seg(t, 9.8, 10.4)                                                  # back to her side, arms crossed
    return dict(x=lerp(255, SX, k), p=walk(t * 9) if k < 1 else arms_crossed(-6), f=lerp(-1, 1, seg(t, 9.8, 10.05)) if t < 10.3 else lerp(1, -1, seg(t, 10.3, 10.6)))


# ------------------------------------------------------------------ world
def plate(c, x, y, a=1.0, dirty_=True, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.drawOval(skia.Rect.MakeLTRB(-22, -5, 22, 5), P((240, 238, 230), a))
    if dirty_:
        c.drawCircle(-8, -1, 4, P((150, 110, 60), 0.8 * a)); c.drawCircle(7, 1, 3, P((120, 150, 70), 0.8 * a))
    c.drawOval(skia.Rect.MakeLTRB(-22, -5, 22, 5), P(INK, a, stroke=1.5))
    c.restore()


def kitchen(c, t):
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, 700, G), P((230, 220, 196)))
    for i in range(-6, 14):                                                # tiles
        c.drawLine(i * 50, G - 330, i * 50, COUNTER_Y, P((205, 196, 172), stroke=2))
    for j in range(5): c.drawLine(-300, G - 330 + j * 42, 700, G - 330 + j * 42, P((205, 196, 172), stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(150, G - 420, 240, G - 300), P((150, 200, 240)))   # window
    c.drawRect(skia.Rect.MakeLTRB(150, G - 420, 240, G - 300), P((120, 90, 60), stroke=5))
    # cupboards
    for x0, x1 in (CUP, (300, 370)):
        c.drawRect(skia.Rect.MakeLTRB(x0, G - 440, x1, G - 340), P((170, 120, 80)))
        c.drawRect(skia.Rect.MakeLTRB(x0, G - 440, x1, G - 340), P(INK, stroke=3))
    op = seg(t, 5.9, 6.2) * (1 - seg(t, 7.6, 7.9))                        # his cupboard opens: EMPTY
    if op > 0:
        c.drawRect(skia.Rect.MakeLTRB(CUP[0] + 4, G - 436, CUP[1] - 4, G - 344), P((70, 50, 40)))
        c.drawRect(skia.Rect.MakeLTRB(CUP[0], G - 440, CUP[0] + (CUP[1] - CUP[0]) * (1 - 0.85 * op), G - 340), P((190, 140, 95)))
        c.drawLine(CUP[0] + 6, G - 390, CUP[1] - 6, G - 390, P((120, 90, 60), stroke=3))
    for i in range(3): plate(c, 335, G - 352 - i * 7, dirty_=False)        # her cupboard top: clean stack visible on the shelf edge
    c.drawRect(skia.Rect.MakeLTRB(-300, G, 700, G + 500), P((170, 150, 120)))


def counter(c, t):
    c.drawRect(skia.Rect.MakeLTRB(-300, COUNTER_Y, 700, G + 500), P((120, 140, 160)))
    c.drawRect(skia.Rect.MakeLTRB(-300, COUNTER_Y - 10, 700, COUNTER_Y + 4), P((235, 235, 240)))
    c.drawRect(skia.Rect.MakeLTRB(-300, COUNTER_Y - 10, 700, COUNTER_Y + 4), P(INK, stroke=2))
    for x0, x1 in (HSINK, SSINK):
        c.drawRect(skia.Rect.MakeLTRB(x0, COUNTER_Y - 10, x1, COUNTER_Y + 2), P((180, 190, 200)))
        c.drawLine((x0 + x1) / 2, COUNTER_Y - 10, (x0 + x1) / 2, COUNTER_Y - 40, P((150, 155, 165), stroke=5))
        c.drawLine((x0 + x1) / 2, COUNTER_Y - 40, (x0 + x1) / 2 + 16, COUNTER_Y - 40, P((150, 155, 165), stroke=5))
    # her drying rack with 1 clean plate
    c.drawRect(skia.Rect.MakeLTRB(170, COUNTER_Y - 40, 215, COUNTER_Y - 10), P((200, 200, 210), stroke=3))
    plate(c, 192, COUNTER_Y - 26, dirty_=False, rot=80)


def dish_tower(c, t):
    n = tower(t)
    cx = (HSINK[0] + HSINK[1]) / 2
    wob = 2 * math.sin(t * 3) * seg(t, LAPSE0, LAPSE1)
    for i in range(n):
        plate(c, cx + wob * i / 6 + 3 * math.sin(i * 1.7), COUNTER_Y - 14 - i * 9)
    for i in range(int(4 * seg(t, 3.0, 5.0))):                             # flies
        a = t * 4 + i * 1.6
        c.drawCircle(cx + 40 * math.cos(a), COUNTER_Y - 30 - n * 9 + 16 * math.sin(a * 1.3), 3, P(INK))
    # falling plate: frame 0 and loop
    for t0, x0 in ((-0.15, cx + 10), (12.0, cx + 10)):
        k = (t - t0) / 0.5
        if 0 <= k <= 1.2:
            top = COUNTER_Y - 14 - (n + 1) * 9
            if k < 1:
                plate(c, x0 + 60 * k, top + 120 * k * k, rot=200 * k)
            else:
                for j in range(5):                                       # shards
                    c.drawLine(x0 + 60 + j * 8 - 16, COUNTER_Y - 2, x0 + 60 + j * 8 - 10 + 6 * (j % 2), COUNTER_Y - 12, P((240, 238, 230), stroke=3))


def to_screen(p): return (470 + (p[0] - CAMX) * K, 1610 + (p[1] - G) * K)


def frame(c, t):
    c.save(); c.translate(470, 1610); c.scale(K, K); c.translate(-CAMX, -G)
    kitchen(c, t)
    lo = (1, -0.6)
    e = her(t)
    je = figure(c, e["x"], G, e["p"], s=S, facing=e["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo)
    h = him(t)
    jh = figure(c, h["x"], G, h["p"], s=S, facing=h["f"], body=H_BODY, rim=((210, 220, 255), 0.5), light=lo)
    counter(c, t)
    dish_tower(c, t)
    if LAPSE0 < t < LAPSE1:                                                # his phone
        px, py = jh["hand_f"]
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px - 6, py - 22, 12, 24), 3, 3), P((30, 30, 40)))
    if 7.9 < t < 8.6:                                                      # the sponge flies from her hand to his
        k = seg(t, 7.95, 8.45)
        (ax, ay), (bx, by) = je["hand_f"], jh["hand_f"]
        sx_, sy_ = lerp(ax, bx, k), lerp(ay, by, k) - 50 * math.sin(math.pi * k)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(sx_ - 8, sy_ - 6, 16, 10), 2, 2), P((250, 220, 60)))
    if 8.6 <= t < 11.6:
        sx_, sy_ = jh["hand_f"]
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(sx_ - 8, sy_ - 6, 16, 10), 2, 2), P((250, 220, 60)))
        for i in range(4):                                                 # bubbles
            c.drawCircle(sx_ + 14 * math.sin(t * 5 + i), sy_ - 10 - ((t * 40 + i * 12) % 40), 3, P((255, 255, 255), 0.8))
    c.restore()
    heads = {"h": to_screen(jh["head"]), "s": to_screen(je["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "DISHES TOMORROW", GREY, size=28, a=na)
        chip(c, 790, 720, "DISHES NOW", AMBER, size=28, a=na)
    vignette(c, 0.22)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    if t < 9.6:
        chip(c, 540, 640, f"DAY {day(t)}" + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=34 + 16 * lapse)
        chip(c, 250, 545, f"DIRTY {dirty(t)}", GREY, size=34)
        chip(c, 790, 545, "DIRTY 0", AMBER, size=34)
    if TURN <= t < 8.0:
        a = seg(t, TURN, TURN + 0.1) * (1 - seg(t, 7.7, 8.0)); pop = 1 + 0.3 * (1 - seg(t, TURN, TURN + 0.25))
        chip(c, 250, 800, "CLEAN PLATES: 0", RED, size=40, a=a, pop=pop)
    for ts, who, txt in TALK:
        if ts < t < ts + 1.3:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.1, ts + 1.3))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 230 if who == "h" else hx_ - 230, 320, 700)
            bubble(c, bx_, 880, txt, a, "speech", tail=(hx_ + (40 if who == "h" else -40), hy_ - 50), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", 0.3, "cinematic-slam-big", -10]]                        # CRASH (frame 0 plate lands at 0.35 s)
    ev += [["sfx", LAPSE0, "time-clock-fast", -10], ["sfx", LAPSE0, "data-countup-long", -14], ["sfx", LAPSE0, "riser-2s-soft", -12]]
    ev += [["sfx", TURN, "tone-ding-high", -8], ["thud", 7.0], ["sfx", 8.2, "pop-medium-in", -8],
           ["sfx", 12.45, "cinematic-slam-big", -12], ["text", END_T0]]
    return ev


if __name__ == "__main__":
    main("Folge33_Dishes_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep33_v2",
         [0.0, 0.3, 1.3, 2.9, 4.6, 5.9, 6.6, 7.4, 8.1, 9.0, 10.3, 11.8, 12.2, 12.45])
