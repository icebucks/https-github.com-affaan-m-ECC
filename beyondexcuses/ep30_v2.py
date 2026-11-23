"""Episode 30 v2 (TikTok: Part 27): ALWAYS LATE vs ALWAYS EARLY – promised by Part 26 ("the friend who's always '5 min away'").
SHAREABLE topic (episodes.md "Teilbar"). Split screen: left his bedroom, right the cinema entrance. Retention-Standard v2.
Frame 0 (climax first): BZZT – his text pops on her phone: "5 min away 🏃" … while he is still in bed.
Time-lapse 7:55 → 8:30: texts keep coming ("almost there!", "parking"), he is still putting on one sock; she waits (WAITING 0 → 35 MIN).
TURN 6.4 s: the cinema sign flips to "STARTED" – she goes in alone, the door closes.
Second turn: he finally runs up and bangs on the closed door.
Loop: he ends where she stood at frame 0, checking his watch."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 27                     # TikTok part number (internal episode 30)
TURN = 6.4
LAPSE0, LAPSE1 = 2.2, 5.2      # 7:55 -> 8:30
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
SPLIT = 168                    # world x of the split line
BED = (-50, 120)
HX = 30                        # him in bed
SX = 352                       # her at the cinema
DOOR = (192, 262)
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Movie at 8:00.\nWho actually makes it?"
CTA = "Part 28 next:\nthe one on his phone at dinner"
END_TXT = "Late isn't cool. It's rude."
TALK = [(1.25, "s", "Where are you?"), (4.9, "h", "Almost there!"), (8.5, "h", "Wait for me!")]
TEXTS = [(0.0, "5 min away!"), (3.0, "almost there!"), (4.3, "parking...")]


def clock(t):
    m = 55 + int(35 * seg(t, LAPSE0, LAPSE1)) + (int(10 * seg(t, LAPSE1, 8.2)) if t > LAPSE1 else 0)
    h, mm = 7 + m // 60, m % 60
    return f"{h}:{mm:02d} PM"


def waited(t): return int(35 * seg(t, LAPSE0, LAPSE1)) if t < TURN else 35


# ------------------------------------------------------------------ characters
def late(t):
    if t < 4.6:                                                            # in bed, scrolling (sits up under the blanket)
        p = dict(sit(t), lean=-14, head=-4, arm_f=70, elb_f=120 + 6 * math.sin(t * 9), arm_b=20, elb_b=40)
        return dict(x=HX, y=G - 92, p=p, f=1, hip=True, room="L")
    if t < 6.6:                                                            # sits on the bed edge, ONE sock on (slow)
        p = dict(sit(t), lean=30, head=24, arm_f=40, elb_f=20, arm_b=30, elb_b=20)
        return dict(x=HX + 40, y=G - 70, p=p, f=1, hip=True, room="L")
    if t < 7.6:                                                            # runs out of the room
        return dict(x=lerp(HX + 40, SPLIT - 10, seg(t, 6.6, 7.6)), y=G, p=run(t * 14), f=1, hip=False, room="L")
    if t < 8.4:                                                            # runs up to the cinema
        return dict(x=lerp(SPLIT + 10, DOOR[1] + 30, seg(t, 7.6, 8.4)), y=G, p=run(t * 14), f=1, hip=False, room="R")
    if t < 10.6:                                                           # bangs on the closed door
        sw = math.sin((t - 8.4) * 16)
        p = dict(stand(), lean=8, head=-6, arm_f=90 + 25 * sw, elb_f=30, arm_b=10, elb_b=20)
        return dict(x=DOOR[1] + 30, y=G, p=p, f=-1, hip=False, room="R")
    k = seg(t, 10.6, 11.0)                                                 # gives up, checks his watch (loop: where she stood)
    p = mix(stand(), dict(stand(), arm_f=75, elb_f=95, head=12), seg(t, 11.6, 12.0))
    return dict(x=lerp(DOOR[1] + 30, SX, k), y=G, p=p if t > 11.0 else walk(t * 9), f=-1, hip=False, room="R")


def early(t):
    if t < TURN:
        p = mix(stand(), dict(stand(), arm_f=75, elb_f=95, head=12), 1 if t < 0.5 else 0.5 + 0.5 * math.sin(t * 2))   # phone / watch
        if LAPSE0 < t < LAPSE1: p = dict(p, lean=4 * math.sin(t * 5))  # taps her foot
        return dict(x=SX, p=p, f=-1, show=1.0)
    k = seg(t, TURN, TURN + 0.9)                                           # walks in, door closes behind her
    return dict(x=lerp(SX, (DOOR[0] + DOOR[1]) / 2, k), p=walk(t * 8), f=-1, show=1 - seg(t, TURN + 0.7, TURN + 1.0))


# ------------------------------------------------------------------ world
def bedroom(c, t):
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, SPLIT, G), P((70, 70, 110)))
    c.drawRect(skia.Rect.MakeLTRB(-40, G - 330, 60, G - 230), P((30, 30, 60))); c.drawRect(skia.Rect.MakeLTRB(-40, G - 330, 60, G - 230), P((150, 120, 90), stroke=6))   # window (dark)
    c.drawCircle(30, G - 300, 12, P((240, 240, 210)))
    c.drawRect(skia.Rect.MakeLTRB(-300, G, SPLIT, G + 500), P((110, 90, 80)))
    x0, x1 = BED
    c.drawRect(skia.Rect.MakeLTRB(x0, G - 70, x1, G - 30), P((230, 230, 240))); c.drawRect(skia.Rect.MakeLTRB(x0, G - 70, x1, G - 30), P(INK, stroke=3))
    c.drawLine(x0, G - 30, x0, G, P(INK, stroke=6)); c.drawLine(x1, G - 30, x1, G, P(INK, stroke=6))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 6, G - 130, x0 + 6, G), P((120, 90, 70)))


def blanket(c, t):
    if t < 4.6:
        x0, x1 = BED
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(HX - 20, G - 86, x1 + 4, G - 50), 12, 12), P((90, 130, 200)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(HX - 20, G - 86, x1 + 4, G - 50), 12, 12), P(INK, stroke=3))


def cinema(c, t):
    eve = 1.0
    c.drawRect(skia.Rect.MakeLTRB(SPLIT, G - 900, 700, G), P((40, 36, 60)))
    c.drawRect(skia.Rect.MakeLTRB(SPLIT + 20, G - 380, 440, G), P((120, 50, 60))); c.drawRect(skia.Rect.MakeLTRB(SPLIT + 20, G - 380, 440, G), P(INK, stroke=4))
    started = t >= TURN
    sign = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(DOOR[0] - 20, G - 300, DOOR[1] - DOOR[0] + 40, 56), 8, 8)
    c.drawRRect(sign, P((20, 20, 30))); c.drawRRect(sign, P((255, 200, 120), stroke=3))
    for i in range(9): c.drawCircle(DOOR[0] - 14 + i * 13, G - 306, 4, P((255, 220, 140), 0.5 + 0.5 * ((i + int(t * 6)) % 2)))
    text(c, "STARTED" if started else "8:00 PM", (DOOR[0] + DOOR[1]) / 2, G - 262, F_CAP, 26, (255, 110, 100) if started else (255, 220, 140), 1.0)
    op = seg(t, TURN, TURN + 0.3) * (1 - seg(t, TURN + 0.8, TURN + 1.1))   # door opens for her, then closes
    c.drawRect(skia.Rect.MakeLTRB(DOOR[0], G - 230, DOOR[1], G), P((255, 220, 150) if op > 0 else (60, 40, 40)))
    dw = (DOOR[1] - DOOR[0]) * (1 - 0.8 * op)
    c.drawRect(skia.Rect.MakeLTRB(DOOR[0], G - 230, DOOR[0] + dw, G), P((150, 70, 60))); c.drawRect(skia.Rect.MakeLTRB(DOOR[0], G - 230, DOOR[1], G), P(INK, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(SPLIT, G, 700, G + 500), P((90, 90, 100)))


def world(c, t):
    bedroom(c, t)
    cinema(c, t)
    c.drawRect(skia.Rect.MakeLTRB(SPLIT - 4, G - 900, SPLIT + 4, G + 500), P((20, 20, 30)))


def to_screen(p): return (470 + (p[0] - 160) * K, 1440 + (p[1] - G) * K)


def frame(c, t):
    c.save(); c.translate(470, 1440); c.scale(K, K); c.translate(-160, -G)
    world(c, t)
    lo = (1, -0.6)
    h = late(t)
    jh = figure(c, h["x"], h["y"], h["p"], s=S, facing=h["f"], body=H_BODY, rim=((210, 220, 255), 0.5), light=lo,
                mode="hip" if h["hip"] else "feet")
    if t < 4.6:                                                            # his phone glow in bed
        px, py = jh["hand_f"]
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px - 6, py - 26, 14, 30), 3, 3), P((30, 30, 40)))
        c.drawCircle(px, py - 12, 40, P((120, 190, 255), 0.3, blur=14))
    blanket(c, t)
    e = early(t)
    if e["show"] > 0:
        c.saveLayerAlpha(None, int(255 * e["show"]))
        je = figure(c, e["x"], G, e["p"], s=S, facing=e["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo)
        c.restore()
    else:
        je = {"head": (SX, G - 200)}
    c.restore()
    heads = {"h": to_screen(jh["head"]), "s": to_screen(je["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "ALWAYS LATE", GREY, size=28, a=na)
        chip(c, 760, 720, "ALWAYS EARLY", AMBER, size=28, a=na)
    vignette(c, 0.25)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    chip(c, 470, 640, clock(t) + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=34 + 16 * lapse)
    chip(c, 760, 545, f"WAITING {waited(t)} MIN", AMBER, size=34, pop=1 + 0.3 * (1 - seg(t, TURN, TURN + 0.25)) * (t > TURN))
    chip(c, 250, 545, "STILL IN BED" if t < 4.6 else ("ONE SOCK ON" if t < 6.6 else "RUNNING"), GREY, size=34)
    for t0, msg in TEXTS:                                                  # his texts pop on her side
        if t0 <= t < t0 + 1.6:
            a = seg(t, t0, t0 + 0.08) * (1 - seg(t, t0 + 1.3, t0 + 1.6)); pop = 1 + 0.25 * (1 - seg(t, t0, t0 + 0.2))
            chip(c, 700, 1200, msg, (120, 190, 255), size=38, a=a, pop=pop)
    for ts, who, txt in TALK:
        if ts < t < ts + 1.35:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.15, ts + 1.35))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 200 if who == "h" else hx_ - 200, 300, 640)
            bubble(c, bx_, 722, txt, a, "speech", tail=(hx_ + (40 if who == "h" else -40), hy_ - 50), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", t0, "pop-medium-in", -6] for t0, _ in TEXTS]
    ev += [["sfx", LAPSE0, "time-clock-fast", -10], ["sfx", LAPSE0, "riser-2s-soft", -12]]
    ev += [["sfx", TURN, "tone-ding-high", -8], ["thud", TURN + 1.0], ["summit", TURN + 0.2], ["thud", 8.5], ["thud", 8.9], ["thud", 9.3],
           ["sfx", 12.0, "pop-medium-in", -8], ["text", END_T0]]
    return ev


if __name__ == "__main__":
    main("Folge30_Early_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep30_v2",
         [0.0, 0.3, 1.3, 3.2, 4.9, 6.6, 7.3, 8.0, 8.9, 10.0, 11.5, 12.4])
