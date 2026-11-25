"""Episode 34 v2 (TikTok: Part 31): ALL-OUT START vs STEADY PACE – promised by Part 30 ("the all-out sprint start").
Sport topic (+ shareable: the friend who always sprints the first 200 m). Retention-Standard v2.
Frame 0 (climax first): BANG – start gun flash, he explodes off the line, she starts at an easy jog.
Time-lapse KM 1 → KM 4: his lead melts (+180 M → +10 M), he slows, gasps; she keeps the same rhythm (pace chip stays 5:30).
TURN 6.4 s: KM 4 – she passes him; he stops, hands on knees.
Second turn: she crosses the finish line; he walks in far behind.
Loop: next race – both at the start line again, BANG (= frame 0)."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 31                     # TikTok part number (internal episode 34)
TURN = 6.4
LAPSE0, LAPSE1 = 2.2, 5.2      # KM 1 -> KM 4
END_T0 = 9.6
LOOP0 = 11.55                  # cut back to a start line
G = 1300
S = 1.5
K = 2.0
SXS = 430                      # her screen x (camera follows her)
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Same race. 5 km.\nWho finishes first?"
CTA = "Part 32 next:\nthe 'I'll text back' friend"
END_TXT = "Start slow. Finish strong."
TALK = [(0.95, "h", "Too slow!"), (6.75, "h", "My legs... gone."), (8.3, "s", "Pace beats panic.")]


def km(t): return min(5, 1 + int(3 * seg(t, LAPSE0, LAPSE1)) + (1 if t > 8.0 else 0)) if t > 0.9 else 0


def rel(t):
    """his position relative to her (world units, + = ahead)"""
    if t < LAPSE0: return 190 * seg(t, 0.0, 2.0)
    if t < TURN: return lerp(190, 30, seg(t, LAPSE0, LAPSE1)) - 30 * seg(t, LAPSE1, TURN)
    if t < 8.4: return -260 * seg(t, TURN, 8.4)
    return -260 - 60 * seg(t, 8.4, 10.5)


def lead_txt(t):
    r = rel(t) * 1.0
    return f"LEAD +{int(r)} M" if r > 0 else "PASSED"


def scroll(t):
    """how far the world has moved (her running speed; faster during the time-lapse)"""
    return 260 * t + 900 * seg(t, LAPSE0, LAPSE1) - (0 if t < 8.4 else 220 * (t - 8.4))   # she slows after the finish


# ------------------------------------------------------------------ characters
def crouch_start(): return dict(lean=36, head=-18, arm_f=-30, elb_f=60, arm_b=50, elb_b=70, leg_f=60, leg_b=-20, knee_f=80, knee_b=30)


KNEES = dict(lean=55, head=14, arm_f=70, elb_f=16, arm_b=62, elb_b=16, leg_f=14, leg_b=-8, knee_f=26, knee_b=22)


def him(t):
    if t >= LOOP0: return dict(p=crouch_start() if t > LOOP0 + 0.2 else run(t * 15), f=1)
    if t < 0.15: return dict(p=crouch_start(), f=1)
    if t < LAPSE0: return dict(p=run(t * 17), f=1)                         # sprint
    if t < LAPSE1:                                                         # slows down, heavier
        k = seg(t, LAPSE0, LAPSE1)
        p = run(t * lerp(17, 9, k)); p["lean"] = lerp(16, 26, k); p["head"] = lerp(-10, 14, k)
        return dict(p=p, f=1)
    if t < TURN:                                                           # walks, gasping
        p = walk(t * 6); p["lean"] = 18; p["head"] = 16
        return dict(p=p, f=1)
    if t < 8.6: return dict(p=mix(walk(t * 6), KNEES, seg(t, TURN, TURN + 0.3)), f=1)   # hands on knees
    p = walk(t * 5); p["lean"] = 14; p["head"] = 12                         # walks in, far behind
    return dict(p=p, f=1)


def her(t):
    if t >= LOOP0: return dict(p=crouch_start() if t > LOOP0 + 0.2 else run(t * 12), f=1)
    if t < 0.15: return dict(p=crouch_start(), f=1)
    if t < 8.4:
        p = run(t * 12); p["lean"] = 10; p["head"] = -6                      # same rhythm all the way
        return dict(p=p, f=1)
    if t < 9.6: return dict(p=mix(run(t * 12), cheer(t), seg(t, 8.4, 8.7)), f=1)   # finish line
    return dict(p=mix(cheer(t), hands_on_hips(), seg(t, 9.6, 10.0)), f=lerp(1, -1, seg(t, 9.9, 10.2)))   # turns, waits for him


# ------------------------------------------------------------------ world
def world(c, t):
    sc = scroll(t) if t < LOOP0 else 0.0
    c.drawRect(skia.Rect.MakeLTRB(-2000, G - 900, 3000, G), P((150, 200, 235)))         # sky
    c.drawCircle(700 - 0.05 * sc, G - 620, 60, P((255, 240, 200)))
    for i in range(-6, 30):                                                # city skyline (slow parallax)
        bx = i * 120 - (0.25 * sc) % 120 * 0 - 0.25 * sc + 120 * int(0.25 * sc / 120)
        h = 140 + 90 * ((i * 37) % 5)
        c.drawRect(skia.Rect.MakeLTRB(i * 120 - (0.25 * sc) % 120 - 400, G - 160 - h, i * 120 - (0.25 * sc) % 120 - 310, G - 160), P((120, 150, 180)))
    for i in range(-8, 30):                                                # trees (mid parallax)
        tx = i * 160 - (0.6 * sc) % 160 - 600
        c.drawLine(tx, G - 60, tx, G - 140, P((110, 80, 60), stroke=8))
        c.drawCircle(tx, G - 160, 40, P((90, 150, 90)))
    c.drawRect(skia.Rect.MakeLTRB(-2000, G - 60, 3000, G + 500), P((90, 95, 105)))       # road
    for i in range(-10, 40):                                               # lane dashes (full speed)
        lx = i * 120 - sc % 120 - 800
        c.drawLine(lx, G + 60, lx + 60, G + 60, P((240, 240, 240), stroke=6))
    c.drawRect(skia.Rect.MakeLTRB(-2000, G + 140, 3000, G + 500), P((120, 170, 100)))
    # start line (frame 0 and loop)
    if t < 1.2 or t >= LOOP0:
        x0 = 30 - (sc if t < LOOP0 else 0)
        c.drawRect(skia.Rect.MakeLTRB(x0 - 4, G - 60, x0 + 4, G + 140), P((255, 255, 255)))
        c.drawLine(x0 - 190, G - 60, x0 - 190, G - 330, P((60, 60, 70), stroke=8)); c.drawLine(x0 + 110, G - 60, x0 + 110, G - 330, P((60, 60, 70), stroke=8))
        c.drawRect(skia.Rect.MakeLTRB(x0 - 190, G - 330, x0 + 110, G - 280), P((40, 120, 200)))
        text(c, "START  5K", x0 - 40, G - 293, F_CAP, 30, (255, 255, 255))     # text stays left of TikTok's right buttons
    # finish banner arrives at 8.4 (her position = world 0)
    if 7.2 < t < LOOP0:
        fx = 1200 * (1 - seg(t, 7.2, 8.4)) + 8 - (0 if t < 8.4 else 220 * (t - 8.4))
        c.drawLine(fx, G - 60, fx, G - 360, P((60, 60, 70), stroke=8)); c.drawLine(fx + 320, G - 60, fx + 320, G - 360, P((60, 60, 70), stroke=8))
        c.drawRect(skia.Rect.MakeLTRB(fx, G - 360, fx + 320, G - 300), P((220, 70, 70)))
        text(c, "FINISH", fx + 160, G - 315, F_CAP, 36, (255, 255, 255))
        c.drawRect(skia.Rect.MakeLTRB(fx - 3, G - 60, fx + 3, G + 140), P((255, 255, 255)))
    # KM 4 sign at the turn
    if 5.6 < t < 7.6:
        kx = 700 * (1 - seg(t, 5.6, 6.4)) - 260 * max(0, t - 6.4)
        c.drawLine(kx, G - 60, kx, G - 200, P((60, 60, 70), stroke=6))
        c.drawRect(skia.Rect.MakeLTRB(kx - 40, G - 240, kx + 40, G - 190), P((250, 200, 60)))
        text(c, "KM 4", kx, G - 205, F_CAP, 26, INK)


def confetti(c, t):
    if 8.4 < t < 10.4:
        k = t - 8.4
        for i in range(40):
            x = SXS + 300 * math.sin(i * 2.1) + 30 * math.sin(k * 3 + i)
            y = 700 + 500 * ((k * 0.6 + i * 0.037) % 1.0)
            col = [(255, 200, 60), (90, 200, 255), (255, 110, 100), (140, 230, 120)][i % 4]
            c.drawRect(skia.Rect.MakeXYWH(x, y, 10, 16), P(col, 0.9))


def frame(c, t):
    hx = rel(t) if t < LOOP0 else -110
    sx = 0.0 if t < LOOP0 else 40
    c.save(); c.translate(SXS, 1500); c.scale(K, K); c.translate(0, -G)
    world(c, t)
    lo = (1, -0.6)
    h = him(t); e = her(t)
    if t >= LOOP0: hx, sx = 20, 140
    elif t < 0.15: hx, sx = 20, 140 - 140                                 # both on the line
    if t < LOOP0 and t >= 0.15: sx = 0.0
    if t < 0.15: hx, sx = 20, 140
    if 0.15 <= t < 0.8: sx = lerp(140, 0, seg(t, 0.15, 0.8)); hx = rel(t) + sx
    jh = figure(c, hx, G, h["p"], s=S, facing=h["f"], body=H_BODY, rim=((210, 220, 255), 0.5), light=lo)
    je = figure(c, sx, G, e["p"], s=S, facing=e["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo)
    c.restore()
    to_s = lambda p: (SXS + p[0] * K, 1500 + (p[1] - G) * K)
    heads = {"h": to_s(jh["head"]), "s": to_s(je["head"])}
    confetti(c, t)
    fl = (1 - seg(t, 0.0, 0.3)) if t < 0.3 else (seg(t, 12.15, 12.46) if t > 12.1 else 0)   # start-gun flash (frame 0 = loop end)
    if fl > 0: c.drawRect(skia.Rect.MakeLTRB(0, 0, 1080, 1920), P((255, 255, 255), 0.45 * fl))
    if LOOP0 - 0.15 < t < LOOP0 + 0.15:                                     # whip cut to the next race
        c.drawRect(skia.Rect.MakeLTRB(0, 0, 1080, 1920), P((255, 255, 255), 0.8 * (1 - abs(t - LOOP0) / 0.15)))
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "ALL-OUT START", GREY, size=28, a=na)
        chip(c, 790, 720, "STEADY PACE", AMBER, size=28, a=na)
    vignette(c, 0.2)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    if 0.3 < t < 9.6:
        chip(c, 540, 640, (f"KM {km(t)}" if km(t) < 5 else "FINISH") + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=34 + 16 * lapse)
        chip(c, 250, 545, lead_txt(t), GREY if rel(t) > 0 else RED, size=34, pop=1 + 0.3 * (1 - seg(t, TURN, TURN + 0.25)) * (TURN < t < TURN + 0.5))
        chip(c, 790, 545, "PACE 5:30 /KM", AMBER, size=34)
    for ts, who, txt in TALK:
        if ts < t < ts + 1.3:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.1, ts + 1.3))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + (-200 if hx_ > 600 else 200), 320, 700)
            bubble(c, bx_, 860, txt, a, "speech", tail=(hx_, hy_ - 60), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", 0.0, "cinematic-slam-big", -8]]                         # BANG
    ev += [["sfx", LAPSE0, "time-clock-fast", -10], ["sfx", LAPSE0, "riser-2s-soft", -12]]
    ev += [["sfx", TURN, "whoosh-fast-medium", -8], ["sfx", 8.4, "celebration-confetti", -10], ["sfx", 8.45, "celebration-applause-small", -14],
           ["sfx", LOOP0, "whoosh-medium-soft", -8], ["sfx", 12.42, "cinematic-slam-big", -12], ["text", END_T0]]
    return ev


if __name__ == "__main__":
    main("Folge34_Pace_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep34_v2",
         [0.0, 0.4, 1.3, 2.9, 4.6, 5.8, 6.6, 7.4, 8.6, 9.4, 10.6, 11.8, 12.3, 12.45])
