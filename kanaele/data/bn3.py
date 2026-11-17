"""By The Numbers #3: How long would it take to walk around the Earth? (format E · time comparison)
Exact arithmetic on the equator, 40,075 km (NASA Earth Fact Sheet: equatorial radius 6,378.137 km -> 2*pi*r = 40,075.0 km):
  jet airliner, 900 km/h cruise (Mach ~0.85)  -> 40,075 / 900 = 44.5 hours
  car, 100 km/h nonstop                         -> 400.75 h = 16.7 days
  bike, 20 km/h nonstop                         -> 2,003.75 h = 83.5 days
  walking, 5 km/h nonstop (~1.4 m/s)            -> 8,015 h = 334 days
  walking 5 km/h, 8 hours a day                 -> 8,015 / 8 = 1,001.9 days ≈ 1,002 days = 2.7 years (/365.25)
As if there were a road along the whole equator (no oceans). No light-speed or space comparisons (reserved for Cosmic Scale)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "beyondexcuses"))
os.environ.setdefault("OUT_DIR", HERE)
from lib import *
sys.path.insert(0, HERE)
from dlib import sfx, finish_data, preview, punch, shake, burst, set_bpm, beats, pulse, music, end_card, rich

BPM = 120                   # upbeat, beat = 0.5 s; every event sits on the grid
set_bpm(BPM)
HOOK = ("Jet around Earth: *44.5 hours*.", "How long to *WALK* it?")
STICKY = "WAIT FOR THE WALK"
GOLD = (255, 200, 80)
CX, CY, R = 470, 850, 200   # globe
RX, RY = 285, 66            # equator ring (route)

# kind, label, sub, hours of travel, display value, colour
MODES = [
    ("jet",  "JET  ·  900 km/h",   "cruising speed, nonstop",   44.53,   (44.5, "HOURS"),  (110, 220, 255)),
    ("car",  "CAR  ·  100 km/h",   "nonstop, no fuel stops",    400.75,  (16.7, "DAYS"),   (255, 130, 110)),
    ("bike", "BIKE  ·  20 km/h",   "nonstop, no sleep",         2003.75, (83.5, "DAYS"),   (120, 230, 150)),
    ("walk", "WALK  ·  5 km/h",    "nonstop, no sleep",         8015.0,  (334, "DAYS"),    (215, 160, 255)),
    ("walk", "WALK  ·  8 h a day", "like a real hike",          24045.0, (1002, "DAYS"),   GOLD),
]
APPEAR = [beats(0), beats(4), beats(10), beats(16), beats(20)]   # 0, 2, 5, 8, 10 s
LANDS = [beats(2), beats(6), beats(12), beats(18), beats(24)]     # 1, 3, 6, 9 s / 12 s = drop (bar start)
BUILD = APPEAR[4]           # 10 s: finale starts, drums drop out
DROP = LANDS[4]             # 12 s: 1,002 DAYS lands
YEARS_T = beats(26)         # 13 s: "= 2.7 YEARS"
END_T = beats(29)           # 14.5 s end card
FOLLOW = beats(32)          # 16 s
LOOP_T = beats(33)          # 16.5 s: back to the opening globe
T_END = beats(35)           # 17.5 s


def cur_mode(t):
    i = 0
    for k, a in enumerate(APPEAR):
        if t >= a: i = k
    return i


# ------------------------------------------------------------------ icons
def icon(c, kind, x, y, s, col, a=1.0, t=0.0):
    """small pictogram centred at (x, y), about 60*s px wide"""
    c.save(); c.translate(x, y); c.scale(s, s)
    ink = P((14, 16, 30), a, stroke=4)
    if kind == "jet":
        p = poly([(30, 0), (18, -5), (-4, -5), (-16, -22), (-24, -22), (-14, -5), (-26, -5), (-32, -14), (-37, -14), (-33, 0),
                  (-37, 14), (-32, 14), (-26, 5), (-14, 5), (-24, 22), (-16, 22), (-4, 5), (18, 5)])
        c.drawPath(p, P(col, a)); c.drawPath(p, ink)
    elif kind == "car":
        body = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-32, -8, 32, 12), 7, 7)
        cab = poly([(-18, -8), (-10, -22), (12, -22), (20, -8)])
        c.drawPath(cab, P(col, a)); c.drawPath(cab, ink)
        c.drawRRect(body, P(col, a)); c.drawRRect(body, ink)
        for wx in (-18, 18):
            c.drawCircle(wx, 13, 8, P((30, 30, 40), a)); c.drawCircle(wx, 13, 3.5, P((220, 220, 230), a))
    elif kind == "bike":
        rot = t * 12
        for wx in (-20, 20):
            c.drawCircle(wx, 8, 14, P(col, a, stroke=5))
            c.drawLine(wx + 12 * math.cos(rot), 8 + 12 * math.sin(rot), wx - 12 * math.cos(rot), 8 - 12 * math.sin(rot), P(col, a * 0.7, stroke=2))
        for (x0, y0, x1, y1) in ((-20, 8, -4, -10), (-4, -10, 16, -10), (16, -10, 20, 8), (-4, -10, 2, 8), (2, 8, 16, -10), (-20, 8, 2, 8), (16, -10, 14, -20)):
            c.drawLine(x0, y0, x1, y1, P(col, a, stroke=5))
        c.drawLine(-8, -16, 2, -16, P(col, a, stroke=6))
    else:   # walker
        c.restore(); c.save(); c.translate(x, y)
        if a < 0.02: c.restore(); return
        c.saveLayerAlpha(skia.Rect.MakeXYWH(-80, -80, 160, 160), int(255 * a))
        figure(c, 0, 30 * s, walk(t * 9), s=0.3 * s, facing=1, body=col, rim=(GOLD, 0.4))
        c.restore()
    c.restore()


# ------------------------------------------------------------------ scene
def bg(c, t):
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, H)], [C((40, 52, 140)), C((84, 52, 150)), C((38, 24, 78))], [0, 0.5, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    rng = np.random.default_rng(5)
    for _ in range(90):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 2.4)
        c.drawCircle(x, (y + t * 14) % H, r, P((255, 255, 255), 0.18 + 0.25 * abs(math.sin(t * 0.9 + x))))
    c.drawCircle(CX, CY, 380, P((120, 180, 255), 0.10 + 0.08 * pulse(t, 1, 7), blur=150))


LAND_BLOBS = [(0.3, 0.25, 0.35, 0.22), (1.4, -0.1, 0.45, 0.45), (2.2, 0.35, 0.3, 0.18), (3.3, -0.35, 0.28, 0.3),
              (4.2, 0.15, 0.55, 0.3), (5.3, -0.45, 0.3, 0.2), (5.9, 0.5, 0.25, 0.15)]


def globe(c, t, a=1.0):
    rot = t * 0.55
    clip = skia.Path(); clip.addCircle(CX, CY, R)
    sh = skia.GradientShader.MakeRadial((CX - 60, CY - 70), R * 1.4, [C((80, 170, 255), a), C((30, 90, 200), a), C((14, 36, 110), a)], [0, 0.55, 1])
    c.drawCircle(CX, CY, R, skia.Paint(AntiAlias=True, Shader=sh))
    c.save(); c.clipPath(clip, doAntiAlias=True)
    for lon0, lat, w, h in LAND_BLOBS:            # stylised land masses drifting with the rotation
        lon = (lon0 + rot) % (2 * math.pi)
        if math.cos(lon) < -0.1: continue
        x = CX + R * math.sin(lon) * math.cos(lat); y = CY - R * math.sin(lat)
        sq = max(0.15, math.cos(lon))
        c.drawOval(skia.Rect.MakeXYWH(x - R * w * sq / 2, y - R * h / 2, R * w * sq, R * h), P((90, 200, 120), 0.9 * a))
    for k in range(6):                             # meridians
        lon = (k * math.pi / 6 + rot) % math.pi
        rx = abs(R * math.cos(lon))
        c.drawOval(skia.Rect.MakeLTRB(CX - rx, CY - R, CX + rx, CY + R), P((255, 255, 255), 0.12 * a, stroke=2))
    for lat in (-0.6, -0.3, 0.3, 0.6):
        y = CY - R * math.sin(lat); rx = R * math.cos(lat)
        c.drawLine(CX - rx, y, CX + rx, y, P((255, 255, 255), 0.12 * a, stroke=2))
    c.drawCircle(CX + R * 0.55, CY + R * 0.2, R * 1.1, P((8, 10, 40), 0.35 * a, blur=40))   # night side
    c.restore()
    c.drawCircle(CX, CY, R, P((190, 230, 255), 0.6 * a, stroke=4))


def ring_pt(th):
    """route along the equator: th = 0 at the front, increasing to the right"""
    return CX + RX * math.sin(th), CY + RY * math.cos(th), math.cos(th) >= 0


def route(c, t, back):
    """dashed equator ring (back or front half) and the coloured trail of the current trip"""
    i = cur_mode(t)
    col = MODES[i][5]
    prog = trip(t)
    n = 120
    for k in range(n):
        th0, th1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        x0, y0, f0 = ring_pt(th0); x1, y1, f1 = ring_pt(th1)
        if f0 == back: continue
        done = th1 <= prog * 2 * math.pi + 1e-6
        if done:
            c.drawLine(x0, y0, x1, y1, P(col, 0.95 if not back else 0.45, stroke=9))
        elif k % 2 == 0:
            c.drawLine(x0, y0, x1, y1, P((255, 255, 255), 0.55 if not back else 0.22, stroke=4))


def trip(t):
    """0..1 progress of the current trip around the equator (follows the counter)"""
    i = cur_mode(t)
    a, l = APPEAR[i], LANDS[i]
    k = clamp((t - a - 0.1) / (l - a - 0.1))
    return 1 - (1 - k) ** 3 if i < 4 else k ** 1.6


def traveller(c, t, back):
    i = cur_mode(t)
    th = trip(t) * 2 * math.pi
    if t > LANDS[i]: th += (t - LANDS[i]) * (1.4 if i == 0 else 0.6)   # keeps circling
    x, y, front = ring_pt(th)
    if front == back: return
    kind, col = MODES[i][0], MODES[i][5]
    c.drawCircle(x, y, 34, P(col, 0.35 if not back else 0.15, blur=12))
    icon(c, kind, x, y - (6 if kind != "walk" else 18), 1.0 if not back else 0.7, col, 1.0 if not back else 0.5, t)


def counter(c, t):
    i = cur_mode(t)
    kind, lab, sub, hrs, (val, unit), col = MODES[i]
    a0, l0 = APPEAR[i], LANDS[i]
    a = seg(t, a0, a0 + 0.2) * (1 - seg(t, END_T - 0.4, END_T))
    last = i == len(MODES) - 1
    slide = (1 - ease((t - a0) / 0.3)) * 50
    c.save(); c.translate(slide, 0)
    # mode row with icon
    f = skia.Font(F_CAP, 46); w = f.measureText(lab) + 80
    x0 = 470 - w / 2
    icon(c, kind, x0 + 30, 1100 - (0 if kind != "walk" else 12), 0.9, col, a, t)
    text(c, lab, x0 + 80, 1116, F_CAP, 46, (255, 255, 255), a, align="left", stroke=10)
    # count-up
    k = trip(t)
    v = val * k
    s = f"{v:,.1f}" if val < 100 else f"{int(round(v)):,}"
    pz = punch(t, l0, 0.42 if last else 0.25)
    c.save(); c.translate(470, 1210); c.scale(pz, pz)
    text(c, f"{s} {unit}", 0, 26, F_CAP, 108 if last else 96, GOLD if last or t >= l0 else (255, 255, 255), a, stroke=18)
    c.restore()
    text(c, sub, 470, 1290, F_SANS, 32, (215, 220, 240), a * seg(t, a0 + 0.2, a0 + 0.4), stroke=6)
    c.restore()
    if last and t >= YEARS_T:
        b = seg(t, YEARS_T, YEARS_T + 0.15) * (1 - seg(t, END_T - 0.4, END_T))
        pz = punch(t, YEARS_T, 0.35)
        c.save(); c.translate(470, 600); c.scale(pz, pz)
        rich(c, "= *2.7 YEARS* of walking", 0, 16, 58, b, stroke=14)
        c.restore()


AX0, AX1, AY = 110, 840, 1372
LOG0, LOG1 = 10.0, 50000.0


def ax(h): return AX0 + (AX1 - AX0) * math.log10(h / LOG0) / math.log10(LOG1 / LOG0)


def timeline(c, t):
    """log time axis: every finished trip leaves a marker"""
    a = seg(t, 0.6, 1.0) * (1 - seg(t, END_T - 0.4, END_T))
    if a <= 0: return
    c.drawLine(AX0, AY, AX1, AY, P((255, 255, 255), 0.35 * a, stroke=4))
    for h, lab in ((24, "1 day"), (24 * 30.44, "1 month"), (24 * 365.25, "1 year")):
        x = ax(h)
        c.drawLine(x, AY - 10, x, AY + 10, P((255, 255, 255), 0.55 * a, stroke=3))
        text(c, lab, x, AY + 40, F_SANS, 28, (200, 205, 230), a)
    short = ["44.5 h", "16.7 d", "83.5 d", "334 d", "2.7 y"]
    for i, (kind, lab, sub, hrs, vv, col) in enumerate(MODES):
        if t < LANDS[i]: continue
        pz = punch(t, LANDS[i], 0.6)
        x = ax(hrs)
        c.drawCircle(x, AY, 11 * pz, P(col, a)); c.drawCircle(x, AY, 11 * pz, P((14, 16, 30), a, stroke=3))
        text(c, short[i], x, AY - 24, F_SANS, 28, col, a, stroke=6)


def frame(c, t):
    dx, dy = shake(t, DROP, 22, 0.45)
    zoom = 1 + 0.025 * pulse(t, 4, 3)
    c.save(); c.translate(CX, CY); c.scale(zoom, zoom); c.translate(-CX, -CY)
    c.save(); c.translate(dx, dy)
    scene(c, t)
    burst(c, t, DROP, 470, 1190, 34)
    burst(c, t, DROP + 0.05, CX, CY - R, 22, col=(215, 160, 255), seed=8)
    c.restore(); c.restore()
    if DROP <= t < DROP + 0.16:
        c.drawRect(skia.Rect.MakeWH(W, H), P((255, 240, 210), 0.45 * (1 - (t - DROP) / 0.16)))
    if t >= LOOP_T:     # crossfade back into the opening frame
        k = seg(t, LOOP_T, LOOP_T + 0.5)
        c.saveLayerAlpha(skia.Rect.MakeWH(W, H), int(255 * k))
        scene(c, 0.04 + (t - LOOP_T) * 0.05, loop=True)
        c.restore()
    grain(c, t, 0.02)
    if t < LOOP_T + 0.3:
        end_card(c, t, END_T, "Walk around the Earth:", "*1,002 days*, 8 h a day.", "Would you make it?", y=1110,
                 alpha=1 - seg(t, LOOP_T - 0.2, LOOP_T + 0.2))


def scene(c, t, loop=False):
    bg(c, t)
    dist_a = 1.0 if loop else seg(t, 0.3, 0.6) * (1 - seg(t, YEARS_T - 0.3, YEARS_T))
    rich(c, "EQUATOR  *40,075 km*", 470, 612, 38, dist_a, stroke=8)
    route(c, t, True); traveller(c, t, True)
    globe(c, t)
    route(c, t, False); traveller(c, t, False)
    if loop: return
    counter(c, t)
    timeline(c, t)


def events():
    ev = []
    for i in range(len(MODES) - 1):
        a, l = APPEAR[i], LANDS[i]
        ev += [sfx(a + 0.1, "whoosh-fast-medium", -9), sfx(l - 0.6, "data-countup-short", -11), sfx(l, "data-number-land", -5),
               sfx(l, f"tone-step-{i + 1}", -12)]
    ev += [sfx(BUILD + 0.1, "whoosh-slow-medium", -6), sfx(DROP - 1.6, "data-countup-medium", -9), sfx(DROP, "riser-2s-strong", -4),
           sfx(DROP, "cinematic-drum-big", -1), sfx(DROP, "data-number-land", -2), sfx(DROP + 0.15, "shimmer-medium-bright", -8),
           sfx(YEARS_T, "pop-large-in", -6), sfx(END_T, "whoosh-medium-soft", -8), sfx(LOOP_T, "whoosh-fast-medium", -6),
           music("upbeat", BPM, build=BUILD, drop=DROP, outro=END_T, seed=3)]
    return ev


def step(t): return sum(1 for a in APPEAR if t >= a)


if __name__ == "__main__":
    if sys.argv[1] == "still":
        preview(frame, 3, *HOOK, FOLLOW, [0.05, 0.5, 1.2, 2.0, 3.2, 5.0, 7.2, 9.3, 11.0, 12.1, 13.3, 15.0, 16.2, 17.4],
                os.path.join(HERE, "check_bn3"), sticky=STICKY, hook_end=beats(6), step_fn=step, steps=len(MODES))
    elif sys.argv[1] == "cover":
        import dlib
        def cover_frame(c, t):
            bg(c, t)
            c.save(); c.translate(70, 300); c.translate(CX, CY); c.scale(1.35, 1.35); c.translate(-CX, -CY)
            route(c, t, True); traveller(c, t, True); globe(c, t); route(c, t, False); traveller(c, t, False)
            c.restore()
        dlib.cover(cover_frame, DROP + 0.6, [(" ".join(sys.argv[2:]), 210)], os.path.join(HERE, "Cover_BN3.jpg"), 3)
    else:
        finish_data("BN3_WalkEarth", frame, T_END, events(), BUILD, 3, *HOOK, FOLLOW, sticky=STICKY, hook_end=beats(6),
                    step_fn=step, steps=len(MODES))
