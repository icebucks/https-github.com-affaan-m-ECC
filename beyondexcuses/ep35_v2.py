"""Episode 35 v2 (TikTok: Part 32): "I'LL TEXT BACK" vs REPLIES – promised by Part 31 ("the 'I'll text back' friend").
SHAREABLE topic (friends, episodes.md "Teilbar"). Split screen: left his couch, right her room. Retention-Standard v2.
Frame 0 (climax first): BZZT – a notification lands on his phone, the UNREAD badge pops … he swipes it away.
Time-lapse MON → FRI: her messages pile up on his side (UNREAD 1 → 99), she gets replies from everyone else.
TURN 6.4 s: on her side the trip is booked – "4 TICKETS" – his phone: "You were not added to WEEKEND TRIP".
Second turn: he finally opens the chat and types "I'M IN!" – she answers "1 SEAT LEFT. GO." – he runs out.
Loop: next buzz – this time he answers in 1 second (frame 0 layout, badge pops)."""
import math
from lib_v2 import *

T_END = 12.5
SHOWN = 32                     # TikTok part number (internal episode 35)
TURN = 6.4
LAPSE0, LAPSE1 = 2.2, 5.2      # MON -> FRI
END_T0 = 9.6
G = 1300
S = 1.5
K = 2.2
SPLIT = 168
HX = 40                        # him on the couch (hip)
SX = 300                       # her standing in her room
SEAT = G - 66
H_BODY = (196, 202, 216)
S_BODY = (255, 226, 178)
HOOK = "Same group chat.\nWho gets left out?"
CTA = "Part 33 next:\nthe 'one more rep' guy"
END_TXT = "Friends wait. Plans don't."
TALK = [(1.0, "h", "I'll reply later."), (6.8, "h", "Wait... what trip?"), (11.7, "h", "On my way!")]
MSGS = [(0.0, "Trip this weekend?"), (2.4, "??"), (3.3, "Booking tonight!"), (4.2, "Last chance...")]
DAYS = ["MON", "TUE", "WED", "THU", "FRI"]


def day(t): return DAYS[min(4, int(5 * seg(t, LAPSE0, LAPSE1)))] if t > LAPSE0 else "MON"
def unread(t):
    if t >= 7.9: return 0
    return 1 + int(98 * seg(t, LAPSE0, LAPSE1))


# ------------------------------------------------------------------ characters
PHONE_SIT = dict(lean=8, head=20, arm_f=62, elb_f=118, arm_b=30, elb_b=100)


def him(t):
    if t < 6.6:                                                            # couch, scrolling, swipes notifications away
        p = dict(sit(t), **PHONE_SIT)
        p["elb_f"] += 6 * math.sin(t * 11)
        if t < 0.6: p["arm_b"] = 30 + 50 * math.sin(math.pi * seg(t, 0.15, 0.55))   # swipe
        return dict(x=HX, y=SEAT, p=p, f=1, hip=True)
    if t < 7.9:                                                            # sits up, stares at the phone
        p = mix(dict(sit(t), **PHONE_SIT), dict(sit(t), lean=-6, head=-2, arm_f=75, elb_f=95, arm_b=30, elb_b=100), seg(t, 6.6, 6.9))
        return dict(x=HX, y=SEAT, p=p, f=1, hip=True)
    if t < 8.9:                                                            # types fast with both thumbs
        p = dict(sit(t), lean=12, head=16, arm_f=70, elb_f=105 + 10 * math.sin(t * 30), arm_b=55, elb_b=110 + 10 * math.sin(t * 30 + 1))
        return dict(x=HX, y=SEAT, p=p, f=1, hip=True)
    if t < 9.5:                                                            # stands up
        k = seg(t, 8.9, 9.5)
        return dict(x=HX + 10 * k, y=lerp(SEAT, G - 126, k), p=mix(dict(sit(t), lean=12, head=16, arm_f=70, elb_f=105, arm_b=55, elb_b=110), stand(), k), f=1, hip=True)
    if t < 11.0:                                                           # runs out (to the right edge of his room)
        return dict(x=lerp(HX + 10, SPLIT - 40, seg(t, 9.5, 10.6)), y=G, p=run(t * 14), f=1, hip=False)
    k = seg(t, 11.0, 11.5)                                                 # loop: back on the couch, answers at once
    p = dict(sit(t), lean=8, head=16, arm_f=70, elb_f=105 + 10 * math.sin(t * 30), arm_b=55, elb_b=110)
    return dict(x=HX, y=SEAT, p=p, f=1, hip=True) if t > 11.5 else dict(x=lerp(SPLIT - 40, HX, k), y=G, p=walk(t * 9), f=lerp(1, -1, seg(t, 11.0, 11.2)) if t < 11.25 else lerp(-1, 1, seg(t, 11.25, 11.5)), hip=False)


def her(t):
    if t < TURN:                                                           # texts, waits, texts again
        p = dict(stand(), lean=2, head=14, arm_f=70, elb_f=105 + 8 * math.sin(t * 9), arm_b=6, elb_b=10)
        if LAPSE0 < t < LAPSE1: p = dict(p, lean=3 * math.sin(t * 5))
        return dict(x=SX, p=p, f=-1)
    if t < 8.0:                                                            # holds up the tickets
        return dict(x=SX, p=dict(stand(), lean=-4, head=-10, arm_f=130, elb_f=30, arm_b=6, elb_b=10), f=-1)
    if t < 9.2:                                                            # answers him
        return dict(x=SX, p=dict(stand(), lean=2, head=14, arm_f=70, elb_f=105 + 8 * math.sin(t * 20), arm_b=6, elb_b=10), f=-1)
    return dict(x=SX, p=mix(hands_on_hips(), dict(stand(), lean=2, head=14, arm_f=70, elb_f=105, arm_b=6, elb_b=10), seg(t, 11.3, 11.7)), f=-1)


# ------------------------------------------------------------------ world
def rooms(c, t):
    c.drawRect(skia.Rect.MakeLTRB(-300, G - 900, SPLIT, G), P((80, 78, 110)))            # his living room (dim)
    c.drawRect(skia.Rect.MakeLTRB(-300, G, SPLIT, G + 500), P((100, 86, 80)))
    c.drawRect(skia.Rect.MakeLTRB(-60, G - 300, 40, G - 200), P((30, 30, 60)))           # window
    c.drawRect(skia.Rect.MakeLTRB(-60, G - 300, 40, G - 200), P((150, 120, 90), stroke=6))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-10, G - 70, 120, G - 30), 10, 10), P((150, 70, 70)))   # couch
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-20, G - 120, 0, G - 30), 8, 8), P((130, 60, 60)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-10, G - 70, 120, G - 30), 10, 10), P(INK, stroke=3))
    c.drawLine(0, G - 30, 0, G, P(INK, stroke=5)); c.drawLine(110, G - 30, 110, G, P(INK, stroke=5))
    c.drawRect(skia.Rect.MakeLTRB(SPLIT, G - 900, 700, G), P((245, 226, 190)))           # her room (bright)
    c.drawRect(skia.Rect.MakeLTRB(SPLIT, G, 700, G + 500), P((190, 160, 120)))
    c.drawRect(skia.Rect.MakeLTRB(220, G - 320, 300, G - 210), P((160, 210, 240)))      # window
    c.drawRect(skia.Rect.MakeLTRB(220, G - 320, 300, G - 210), P((140, 100, 70), stroke=6))
    c.drawRect(skia.Rect.MakeLTRB(SPLIT - 4, G - 900, SPLIT + 4, G + 500), P((20, 20, 30)))


def tickets(c, x, y, a):
    for i in range(4):
        c.save(); c.translate(x - 30 + i * 14, y - i * 4); c.rotate(-12 + i * 8)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-14, -22, 28, 40), 3, 3), P((255, 255, 255), a))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-14, -22, 28, 40), 3, 3), P(INK, a, stroke=1.5))
        c.drawLine(-8, -6, 8, -6, P((90, 160, 230), a, stroke=3))
        c.restore()


def phone(c, x, y, glow=True):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 7, y - 26, 14, 28), 3, 3), P((30, 30, 40)))
    if glow: c.drawCircle(x - 4, y - 14, 40, P((120, 190, 255), 0.3, blur=14))


def to_screen(p): return (470 + (p[0] - 160) * K, 1440 + (p[1] - G) * K)


def frame(c, t):
    c.save(); c.translate(470, 1440); c.scale(K, K); c.translate(-160, -G)
    rooms(c, t)
    lo = (1, -0.6)
    h = him(t)
    jh = figure(c, h["x"], h["y"], h["p"], s=S, facing=h["f"], body=H_BODY, rim=((150, 190, 255), 0.6), light=lo, mode="hip" if h["hip"] else "feet")
    if t < 8.9 or t > 11.5: phone(c, *jh["hand_f"])
    e = her(t)
    je = figure(c, e["x"], G, e["p"], s=S, facing=e["f"], body=S_BODY, rim=((255, 220, 170), 0.6), light=lo)
    if TURN <= t < 8.0: tickets(c, *je["hand_f"], seg(t, TURN, TURN + 0.15))
    else: phone(c, *je["hand_f"], glow=False)
    c.restore()
    heads = {"h": to_screen(jh["head"]), "s": to_screen(je["head"])}
    na = 1 - seg(t, 0.95, 1.2)
    if na > 0:
        chip(c, 250, 720, "I'LL TEXT BACK", GREY, size=28, a=na)
        chip(c, 790, 720, "REPLIES", AMBER, size=28, a=na)
    vignette(c, 0.25)
    lapse = seg(t, LAPSE0, LAPSE0 + 0.25) * (1 - seg(t, LAPSE1, LAPSE1 + 0.4))
    if t < 9.6:
        chip(c, 540, 640, day(t) + ("  >>" if lapse > 0.5 else ""), AMBER if lapse > 0.5 else (255, 240, 210), size=34 + 16 * lapse)
        n = unread(t)
        chip(c, 250, 545, f"UNREAD {n}" if n else "UNREAD 0", RED if n > 20 else GREY, size=34, pop=1 + 0.25 * abs(math.sin(t * 9)) * (LAPSE0 < t < LAPSE1))
        chip(c, 790, 545, "REPLIES IN 1 MIN", AMBER, size=34)
    # her messages landing on his side (and swiped away)
    for t0, msg in MSGS:
        if t0 <= t < t0 + 0.9:
            a = seg(t, t0, t0 + 0.08) * (1 - seg(t, t0 + 0.6, t0 + 0.9)); pop = 1 + 0.25 * (1 - seg(t, t0, t0 + 0.2))
            chip(c, 290, 860, msg, (120, 190, 255), size=36, a=a, pop=pop)
    if TURN + 0.2 <= t < 7.9:                                              # the turn: he is not on the trip
        a = seg(t, TURN + 0.2, TURN + 0.3) * (1 - seg(t, 7.6, 7.9)); pop = 1 + 0.3 * (1 - seg(t, TURN + 0.2, TURN + 0.45))
        chip(c, 700, 860, "4 TICKETS BOOKED", AMBER, size=34, a=a, pop=pop)   # stays left of the TikTok buttons
        chip(c, 290, 1180, "Not added to WEEKEND TRIP", RED, size=32, a=a, pop=pop)
    if 8.0 <= t < 9.4:                                                     # finally: the chat
        a = seg(t, 8.0, 8.1) * (1 - seg(t, 9.1, 9.4))
        chip(c, 290, 860, "I'M IN!", (120, 190, 255), size=44, a=a, pop=1 + 0.25 * (1 - seg(t, 8.0, 8.2)))
        if t > 8.5: chip(c, 680, 860, "1 SEAT LEFT. GO.", AMBER, size=40, a=seg(t, 8.5, 8.6) * (1 - seg(t, 9.1, 9.4)), pop=1 + 0.25 * (1 - seg(t, 8.5, 8.7)))
    if t >= 11.9:                                                          # loop: the badge pops like in frame 0
        chip(c, 290, 860, "Trip this weekend?", (120, 190, 255), size=36, a=seg(t, 11.9, 12.0), pop=1 + 0.25 * seg(t, 12.2, 12.5))
    for ts, who, txt in TALK:
        if ts < t < ts + 1.2:
            a = seg(t, ts, ts + 0.12) * (1 - seg(t, ts + 1.0, ts + 1.2))
            hx_, hy_ = heads[who]
            bubble(c, clamp(hx_ + 220, 300, 640), 1010, txt, a, "speech", tail=(hx_ + 40, hy_ - 50), size=44, pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    grain(c, t, 0.03)


def events():
    ev = [["pop", ts] for ts, _, _ in TALK]
    ev += [["sfx", t0, "pop-medium-in", -6] for t0, _ in MSGS]
    ev += [["sfx", LAPSE0, "time-clock-fast", -10], ["sfx", LAPSE0, "data-countup-long", -14], ["sfx", LAPSE0, "riser-2s-soft", -12]]
    ev += [["sfx", TURN, "tone-ding-high", -8], ["thud", TURN + 0.3], ["sfx", 8.0, "pop-large-in", -8], ["sfx", 8.5, "pop-medium-in", -8],
           ["sfx", 9.5, "whoosh-fast-medium", -10], ["sfx", 11.9, "pop-medium-in", -6], ["text", END_T0]]
    return ev


if __name__ == "__main__":
    main("Folge35_TextBack_v2", frame, T_END, events(), TURN, SHOWN, HOOK, CTA, END_T0, END_TXT, "ep35_v2",
         [0.0, 0.3, 1.3, 3.0, 4.5, 6.0, 6.8, 7.4, 8.2, 8.7, 9.8, 11.2, 12.0, 12.45])
