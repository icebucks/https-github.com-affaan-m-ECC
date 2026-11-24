"""Episode 31 v2 (TikTok: Part 28): PHONE AT DINNER vs PRESENT – promised by Part 27 ("the one on his phone at dinner").
SHAREABLE topic (couples, episodes.md "Teilbar"). Retention-Standard v2.
Frame 0 (climax first): CLINK – she raises her glass for a toast, his glass stays on the table, his face glows blue from the phone.
Time-lapse 8:00 → 8:45: she talks, then waits (chin on hand); the candle burns down; his like counter climbs (ON PHONE 0 → 45 MIN).
TURN 6.4 s: the candle goes out – she stands up and leaves. His phone buzzes: her text "Enjoy dinner with your phone."
Second turn: he looks up at the empty chair, puts the phone face down (THUD) and pulls her chair out – she comes back.
Loop: both seated again, she raises her glass – this time he raises his too."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 28                     # TikTok part number (internal episode 31)
TURN = 6.4
LAPSE0, LAPSE1 = 2.2, 5.2      # 8:00 -> 8:45
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
CAMX = 190                     # camera centre (world x)
TAB = (95, 225)                # table x range (world)
TAB_Y = G - 112                # table top
HX = 32                        # his hip
SX = 288                       # her hip
SEAT = G - 68                  # hip height when seated
STAND = G - 126                # hip height when standing (thigh + shin = 84 * S)
DOORX = 360
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Dinner for two.\nWho's actually there?"
CTA = "Part 29 next:\nthe gym selfie guy"
END_TXT = "Look up. They're right there."
TALK = [(0.95, "s", "Guess what happened!"), (2.35, "h", "Mhm."), (8.3, "h", "I'm here now.")]


def clock(t):
    m = int(45 * seg(t, LAPSE0, LAPSE1)) + (int(5 * seg(t, LAPSE1, TURN)) if t > LAPSE1 else 0)
    return f"8:{m:02d} PM"


def on_phone(t): return int(45 * seg(t, LAPSE0, LAPSE1)) + (int(5 * seg(t, LAPSE1, TURN)) if t > LAPSE1 else 0)


def candle(t):
    """remaining candle height 0..1 and flame 0..1"""
    h = 1 - 0.8 * seg(t, LAPSE0, LAPSE1)
    if t < TURN: fl = 1.0 if t < 5.4 else 0.55 + 0.45 * abs(math.sin(t * 23))      # flickers before it dies
    elif t < 10.2: fl = 0.0
    else: fl = seg(t, 10.2, 10.45)                                                   # he lights it again
    return h if t < 10.2 else 1.0, fl


# ------------------------------------------------------------------ characters
PHONE = dict(lean=10, head=22, arm_f=62, elb_f=118, arm_b=30, elb_b=100)            # both hands on the phone at chest height


def him(t):
    if t < 6.9:                                                            # scrolling, head down
        p = dict(sit(t), **PHONE)
        p["elb_f"] += 5 * math.sin(t * 11)                                  # thumb scrolling
        return dict(x=HX, y=SEAT, p=p, f=1)
    if t < 7.5:                                                            # looks up at the empty chair
        k = seg(t, 6.9, 7.2)
        p = mix(dict(sit(t), **PHONE), dict(sit(t), lean=-2, head=-6, arm_f=62, elb_f=110, arm_b=30, elb_b=100), k)
        return dict(x=HX, y=SEAT, p=p, f=1)
    if t < 8.0:                                                            # slams the phone face down on the table
        k = seg(t, 7.5, 7.75)
        p = mix(dict(sit(t), lean=-2, head=-6, arm_f=62, elb_f=110, arm_b=30, elb_b=100),
                dict(sit(t), lean=14, head=10, arm_f=78, elb_f=24, arm_b=20, elb_b=40), k)
        return dict(x=HX, y=SEAT, p=p, f=1)
    if t < 10.1:                                                           # turns to her, open hand (apology)
        p = dict(sit(t), lean=4, head=-4, arm_f=70, elb_f=30, arm_b=16, elb_b=40)
        return dict(x=HX, y=SEAT, p=p, f=1)
    if t < 10.6:                                                           # lights the candle again
        p = dict(sit(t), lean=16, head=14, arm_f=80, elb_f=20, arm_b=16, elb_b=40)
        return dict(x=HX, y=SEAT, p=p, f=1)
    k = seg(t, 11.5, 11.9)                                                 # loop: raises his glass too
    p = mix(dict(sit(t), lean=4, head=-4, arm_f=40, elb_f=60, arm_b=16, elb_b=40),
            dict(sit(t), lean=4, head=-8, arm_f=88, elb_f=46, arm_b=16, elb_b=40), k)
    return dict(x=HX, y=SEAT, p=p, f=1)


TOAST = dict(lean=-2, head=-8, arm_f=92, elb_f=44, arm_b=16, elb_b=40)


def her(t):
    if t < 0.75:                                                           # frame 0: glass raised for the toast
        return dict(x=SX, y=SEAT, p=dict(sit(t), **TOAST), f=-1, hip=True)
    if t < 3.4:                                                            # talks with her hands
        g = math.sin(t * 7)
        p = mix(dict(sit(t), **TOAST), dict(sit(t), lean=2, head=-4, arm_f=55 + 14 * g, elb_f=70 - 20 * g, arm_b=16, elb_b=40),
                seg(t, 0.75, 1.0))
        return dict(x=SX, y=SEAT, p=p, f=-1, hip=True)
    if t < TURN:                                                           # gives up: elbow on the table, chin on hand
        p = mix(dict(sit(t), lean=2, head=-4, arm_f=55, elb_f=70, arm_b=16, elb_b=40),
                dict(sit(t), lean=14, head=14, arm_f=28, elb_f=150, arm_b=16, elb_b=60), seg(t, 3.4, 3.8))
        return dict(x=SX, y=SEAT, p=p, f=-1, hip=True)
    if t < 6.9:                                                            # stands up
        k = seg(t, TURN, 6.9)
        p = mix(dict(sit(t), lean=14, head=14, arm_f=28, elb_f=150, arm_b=16, elb_b=60), stand(), k)
        return dict(x=SX + 14 * k, y=lerp(SEAT, STAND, k), p=p, f=-1, hip=True)
    if t < 7.9:                                                            # walks away to the door
        k = seg(t, 6.9, 7.9)
        return dict(x=lerp(SX + 14, DOORX, k), y=G, p=walk(t * 9), f=lerp(-1, 1, seg(t, 6.9, 7.2)), hip=False)
    if t < 8.9:                                                            # stops, turns back when the phone hits the table
        return dict(x=DOORX, y=G, p=arms_crossed(-4), f=lerp(1, -1, seg(t, 8.1, 8.4)), hip=False)
    if t < 9.9:                                                            # comes back
        k = seg(t, 8.9, 9.9)
        return dict(x=lerp(DOORX, SX + 14, k), y=G, p=walk(t * 9), f=-1, hip=False)
    if t < 10.4:                                                           # sits down
        k = seg(t, 9.9, 10.4)
        return dict(x=lerp(SX + 14, SX, k), y=lerp(STAND, SEAT, k), p=mix(stand(), dict(sit(t), lean=2, head=-4, arm_f=40, elb_f=60, arm_b=16, elb_b=40), k), f=-1, hip=True)
    k = seg(t, 11.5, 11.9)                                                 # loop: raises her glass like in frame 0
    p = mix(dict(sit(t), lean=2, head=-4, arm_f=40, elb_f=60, arm_b=16, elb_b=40), dict(sit(t), **TOAST), k)
    return dict(x=SX, y=SEAT, p=p, f=-1, hip=True)


# ------------------------------------------------------------------ world
def room(c, t):
    dark = 0.35 * seg(t, TURN, TURN + 0.2) * (1 - seg(t, 10.2, 10.5))    # the room dims when the candle dies
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, 700, G), P(lerpc((92, 58, 48), (50, 34, 34), dark)))
    for i in range(-3, 8):                                                 # wall panels
        c.drawLine(i * 90, G - 380, i * 90, G, P((70, 44, 38), stroke=3))
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 380, 700, G - 372), P((130, 90, 60)))
    c.drawRect(skia.Rect.MakeLTRB(40, G - 330, 280, G - 200), P((24, 26, 52)))   # window, night city
    for i, (wx, wy) in enumerate([(70, -300), (110, -280), (150, -310), (200, -290), (240, -305), (90, -250), (180, -240), (255, -260)]):
        c.drawCircle(wx, G + wy, 3, P((255, 220, 150), 0.6 + 0.4 * math.sin(t * 2 + i)))
    c.drawRect(skia.Rect.MakeLTRB(40, G - 330, 280, G - 200), P((140, 100, 70), stroke=6))
    c.drawLine(160, G - 330, 160, G - 200, P((140, 100, 70), stroke=4))
    for i in range(12):                                                    # string lights
        lx = -120 + i * 60; ly = G - 420 + 14 * math.sin(i * 1.3)
        c.drawCircle(lx, ly, 6, P((255, 210, 130), (0.9 - dark) * (0.7 + 0.3 * math.sin(t * 3 + i))))
        c.drawCircle(lx, ly, 18, P((255, 190, 110), 0.25 * (1 - dark), blur=8))
    c.drawRect(skia.Rect.MakeLTRB(DOORX + 40, G - 260, DOORX + 130, G), P((60, 36, 30)))   # exit door
    c.drawRect(skia.Rect.MakeLTRB(DOORX + 40, G - 260, DOORX + 130, G), P(INK, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(-300, G, 700, G + 500), P((70, 50, 44)))


def chairs(c, t):
    for x, d in ((HX, -1), (SX, 1)):
        c.drawRect(skia.Rect.MakeLTRB(x - 30, SEAT + 2, x + 30, SEAT + 12), P((120, 80, 50)))
        c.drawLine(x - 24, SEAT + 12, x - 24, G, P((90, 60, 40), stroke=6)); c.drawLine(x + 24, SEAT + 12, x + 24, G, P((90, 60, 40), stroke=6))
        bx = x + 30 * d
        c.drawLine(bx, SEAT + 12, bx, SEAT - 110, P((90, 60, 40), stroke=8))


def table(c, t):
    x0, x1 = TAB
    c.drawRect(skia.Rect.MakeLTRB(x0, TAB_Y, x1, TAB_Y + 70), P((235, 225, 210)))   # tablecloth
    c.drawRect(skia.Rect.MakeLTRB(x0, TAB_Y, x1, TAB_Y + 70), P(INK, stroke=3))
    c.drawLine((x0 + x1) / 2, TAB_Y + 70, (x0 + x1) / 2, G, P((90, 60, 40), stroke=10))
    c.drawLine((x0 + x1) / 2 - 30, G, (x0 + x1) / 2 + 30, G, P((90, 60, 40), stroke=8))
    for px in (x0 + 30, x1 - 30):                                          # plates (her food untouched)
        c.drawOval(skia.Rect.MakeLTRB(px - 24, TAB_Y - 8, px + 24, TAB_Y + 2), P((250, 250, 250)))
        c.drawOval(skia.Rect.MakeLTRB(px - 24, TAB_Y - 8, px + 24, TAB_Y + 2), P(INK, stroke=2))
    h, fl = candle(t)                                                      # candle in the middle
    cx = (x0 + x1) / 2
    ch = 60 * h
    c.drawRect(skia.Rect.MakeLTRB(cx - 7, TAB_Y - ch, cx + 7, TAB_Y), P((250, 240, 220)))
    c.drawRect(skia.Rect.MakeLTRB(cx - 7, TAB_Y - ch, cx + 7, TAB_Y), P(INK, stroke=2))
    if fl > 0:
        c.drawCircle(cx, TAB_Y - ch - 10, 60, P((255, 180, 90), 0.35 * fl, blur=22))
        c.drawOval(skia.Rect.MakeLTRB(cx - 5 * fl, TAB_Y - ch - 22 * fl, cx + 5 * fl, TAB_Y - ch - 2), P((255, 220, 120), fl))
    if TURN <= t < TURN + 1.6:                                             # smoke curl when it dies
        k = (t - TURN) / 1.6
        for i in range(3):
            c.drawCircle(cx + 8 * math.sin(k * 7 + i), TAB_Y - ch - 14 - 70 * k - i * 14, 6 + 5 * k, P((200, 200, 210), 0.5 * (1 - k)))
    if t < 7.5 or t >= 10.6:                                               # his glass stays on the table (until the loop)
        pass


def glass(c, x, y, a=1.0):
    c.drawRect(skia.Rect.MakeLTRB(x - 6, y - 26, x + 6, y - 6), P((180, 40, 60), 0.85 * a))
    c.drawLine(x, y - 6, x, y + 6, P((230, 230, 240), a, stroke=3))
    c.drawRect(skia.Rect.MakeLTRB(x - 7, y - 30, x + 7, y - 6), P((230, 230, 240), a, stroke=2))


def to_screen(p): return (470 + (p[0] - CAMX) * K, 1440 + (p[1] - G) * K)


def frame(c, t):
    c.save(); c.translate(470, 1440); c.scale(K, K); c.translate(-CAMX, -G)
    room(c, t)
    chairs(c, t)
    lo = (1, -0.6)
    h = him(t)
    jh = figure(c, h["x"], h["y"], h["p"], s=S, facing=h["f"], body=H_BODY, rim=((150, 190, 255), 0.6), light=lo, mode="hip")
    e = her(t)
    je = figure(c, e["x"], e["y"], e["p"], s=S, facing=e["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo,
                mode="hip" if e["hip"] else "feet")
    table(c, t)
    # her glass: in her hand while toasting, otherwise on the table
    if t < 1.0 or t >= 11.5:
        glass(c, *je["hand_f"])
    else:
        glass(c, TAB[1] - 52, TAB_Y)
    # his glass: on the table, in his hand only in the loop toast
    if t >= 11.5:
        glass(c, *jh["hand_f"])
    else:
        glass(c, TAB[0] + 52, TAB_Y)
    # his phone: in his hands, face down on the table after the slam
    if t < 7.6:
        px, py = jh["hand_f"]
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px - 7, py - 24, 14, 28), 3, 3), P((30, 30, 40)))
        c.drawCircle(px - 6, py - 14, 46, P((120, 190, 255), 0.35, blur=16))
    else:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(TAB[0] + 6, TAB_Y - 5, 30, 5), 2, 2), P((30, 30, 40)))
    c.restore()
    heads = {"h": to_screen(jh["head"]), "s": to_screen(je["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "PHONE AT DINNER", GREY, size=28, a=na)
        chip(c, 760, 720, "PRESENT", AMBER, size=28, a=na)
    vignette(c, 0.25 + 0.2 * seg(t, TURN, TURN + 0.2) * (1 - seg(t, 10.2, 10.5)))
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    if t < 9.6:
        chip(c, 540, 640, clock(t) + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=34 + 16 * lapse)
        chip(c, 250, 545, f"ON PHONE {on_phone(t)} MIN", GREY, size=34)
        st = "TALKING" if t < 3.4 else ("WAITING" if t < TURN else ("LEAVING" if t < 8.15 else "COMING BACK"))
        chip(c, 790, 545, st, AMBER, size=34, pop=1 + 0.3 * (1 - seg(t, TURN, TURN + 0.25)) * (TURN < t < TURN + 0.5))
    if LAPSE0 < t < TURN:                                                  # his likes keep coming in
        n = int(1 + 46 * seg(t, LAPSE0, LAPSE1))
        hx, hy = to_screen(jh["hand_f"])
        chip(c, hx + 10, hy - 150, f"+{n} likes", (120, 190, 255), size=30, pop=1 + 0.12 * abs(math.sin(t * 9)))
    if TURN + 0.25 <= t < 8.2:                                             # her text lands on his phone
        a = seg(t, TURN + 0.25, TURN + 0.35) * (1 - seg(t, 7.9, 8.2)); pop = 1 + 0.25 * (1 - seg(t, TURN + 0.25, TURN + 0.45))
        chip(c, 540, 770, "\"Enjoy dinner with your phone.\"", (120, 190, 255), size=34, a=a, pop=pop)
    for ts, who, txt in TALK:
        if ts < t < ts + 1.3:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.1, ts + 1.3))
            hx_, hy_ = heads[who]
            bx_ = clamp(hx_ + 220 if who == "h" else hx_ - 220, 300, 700)
            bubble(c, bx_, 830, txt, a, "speech", tail=(hx_ + (40 if who == "h" else -40), hy_ - 50), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", 0.0, "tone-ding-high", -6]]                             # clink of the toast in frame 0
    ev += [["sfx", LAPSE0, "time-clock-fast", -10], ["sfx", LAPSE0, "data-countup-long", -14], ["sfx", LAPSE0, "riser-2s-soft", -12]]
    ev += [["sfx", TURN + 0.3, "pop-medium-in", -6], ["thud", 7.7], ["sfx", 10.25, "shimmer-long-sparkle", -14],
           ["sfx", 11.9, "tone-ding-high", -8], ["text", END_T0]]
    return ev


if __name__ == "__main__":
    main("Folge31_Dinner_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep31_v2",
         [0.0, 0.4, 1.3, 2.6, 3.9, 5.6, 6.6, 7.3, 7.8, 8.6, 10.0, 11.0, 12.0, 12.4])
