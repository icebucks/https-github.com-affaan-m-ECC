"""Episode 12 (TikTok: Part 9): VICTIM vs. OWNER, Part 2 – after the storm.
Same attic (sequel exception), new light: grey dawn and drizzle, then the sun.
The owner's hole is patched. The victim still stands in his drip, facing away from the fix: a stepladder,
a hammer and a plank right behind him. The owner points. He finally turns around, climbs, nails the plank –
the drip stops, the sun comes out, and his label turns from VICTIM to OWNER."""
import sys, math
import numpy as np
from lib import *
import ep11 as E

T_END = 17.2
OFF = 0.3
SHOWN = 9                      # part number on TikTok (internal episode 12)
G, SC, DY, S = E.G, E.SC, E.DY, E.S
H1, H2, LAD = E.H1, E.H2, E.LAD
LAD2 = 705                     # the stepladder behind the victim
TOP2 = G - 280                 # feet height on top of it
TURN = 11.4                    # drip stops, sun breaks through
HITS = [10.45, 10.9, 11.3]
PATCH = 10.3
MORPH = (11.6, 12.3)           # VICTIM -> OWNER
VICTIM_TALK = [(1.0, "Still raining…"), (4.2, "Somebody fix this!")]
OWN_BODY, VIC_BODY = E.OWN_BODY, E.VIC_BODY
NEW_BODY = (236, 214, 178)     # the victim after he owns it
HOOK = "3 days in the same drip.\nThe fix was right behind him."
FOCUS = (700, 1050)            # screen point of the victim under his drip – the opening close-up
CTA = "Part 10 tomorrow:\nthe chair that never gets finished"

# reuse the attic from #11 with this episode's timing and a lighter drizzle
E.TURN = TURN
E.water_lvl = lambda t: 18 + 4 * seg(t, 0, 8)
_rain = E.rain
E.rain = lambda c, t, x0, x1, y0, y1, a, n=120, seed=2: _rain(c, t, x0, x1, y0, y1, a * 0.7, max(10, n // 2), seed)

RUNG0, RUNG = G - 30, 46
def rung_y(k): return RUNG0 - RUNG * k
C_TOP2 = (G - TOP2 - 30) / RUNG


def limb_rung(c, off):
    q = c + off; n = math.floor(q); fr = q - n
    return n + ease(clamp((fr - 0.7) / 0.3))


def climbing2(c):
    """victim on the stepladder (facing right), same reach-checked offsets as ep11.climbing()"""
    reach = {"f": (LAD2 + 8, rung_y(limb_rung(c, 0.0) + 3) + 2), "b": (LAD2 + 2, rung_y(limb_rung(c, 0.5) + 2.5) + 2)}
    kf, kb = limb_rung(c, 0.5), limb_rung(c, 0.0)
    plant = {"f": (LAD2 + 6, rung_y(kf) if kf >= 0 else G), "b": (LAD2 + 0, rung_y(kb) if kb >= 0 else G)}
    p = dict(lean=-4, head=-18, leg_f=20, leg_b=10, knee_f=40, knee_b=30)
    return dict(x=LAD2 - 24, y=rung_y(c) + 40, p=p, f=1, mode="hip", reach=reach, plant=plant)


def hammer_swing(t):
    k = 0.0
    for h in HITS:
        if h - 0.35 < t < h + 0.1: k = ease((t - (h - 0.35)) / 0.35) if t < h else 1 - (t - h) / 0.1
    return clamp(k)


def owner(t):
    base = dict(stand(), head=-4)
    if 6.0 < t < 7.9:                           # points at the stepladder behind him
        k = seg(t, 6.0, 6.3) * (1 - seg(t, 7.6, 7.9))
        o = dict(x=450, y=G, p=mix(base, offer(), k), f=1)
        if k > 0.3: o["reach"] = {"f": (lerp(470, 518, k), G - 160)}
        return o
    if TURN + 0.6 < t:                          # hops for him, until the end (keeps the end card alive)
        ph = (t - TURN - 0.6) / 0.62
        hop = max(0.0, math.sin(ph * math.pi)) if int(ph) % 2 == 0 else 0.0
        return dict(x=450, y=G - 40 * hop, p=cheer(t), f=1)
    return dict(x=450, y=G, p=dict(base, lean=math.sin(t * 1.7) * 3, head=-4 + 6 * math.sin(t * 0.9)), f=1)


def victim(t):
    base = arms_crossed(head=-8)
    if t < 7.6:                                 # stands in his drip, facing away from the fix
        for ts, _ in VICTIM_TALK:
            if ts < t < ts + 1.8:
                k = seg(t, ts, ts + 0.25) * (1 - seg(t, ts + 1.5, ts + 1.8))
                return dict(x=650, y=G, p=mix(base, shrug(1.0), k), f=-1)
        return dict(x=650, y=G, p=dict(base, lean=-4 + math.sin(t * 2) * 2), f=-1)
    if t < 8.1:                                 # turns around – sees the ladder and the hammer
        return dict(x=650, y=G, p=mix(base, dict(stand(), head=12), seg(t, 7.6, 7.9)), f=lerp(-1, 1, seg(t, 7.6, 8.0)))
    if t < 8.7:                                 # steps over and takes the hammer from the step
        k = seg(t, 8.1, 8.45)
        o = dict(x=lerp(650, 668, k), y=G, p=dict(stand(), lean=8, head=6) if k >= 1 else walk(t * 8), f=1)
        o["reach"] = {"f": (LAD2 - 2, rung_y(2) + 4)} if t > 8.3 else None
        return o
    if t < 10.1:                                # climbs, hammer in hand
        return climbing2(C_TOP2 * seg(t, 8.7, 10.1))
    if t < TURN + 0.2:                          # holds the plank to his hole and nails it
        o = climbing2(C_TOP2)
        o["x"] = LAD2 - 14
        o["reach"] = {"b": (H2 + 30, E.roof_y(H2) + 46)}
        k = hammer_swing(t)
        wind, strike = (LAD2 - 10, o["y"] - 200), (H2 + 22, E.roof_y(H2) + 52)
        o["reach"]["f"] = (lerp(wind[0], strike[0], k), lerp(wind[1], strike[1], k)) if t > PATCH else (H2 + 40, E.roof_y(H2) + 60)
        o["p"] = dict(o["p"], head=-26)
        return o
    o = climbing2(C_TOP2)                       # on top of the ladder in the sun: cheers
    o["x"] = LAD2 - 14
    o["reach"] = None
    o["p"] = dict(o["p"], **{k: v for k, v in cheer(t).items() if k.startswith(("arm", "elb"))}, head=-10)
    return o


def stepladder(c, glow=0.0, t=0.0):
    top = TOP2 - 12
    for rx, lean in ((LAD2 - 26, -10), (LAD2 + 26, 10)):
        c.drawLine(rx + lean, G + 2, rx, top, P(INK, stroke=12)); c.drawLine(rx + lean, G + 2, rx, top, P((176, 132, 88), stroke=6))
    c.drawLine(LAD2 + 36, G + 2, LAD2 + 26, top + 10, P(INK, 0.8, stroke=8))     # back leg of the A-frame
    for k in range(6):
        ry = rung_y(k)
        if ry < top + 6: break
        c.drawLine(LAD2 - 26, ry, LAD2 + 26, ry, P(INK, stroke=9)); c.drawLine(LAD2 - 26, ry, LAD2 + 26, ry, P((196, 152, 100), stroke=4))
    c.drawRect(skia.Rect.MakeXYWH(LAD2 - 34, top - 10, 68, 14), P((150, 110, 74))); c.drawRect(skia.Rect.MakeXYWH(LAD2 - 34, top - 10, 68, 14), P(INK, stroke=4))
    if glow > 0:   # the fix lights up when the owner points at it
        pulse = 0.6 + 0.4 * math.sin(t * 7)
        c.drawCircle(LAD2, rung_y(2), 70, P((255, 210, 120), 0.35 * glow * pulse, blur=22))


def frame(c, t):
    c.save(); c.translate(540, G + DY); c.scale(SC, SC); c.translate(-540, -G)
    u = E.world(c, t)
    # grey-pink dawn light before the sun breaks through
    c.drawRect(skia.Rect.MakeLTRB(-300, 0, W + 300, G), P((190, 170, 200), 0.10 * (1 - u)))
    if u > 0:   # sun shaft through the window, now falling toward the victim's corner
        x, y, w, h = E.WIN
        beam = poly([(x + w, y), (x, y + 20), (420, G), (700, G)])
        sh = skia.GradientShader.MakeLinear([(x + w / 2, y), (560, G)], [C((255, 220, 150), 0.55 * u), C((255, 200, 120), 0.15 * u)])
        c.drawPath(beam, skia.Paint(AntiAlias=True, Shader=sh))
        rng = np.random.default_rng(7)
        for i in range(40):
            k = (rng.uniform(0, 1) + t * rng.uniform(0.08, 0.2)) % 1.0
            px = lerp(lerp(530, 470, rng.uniform(0, 1)), lerp(420, 700, rng.uniform(0, 1)), k) + 12 * math.sin(t * 2 + i)
            c.drawCircle(px, lerp(y + 40, G - 20, k), 2.5, P((255, 240, 200), 0.7 * u))
    E.ladder(c)
    # the owner's hole: patched yesterday, bucket still full
    E.plank(c, H1 + 6, E.roof_y(H1) + 42, -7)
    for k in range(6): c.drawCircle(H1 - 36 + k * 15, E.roof_y(H1) + 42 + k * 1.8, 3.5, P((60, 60, 70)))
    E.bucket(c, H1 + 8, G, 1.0)
    glow = seg(t, 6.2, 6.6) * (1 - seg(t, 8.2, 8.5))
    stepladder(c, glow, t)
    v = smooth(victim, t)
    has_hammer = t > 8.45
    if not has_hammer:                           # hammer hanging on rung 2, plank lying on top
        E.hammer(c, LAD2 - 2, rung_y(2) + 4, 160)
    if t < PATCH: E.plank(c, LAD2 + 4, TOP2 - 28, -3)
    # Owner
    o = smooth(owner, t)
    lo = (1, -0.4) if t < TURN else (1, -1)
    shadow(c, o["x"], o["y"], S, 0.3)
    jo = figure(c, o["x"], o["y"], o["p"], s=S, facing=o["f"], body=OWN_BODY, rim=(lerpc((255, 196, 110), (255, 214, 150), u), 0.6), light=lo,
                reach=o.get("reach"))
    # Victim (becomes an owner)
    m = seg(t, *MORPH)
    body = lerpc(VIC_BODY, NEW_BODY, m)
    hip_mode = v.get("mode") == "hip"
    shadow(c, v["x"], G if hip_mode else v["y"], S, 0.3)
    jv = figure(c, v["x"], v["y"] - (84 * S + 6 if hip_mode else 0), v["p"], s=S, facing=v["f"], body=body,
                rim=(lerpc((170, 200, 255), (255, 210, 150), m), 0.5), light=(-1, -0.6), mode=v.get("mode", "feet"),
                reach=v.get("reach"), plant=v.get("plant"))
    if has_hammer:
        hx, hy = jv["hand_f"]; sx, sy = jv["el_f"]
        E.hammer(c, hx, hy, math.degrees(math.atan2(hx - sx, -(hy - sy))))
    if PATCH <= t:                               # his plank, nailed
        E.plank(c, H2 + 34, E.roof_y(H2) + 42, -7)
        for k in range(min(3, sum(1 for h in HITS if t > h))):
            c.drawCircle(H2 + 4 + k * 18, E.roof_y(H2) + 43 + k * 2, 3.5, P((60, 60, 70)))
    elif t > 10.1:
        E.plank(c, jv["hand_b"][0] - 6, jv["hand_b"][1] - 4, -7)
    for h in HITS:
        if h < t < h + 0.35:
            k = (t - h) / 0.35
            c.drawCircle(H2 + 30, E.roof_y(H2) + 40, 10 + 30 * k, P((230, 210, 180), 0.5 * (1 - k)))
    # his drip – stops once the plank is on
    drip_a = 1 - seg(t, HITS[-1], HITS[-1] + 0.3)
    head_y = jv["head"][1] - 18
    E.drips(c, t, H2, E.roof_y(H2) + 30, head_y if t < 8.1 else G - E.water_lvl(t), drip_a, rate=1.1, seed=4)
    if t < 8.1: c.drawCircle(jv["head"][0], jv["head"][1] - 8, 14, P((180, 210, 240), 0.35))
    E.floodwater(c, t, u)
    # labels: VICTIM turns into OWNER
    plate_label(c, "OWNER", jo["head"][0], jo["head"][1] - 52, AMBER, 0.95)
    lx_, ly_ = jv["head"][0], jv["head"][1] - 52
    if m < 1: plate_label(c, "VICTIM", lx_, ly_, GREY, 0.9 * (1 - m))
    if m > 0:
        pop = 1 + 0.25 * (1 - ease((t - MORPH[0]) / 0.5)) if t < MORPH[0] + 0.5 else 1.0
        c.save(); c.translate(lx_, ly_); c.scale(pop, pop); c.translate(-lx_, -ly_)
        plate_label(c, "OWNER", lx_, ly_, AMBER, 0.95 * m)
        c.restore()
    for ts, txt in VICTIM_TALK:
        if ts < t < ts + 1.9:
            a = seg(t, ts, ts + 0.15) * (1 - seg(t, ts + 1.6, ts + 1.9))
            bubble(c, 600, jv["head"][1] - 170, txt, a, "speech", tail=(jv["head"][0] - 6, jv["head"][1] - 60), size=32,
                   pop=1 + 0.15 * (1 - seg(t, ts, ts + 0.2)))
    c.restore()
    if u > 0: c.drawRect(skia.Rect.MakeWH(W, H), P((255, 190, 110), 0.06 * u))
    vignette(c, 0.42)
    grain(c, t, 0.035)
    end_text(c, t, 13.6, "Blame kept him wet.", "One turn kept him dry.", "Your fix is behind you.", y=1430)


def events():
    ev = [["rain", 0.0, TURN - 0.4]]
    for ts, _ in VICTIM_TALK: ev.append(["pop", ts])
    ev += [["pop", 6.2], ["slide", 7.7]]                       # the owner points / he turns around
    for k in range(2): ev.append(["step", 8.15 + k * 0.2, False])
    for k in range(5): ev.append(["step", 8.8 + k * 0.28, True])
    ev.append(["thud", PATCH])
    for h in HITS: ev.append(["thud", h])
    ev += [["sunrise", TURN - 1.0], ["summit", MORPH[0]], ["text", 13.6], ["text2", 14.4]]
    return ev


def overlay(c, t):
    series_overlay(c, t, SHOWN, HOOK, 15.0 - OFF, 380, None, CTA)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or [0.5, 4.6, 6.8, 7.8, 8.4, 9.4, 10.6, 11.9, 12.6, 14.2, 15.2, 16.6]
        def opening(c, t):
            zf = 1 + 0.6 * (1 - ease(t / 1.1)); c.save(); c.translate(*FOCUS); c.scale(zf, zf); c.translate(-FOCUS[0], -FOCUS[1])
            frame(c, t + OFF); c.restore(); overlay(c, t)
        stills(opening, ts, "check/ep12")
    elif cmd == "qa":
        probs = figure_qa(lambda c, t: frame(c, t + OFF), T_END - OFF, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs))
    else:
        finish_v2("Folge12_OwnerPart2", frame, T_END, events(), TURN, SHOWN, HOOK, OFF, 15.0, cta=CTA, focus=FOCUS)
