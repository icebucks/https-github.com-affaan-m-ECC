"""Episode 36 v2 (TikTok: Part 33): ONE MORE REP vs GOOD FORM – promised by Part 32 ("the 'one more rep' guy").
Sport topic (pull-ups; shareable: the gym buddy who swings every rep). Retention-Standard v2.
Frame 0 (climax first): CLANG – he swings so hard the bar rattles ("ONE MORE!").
Time-lapse WEEK 1 → WEEK 8: he swings half reps (REPS 20, "half"), she does slow strict reps (STRICT 1 → 10).
TURN 6.4 s: TEST DAY – 10 strict reps each: she does 10 clean; he gets 2 and hangs stuck.
Second turn: she shows him: slow, full range. He drops down and starts over with one slow rep.
Loop: back at the bar – he swings again (frame 0)… the chip says WEEK 1 again.
Poses: both hands are IK-locked to the bar (reach), hanging = arms straight up, chin over the bar at the top."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 33                     # TikTok part number (internal episode 36)
TURN = 6.4
LAPSE0, LAPSE1 = 2.2, 5.2      # WEEK 1 -> WEEK 8
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
CAMX = 180
BAR_Y = G - 372
HX, SX = 80, 290               # bar centres
HANG = BAR_Y + 196             # hip height hanging with straight arms
TOP = BAR_Y + 130              # hip height with the chin over the bar
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Same bar. 8 weeks.\nWho can do 10 real ones?"
CTA = "Part 34 next:\nthe 'diet starts Monday' friend"
END_TXT = "Full range beats more reps."
TALK = [(0.9, "h", "One more!"), (7.0, "h", "Why is this... hard?"), (8.3, "s", "Slow. All the way.")]


def week(t): return 1 + int(7 * seg(t, LAPSE0, LAPSE1)) if t < 11.6 else 1
def strict(t):
    if t < LAPSE0: return 1
    if t < TURN: return 1 + int(9 * seg(t, LAPSE0, LAPSE1))
    return min(10, int(10 * seg(t, TURN, 7.9)))


# ------------------------------------------------------------------ characters
HANG_P = dict(lean=0, head=-12, arm_f=172, elb_f=6, arm_b=172, elb_b=6, leg_f=12, leg_b=4, knee_f=30, knee_b=24)


def him(t):
    if t < LAPSE1 or t >= 11.6:                                           # kipping: body swings, half reps
        sp = 9 if LAPSE0 < t < LAPSE1 else 6
        ph = math.sin(t * sp)
        y = lerp(HANG - 10, TOP + 30, 0.5 + 0.5 * ph)                     # never really reaches the top
        p = dict(HANG_P, lean=22 * math.cos(t * sp), leg_f=12 + 40 * max(0, -math.cos(t * sp)), leg_b=4 + 30 * max(0, -math.cos(t * sp)),
                 knee_f=30 + 40 * max(0, math.cos(t * sp)), head=-16)
        return dict(x=HX + 10 * math.cos(t * sp), y=y, p=p, hang=True)
    if t < TURN: return dict(x=HX, y=HANG, p=HANG_P, hang=True)
    if t < 7.9:                                                            # test day: strict – 2 reps, then stuck halfway
        r = (t - TURN) / 0.55
        if r < 2: k = math.sin(math.pi * (r % 1))
        else: k = 0.45 + 0.04 * math.sin(t * 30)                           # trembling, stuck
        return dict(x=HX, y=lerp(HANG, TOP, k), p=dict(HANG_P, head=-20), hang=True)
    if t < 8.4:                                                            # drops down to the floor
        k = seg(t, 7.9, 8.2)
        return dict(x=HX, y=lerp(HANG, G - 126, k), p=mix(HANG_P, stand(), k), hang=k < 0.5)
    if t < 10.6:                                                           # listens, then one slow full rep
        if t < 9.4: return dict(x=HX + 20, y=G - 126, p=dict(stand(), head=6), hang=False, f=1)
        k = seg(t, 9.4, 9.6)
        if t < 9.6: return dict(x=lerp(HX + 20, HX, k), y=lerp(G - 126, HANG, k), p=mix(stand(), HANG_P, k), hang=k > 0.5)
        r = math.sin(math.pi * seg(t, 9.6, 10.6))
        return dict(x=HX, y=lerp(HANG, TOP, r), p=HANG_P, hang=True)
    return dict(x=HX, y=HANG, p=HANG_P, hang=True)


def her(t):
    if t < TURN or (8.1 < t < 9.3) or t > 11.0:                           # slow strict reps (fast in the time-lapse)
        if 8.1 < t < 9.3:                                                  # shows him: one slow rep while talking
            r = math.sin(math.pi * seg(t, 8.1, 9.3))
        else:
            sp = 7 if LAPSE0 < t < LAPSE1 else 2.4
            r = 0.5 - 0.5 * math.cos(t * sp)
        return dict(x=SX, y=lerp(HANG, TOP, r), p=dict(HANG_P, leg_f=8, leg_b=8, knee_f=20, knee_b=20), hang=True)
    if t < 8.1:                                                            # test day: 10 strict reps, quick but full
        r = 0.5 - 0.5 * math.cos(2 * math.pi * 10 * seg(t, TURN, 7.9))
        return dict(x=SX, y=lerp(HANG, TOP, r), p=dict(HANG_P, leg_f=8, leg_b=8, knee_f=20, knee_b=20), hang=True)
    return dict(x=SX, y=HANG, p=dict(HANG_P, leg_f=8, leg_b=8, knee_f=20, knee_b=20), hang=True)


# ------------------------------------------------------------------ world
def gym(c, t):
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, 700, G), P((70, 74, 86)))
    for i in range(-3, 9):
        c.drawRect(skia.Rect.MakeLTRB(i * 90 - 30, G - 560, i * 90 + 30, G - 552), P((240, 240, 255), 0.9))
    c.drawRect(skia.Rect.MakeLTRB(-300, G, 700, G + 500), P((44, 46, 54)))
    for i in range(-3, 9): c.drawLine(i * 80, G, i * 80 - 40, G + 500, P((56, 58, 66), stroke=3))
    for bx in (HX, SX):                                                   # pull-up rigs
        shake = 2.5 * math.sin(t * 60) * (1 - seg(t, 0.0, 0.35)) if bx == HX else 0
        c.drawLine(bx - 70, BAR_Y - 20, bx - 70, G, P((50, 50, 58), stroke=9))
        c.drawLine(bx + 70, BAR_Y - 20, bx + 70, G, P((50, 50, 58), stroke=9))
        c.drawLine(bx - 74, BAR_Y + shake, bx + 74, BAR_Y + shake, P((190, 190, 200), stroke=6))


def to_screen(p): return (470 + (p[0] - CAMX) * K, 1700 + (p[1] - G) * K)


def body(c, d, col, rim, lo):
    if d["hang"]:
        return figure(c, d["x"], d["y"], d["p"], s=S, facing=1, body=col, rim=rim, light=lo, mode="hip",
                      reach={"f": (d["x"] + 22, BAR_Y), "b": (d["x"] - 22, BAR_Y)})
    return figure(c, d["x"], G, d["p"], s=S, facing=d.get("f", 1), body=col, rim=rim, light=lo)


def frame(c, t):
    c.save(); c.translate(470, 1700); c.scale(K, K); c.translate(-CAMX, -G)
    gym(c, t)
    lo = (1, -0.6)
    jh = body(c, him(t), H_BODY, ((210, 220, 255), 0.5), lo)
    je = body(c, her(t), S_BODY, ((255, 220, 170), 0.6), lo)
    c.restore()
    heads = {"h": to_screen(jh["head"]), "s": to_screen(je["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "ONE MORE REP", GREY, size=28, a=na)
        chip(c, 760, 720, "GOOD FORM", AMBER, size=28, a=na)
    vignette(c, 0.25)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    if t < 9.6 or t >= 11.6:
        label = "TEST DAY" if TURN <= t < 9.6 else f"WEEK {week(t)}"
        chip(c, 520, 640, label + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 or label == "TEST DAY" else (255, 240, 210), size=34 + 16 * lapse)
    if t < 9.6:
        if t < TURN: chip(c, 250, 545, f"REPS {20 if t > LAPSE0 + 0.5 else 12} (HALF)", GREY, size=34)
        else: chip(c, 250, 545, "STRICT 2", RED, size=34, pop=1 + 0.3 * (1 - seg(t, 7.5, 7.75)) * (7.5 < t < 8.0))
        chip(c, 760, 545, f"STRICT {strict(t)}", AMBER, size=34, pop=1 + 0.2 * (TURN < t < 7.9) * abs(math.sin(t * 20)))
    for ts, who, txt in TALK:
        if ts < t < ts + 1.3:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.1, ts + 1.3))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 230 if who == "h" else hx_ - 230, 320, 700)
            bubble(c, bx_, 1180, txt, a, "speech", tail=(hx_ + (50 if who == "h" else -50), hy_ + 20), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", 0.0, "cinematic-slam-big", -10]]                        # CLANG
    ev += [["sfx", LAPSE0, "time-clock-fast", -10], ["sfx", LAPSE0, "riser-2s-soft", -12]]
    ev += [["sfx", TURN, "tone-ding-high", -8], ["sfx", TURN + 0.2, "data-countup-medium", -12], ["thud", 8.2],
           ["sfx", 10.6, "tone-step-3", -8], ["sfx", 11.6, "whoosh-medium-soft", -8], ["sfx", 12.4, "cinematic-slam-big", -14], ["text", END_T0]]
    return ev


if __name__ == "__main__":
    main("Folge36_OneMoreRep_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep36_v2",
         [0.0, 0.3, 1.3, 3.0, 4.6, 6.0, 6.8, 7.6, 8.3, 8.8, 9.9, 11.0, 12.0, 12.45])
