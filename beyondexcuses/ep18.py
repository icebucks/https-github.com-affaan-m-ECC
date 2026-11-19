"""Episode 18 (TikTok: Part 15): EXCUSE CLOCK vs EARLY RISER – promised by the Part 14 cliffhanger ("the one who hits snooze").
Two bedrooms side by side at dawn (cut-away), cold blue night inside → warm sunrise shafts through the windows (new place + light).
6:00 – both alarms ring. She gets up at once and leaves for a run (seen passing his window). He hits snooze three times
("5 more minutes…", "Too cold…", "I'll start Monday."). The clock jumps to 7:45: he shoots up – she walks back in from her run."""
import sys, math
import numpy as np
from lib import *

T_END = 17.2
OFF = 0.3
SHOWN = 15                     # TikTok part number (internal episode 18)
G = 1240
SC = 1.25
DY = 0
S = 1.0
TURN = 10.0                    # 07:45 – he wakes up for real
RINGS = [0.7, 3.9, 6.9]        # the alarm rings (06:00, 06:09, 06:18)
SNOOZE = [r + 0.6 for r in RINGS]
TALK = [(SNOOZE[0] + 0.2, "e", "5 more minutes..."), (SNOOZE[1] + 0.2, "e", "Too cold..."), (SNOOZE[2] + 0.2, "e", "I'll start Monday."),
        (TURN + 0.3, "e", "7:45?! WHAT?!"), (TURN + 2.0, "r", "5 km done. Morning!")]
E_BODY = (196, 202, 216)
R_BODY = (255, 226, 178)
HOOK = "Snooze. Snooze. Snooze.\nShe ran 5 km meanwhile."
FOCUS = (330, 1080)
CTA = "Part 16 tomorrow:\nthe one who won't ask for help"
WALL = 470                     # wall between the rooms (his room left, hers right)
CLOCK = (395, G - 120)         # his alarm clock on the night stand
CLOCK_R = (560, G - 120)       # hers


def light(t): return seg(t, 2.0, TURN + 1.0)


def clock_text(t):
    if t >= TURN: return "07:45", (255, 90, 80)
    if t >= RINGS[2]: return "06:18", (255, 200, 80)
    if t >= RINGS[1]: return "06:09", (255, 200, 80)
    return "06:00", (255, 200, 80)


def ringing(t):
    return any(r <= t < s for r, s in zip(RINGS, SNOOZE)) or (TURN <= t < TURN + 0.6)


# ------------------------------------------------------------------ characters
def riser(t):
    if t < 1.0:
        return None                                                     # still in bed (drawn as blanket + head)
    if t < 1.8:                                                         # stands up next to her bed, stretches
        return dict(x=640, y=G, p=mix(dict(crouch(), head=-6), cheer(t), seg(t, 1.0, 1.8)), f=-1)
    if t < 2.4:
        return dict(x=640, y=G, p=mix(cheer(t), stand(), seg(t, 1.8, 2.4)), f=-1 + 2 * seg(t, 2.0, 2.4))
    if t < 3.4:                                                         # out through her door (right)
        x = lerp(640, 700, seg(t, 2.4, 3.4))
        return dict(x=x, y=G, p=walk(t * 8, lean=6), f=1, fade=1 - seg(t, 3.0, 3.4))
    if t < TURN + 0.8:
        return None
    x = lerp(700, 610, seg(t, TURN + 0.8, TURN + 1.6))                   # back from the run, glowing
    if t < TURN + 1.6:
        return dict(x=x, y=G, p=walk(t * 8, lean=4), f=-1, fade=seg(t, TURN + 0.8, TURN + 1.1))
    return dict(x=610, y=G, p=dict(hands_on_hips(), head=-8, lean=-4 + 1.5 * math.sin(t * 3)), f=-1)


def excuse(t):
    if t < TURN:
        return None                                                     # in bed
    k = seg(t, TURN, TURN + 0.5)                                        # shoots up, hands to his head
    return dict(x=300, y=G, p=mix(dict(crouch(), head=20), dict(shrug(1.0), head=-14, lean=-6), k), f=1)


# ------------------------------------------------------------------ world
def bed(c, x0, x1, cover, sleeper_col, head_pos, head_a, t, blanket_up=1.0):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, G - 70, x1, G - 30), 8, 8), P((140, 100, 80)))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 6, G - 30, x0 + 18, G), P((110, 80, 60))); c.drawRect(skia.Rect.MakeLTRB(x1 - 18, G - 30, x1 - 6, G), P((110, 80, 60)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0 - 4, G - 120, x0 + 18, G - 30), 6, 6), P((120, 86, 66)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0 + 18, G - 96, x0 + 92, G - 68), 12, 12), P((236, 236, 244)))
    if head_a > 0:
        c.drawCircle(head_pos[0], head_pos[1], 19, P(sleeper_col, head_a)); c.drawCircle(head_pos[0], head_pos[1], 19, P(INK, head_a, stroke=4))
    breathe = 3 * math.sin(t * 1.6)
    if blanket_up > 0:
        p = poly([(x0 + 60, G - 70), (x0 + 70, G - 104 - breathe), (x0 + 140, G - 112 - breathe), (x1 - 30, G - 96), (x1 - 10, G - 70)])
        c.drawPath(p, P(cover, blanket_up)); c.drawPath(p, P(INK, blanket_up, stroke=4))
    else:
        c.drawPath(poly([(x1 - 60, G - 70), (x1 - 20, G - 90), (x1 + 10, G - 50), (x1 - 10, G - 40)]), P(cover))


def alarm(c, pos, t, text_col_t):
    x, y = pos
    txt, col = text_col_t
    shake = 3 * math.sin(t * 60) if ringing(t) else 0
    c.save(); c.translate(x + shake, y)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-48, -30, 96, 52), 10, 10), P((40, 40, 50)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-48, -30, 96, 52), 10, 10), P(INK, stroke=4))
    text(c, txt, 0, 8, F_CAP, 30, col, 1.0)
    c.restore()
    if ringing(t):
        for k in (1, 2):
            c.drawArc(skia.Rect.MakeXYWH(x - 50 - 14 * k, y - 46 - 10 * k, 100 + 28 * k, 80 + 20 * k), 200, 140, False, P((255, 220, 120), 0.8, stroke=4))


def world(c, t):
    u = light(t)
    sky(c, t, lerpc((30, 40, 90), (120, 160, 230), u), lerpc((60, 70, 130), (255, 180, 140), u), lerpc((90, 90, 150), (255, 220, 170), u), 1100)
    # rooms (cut-away)
    for x0, x1, wall in ((150, WALL, (110, 120, 170)), (WALL + 14, 760, (150, 120, 150))):
        c.drawRect(skia.Rect.MakeLTRB(x0, G - 400, x1, G), P(lerpc(tuple(int(v * 0.55) for v in wall), wall, u)))
    c.drawRect(skia.Rect.MakeLTRB(WALL, G - 400, WALL + 14, G), P((70, 70, 90)))
    c.drawRect(skia.Rect.MakeLTRB(140, G - 410, 770, G - 396), P((70, 70, 90)))
    c.drawRect(skia.Rect.MakeLTRB(130, G, 780, G + 16), P((90, 70, 60)))
    # his window: dawn outside, she runs past at 4.6–6.8
    wx0, wy0, wx1, wy1 = 210, G - 350, 400, G - 200
    c.save(); c.clipRect(skia.Rect.MakeLTRB(wx0, wy0, wx1, wy1))
    sky(c, t, lerpc((40, 50, 110), (255, 170, 120), u), lerpc((70, 80, 140), (255, 200, 150), u), lerpc((90, 90, 150), (255, 230, 180), u), wy1)
    c.drawCircle(330, wy1 + 30 - 60 * u, 40, P((255, 230, 180), 0.6 + 0.4 * u))
    c.drawRect(skia.Rect.MakeLTRB(wx0, wy1 - 26, wx1, wy1), P(lerpc((30, 40, 50), (80, 100, 70), u)))
    rk = seg(t, 4.6, 6.8)
    figure(c, lerp(wx0 - 20, wx1 + 20, rk), wy1 - 26, run(t * 12), s=0.38, facing=1, body=R_BODY)   # outside the window = clipped when not passing
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(wx0, wy0, wx1, wy1), P((240, 236, 230), stroke=10))
    c.drawLine((wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1, P((240, 236, 230), stroke=6))
    # sun shafts through the window
    if u > 0.05:
        c.drawPath(poly([(wx0, wy0), (wx1, wy0), (wx1 + 220, G), (wx0 + 120, G)]), P((255, 210, 150), 0.18 * u, blur=20))
    # her door (right)
    c.drawRect(skia.Rect.MakeLTRB(690, G - 220, 750, G), P((120, 90, 70))); c.drawCircle(700, G - 110, 5, P((230, 200, 120)))
    # night stands + clocks
    for (x, y) in (CLOCK, CLOCK_R):
        c.drawRect(skia.Rect.MakeLTRB(x - 40, y + 22, x + 40, G), P((120, 86, 66)))
    alarm(c, CLOCK, t, clock_text(t))
    alarm(c, CLOCK_R, t, ("06:00", (255, 200, 80)) if t < 1.0 else ("06:00", (150, 150, 160)))
    # beds
    ex = excuse(t)
    bed(c, 160, 360, (90, 110, 170), E_BODY, (200, G - 98), 1.0 if ex is None else 0.0, t, blanket_up=1.0 if ex is None else 0.0)
    bed(c, 600, 750, (220, 120, 90), R_BODY, (640, G - 98), 1.0 if t < 1.0 else 0.0, t, blanket_up=1.0 if t < 1.0 else 0.0)
    return u


def snooze_arm(c, t):
    """his arm comes out from under the blanket and slaps the snooze button"""
    for s in SNOOZE:
        k = seg(t, s - 0.4, s) * (1 - seg(t, s + 0.15, s + 0.6))
        if k > 0:
            sx, sy = 300, G - 100
            ex, ey = lerp(sx + 20, CLOCK[0], k), lerp(sy, CLOCK[1] - 30, k)
            mx, my = (sx + ex) / 2, min(sy, ey) - 26 * k
            p = skia.Path(); p.moveTo(sx, sy); p.quadTo(mx, my, ex, ey)
            c.drawPath(p, P(INK, stroke=22)); c.drawPath(p, P(E_BODY, stroke=14))
            c.drawCircle(ex, ey, 11, P(E_BODY)); c.drawCircle(ex, ey, 11, P(INK, stroke=4))


def frame(c, t):
    sway = 1 + 0.018 * math.sin(t * 0.9) + 0.06 * seg(t, 13.6, T_END)
    c.save(); c.translate(540 + 8 * math.sin(t * 0.6), G + DY); c.scale(SC * sway, SC * sway); c.translate(-540 + 34, -G)   # +34: centre the two rooms
    u = world(c, t)
    snooze_arm(c, t)
    lo = (-1, -0.6)
    heads = {"e": (200, G - 98), "r": (640, G - 98)}
    # both figures are always drawn (invisible while in bed / out on the run) so the figure check can follow them
    ex = excuse(t) or dict(x=300, y=G, p=dict(crouch(), head=20), f=1)
    c.saveLayerAlpha(None, 255 if t >= TURN else 0)
    je = figure(c, ex["x"], ex["y"], ex["p"], s=S, facing=ex["f"], body=E_BODY, rim=((210, 220, 255), 0.5), light=lo)
    c.restore()
    if t >= TURN: heads["e"] = je["head"]
    ri = riser(t)
    rv = ri or dict(x=640 if t < 1.0 else 700, y=G, p=dict(crouch(), head=-6) if t < 1.0 else stand(), f=-1 if t < 1.0 else 1 - 2 * seg(t, 5.0, 6.0), fade=0.0)   # turns around while out of sight
    c.saveLayerAlpha(None, int(255 * rv.get("fade", 1.0)))
    jr = figure(c, rv["x"], rv["y"], rv["p"], s=S, facing=rv["f"], body=R_BODY, rim=((255, 220, 170), 0.3 + 0.5 * u), light=lo)
    c.restore()
    if ri is not None: heads["r"] = jr["head"]
    if t > 13.0 or ri is not None or t < 1.0:
        plate_label(c, "EARLY RISER", heads["r"][0], heads["r"][1] - 56 - (40 if ri is None else 0), AMBER, 0.95 * (1 if ri is not None or t < 1.0 else 0))
    plate_label(c, "EXCUSE CLOCK", heads["e"][0] + (20 if t < TURN else 0), heads["e"][1] - 66, GREY, 0.9)
    for ts, who, txt in TALK:
        if ts < t < ts + 1.7:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.4, ts + 1.7))
            hd = heads[who]
            bx = clamp(hd[0] + (90 if who == "e" else -60), 300, 600)
            bubble(c, bx, hd[1] - 140, txt, a, "speech", tail=(hd[0] + 10, hd[1] - 40), size=30, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    vignette(c, 0.35)
    grain(c, t, 0.03)
    end_text(c, t, 13.6, "He hit snooze 3 times.", "She was already out.", "Win the morning. Win the day.", y=1430)


def events():
    ev = []
    for ts, _, _ in TALK: ev.append(["pop", ts])
    for r in RINGS: ev.append(["slip", r])
    for s in SNOOZE: ev.append(["thud", s])
    ev += [["land", TURN], ["sunrise", TURN + 0.6], ["summit", TURN + 1.6], ["text", 13.6], ["text2", 14.4]]
    return ev


def overlay(c, t):
    series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.05, 0.9, 1.6, 2.2, 3.0, 4.6, 5.6, 7.6, 9.0, 10.2, 11.0, 12.2, 14.4, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore(); overlay(c, t)
        stills(opening, ts, "check/ep18")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs))
    else:
        finish_v2("Folge18_EarlyRiser", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
