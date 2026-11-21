"""SPACE #6 – 16 sunrises a day on the space station (format: YOU, your day vs an astronaut's day)
Facts (checked 21.11.2026):
  NASA "Space Station Facts and Figures" (nasa.gov/international-space-station/space-station-facts-and-figures):
    the station orbits Earth about every 90 minutes; "in 24 hours, the space station makes 16 orbits of Earth,
    traveling through 16 sunrises and sunsets"
  NASA SVS "HD Earth Views": "Its crew experiences 16 sunrises and sunsets each day" (orbit every 90 minutes)
  (NASA's orbit tutorial notes the exact count is usually a little under 16 – so every figure below is said with "about")
Exact math from 16 a day: a week 16 x 7 = 112 · a year 16 x 365 = 5,840 · 8 h of sleep = 480 min / 90 min = 5.3 orbits -> about 5 sunrises.
Not used: speed or altitude (speed belongs to the long video "How fast are you moving", altitude figures differ by source)."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import vshort as V
from vshort import body, big, bar, counter, P, GOLD, WHITE, MUTED, BLUE, RED, lib, clamp, seg, ease, skia, burst

CX, CY = V.SX, V.SY
SUNC = (255, 196, 90)
TEAL = (110, 220, 230)


def at(b, f):
    return b["start"] + f * (b["end"] - b["start"])


def sun_at(c, x, y, r, a=1.0):
    c.drawCircle(x, y, r * 2.4, P(SUNC, 0.18 * a, blur=r))
    c.drawCircle(x, y, r, P((255, 230, 150), a))


def earth_orbit(c, t, ex, ey, er, orbit_r, n_orbits_per_s, a=1.0, trail=True):
    """Earth with a day/night side (sun on the left), the station circling; returns the station position and whether it is in sunlight"""
    body(c, "earth", ex, ey, er, t, a, rot=t * 0.05)
    # night half (right side, away from the sun)
    c.save(); c.clipPath(skia.Path().addCircle(ex, ey, er), doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(ex, ey - er, ex + er, ey + er), P((4, 6, 20), 0.62 * a))
    c.restore()
    c.drawOval(skia.Rect.MakeLTRB(ex - orbit_r, ey - orbit_r * 0.32, ex + orbit_r, ey + orbit_r * 0.32), P(TEAL, 0.35 * a, stroke=3))
    ang = t * n_orbits_per_s * 2 * math.pi
    sx, sy = ex + orbit_r * math.cos(ang), ey + orbit_r * 0.32 * math.sin(ang)
    lit = math.cos(ang) < 0.15
    if trail:
        for k in range(1, 12):
            a2 = ang - k * 0.08
            c.drawCircle(ex + orbit_r * math.cos(a2), ey + orbit_r * 0.32 * math.sin(a2), 6 - k * 0.4, P(TEAL, a * 0.5 * (1 - k / 12)))
    behind = math.sin(ang) < 0 and abs(math.cos(ang)) * orbit_r < er
    if not behind:
        station(c, sx, sy, 1.0, a, lit)
    return sx, sy, lit


def station(c, x, y, s, a=1.0, lit=True):
    col = (235, 240, 250) if lit else (120, 130, 160)
    c.save(); c.translate(x, y); c.scale(s, s)
    for dx in (-34, 22):
        c.drawRect(skia.Rect.MakeXYWH(dx, -18, 12, 36), P((60, 110, 200), a))
        c.drawRect(skia.Rect.MakeXYWH(dx, -18, 12, 36), P(INK_, a, stroke=2))
    c.drawRect(skia.Rect.MakeXYWH(-22, -4, 44, 8), P(col, a)); c.drawRect(skia.Rect.MakeXYWH(-8, -8, 16, 16), P(col, a))
    c.restore()


INK_ = (14, 16, 30)


# ------------------------------------------------------------------ beat 0: you vs an astronaut
def s_hook(c, t, u, b):
    # left: you on a small hill, one sun rising behind it; right: the station circling the Earth fast
    c.drawCircle(270, 1000, 420, P((255, 160, 80), 0.38, blur=130))           # warm dawn glow (bright, colourful first second)
    c.drawCircle(740, 900, 300, P((90, 170, 255), 0.30, blur=110))
    sun_at(c, 270, 1010 - 230 * seg(u, 0.05, 0.6), 46)
    hill = skia.Path(); hill.addOval(skia.Rect.MakeLTRB(60, 1010, 480, 1130))       # small hill hides the sun before it rises
    c.drawPath(hill, P((44, 70, 58))); c.drawPath(hill, P((90, 130, 100), stroke=4))
    lib.figure(c, 270, 1012, lib.stand(), s=0.75, facing=1, body=(246, 238, 220), rim=(GOLD, 0.5))
    big(c, "YOU: 1", 270, 660, 64, WHITE, seg(u, 0.1, 0.2), t, land=at(b, 0.2))
    earth_orbit(c, t, 740, 900, 120, 190, 0.5)
    big(c, "THEM: 16", 740, 660, 64, GOLD, seg(u, 0.45, 0.55), t, land=at(b, 0.5))


# ------------------------------------------------------------------ beat 1: one orbit every 90 minutes
def s_orbit(c, t, u, b):
    sx, sy, lit = earth_orbit(c, t, CX, 880, 210, 330, 0.18)
    sun_at(c, 110, 880, 34)
    k = clamp((u - 0.1) / 0.6)
    # clock ring counting 90 minutes
    c.drawArc(skia.Rect.MakeXYWH(CX - 380, 880 - 380, 760, 760), -90, 360 * k, False, P(GOLD, 0.6, stroke=8))
    big(c, counter(90, k) + " MIN", CX, 1220, 70, GOLD, seg(u, 0.05, 0.15), t, land=at(b, 0.72))


# ------------------------------------------------------------------ beat 2: 16 sunrises in 24 hours
def s_sixteen(c, t, u, b):
    n = int(16 * clamp((u - 0.05) / 0.7) + 0.0001)
    for i in range(16):                                    # 16 little suns in a 4 x 4 grid, popping in
        gx, gy = 220 + (i % 4) * 170, 640 + (i // 4) * 130
        a = 1.0 if i < n else 0.12
        k = V.punch(t, at(b, 0.05 + 0.7 * (i + 1) / 16), 0.4) if i < n else 1.0
        c.save(); c.translate(gx, gy); c.scale(k, k)
        sun_at(c, 0, 0, 30, a)
        c.restore()
    big(c, f"{n}", CX, 1225, 100, GOLD, 1.0, t, land=at(b, 0.75))
    lib.text(c, "SUNRISES IN 24 HOURS", CX, 1110, lib.F_CAP, 40, WHITE, seg(u, 0.75, 0.85), stroke=8)


# ------------------------------------------------------------------ beat 3 (drop): your week vs theirs
def s_week(c, t, u, b):
    x0, w = 150, 660
    a1 = seg(u, 0.0, 0.1)
    lib.text(c, "YOUR WEEK", x0, 720, lib.F_CAP, 44, WHITE, a1, align="left", stroke=8)
    bar(c, x0, 740, w, 60, 7 / 112, BLUE, a1)
    lib.text(c, "7", x0 + 70, 790, lib.F_CAP, 44, WHITE, a1, align="left", stroke=8)
    k = clamp((u - 0.15) / 0.4); k = 1 - (1 - k) ** 3
    a2 = seg(u, 0.12, 0.2)
    lib.text(c, "AN ASTRONAUT'S WEEK", x0, 920, lib.F_CAP, 44, WHITE, a2, align="left", stroke=8)
    bar(c, x0, 940, w, 60, k, GOLD, a2)
    big(c, f"{int(round(112 * k))}", x0 + w - 70, 1100, 90, GOLD, a2, t, land=at(b, 0.55))
    lib.text(c, "16 x 7", x0, 1100, lib.F_SANS, 34, MUTED, seg(u, 0.6, 0.7), align="left", stroke=6)
    if u > 0.55: burst(c, t, at(b, 0.55), x0 + w - 60, 970, n=24, col=GOLD)


# ------------------------------------------------------------------ beat 4: a whole year
def s_year(c, t, u, b):
    k = clamp((u - 0.05) / 0.7)
    rows, cols = 20, 30                                   # dots: each = 10 sunrises -> 584 dots fill a calendar wall
    n = int(584 * (1 - (1 - k) ** 2))
    for i in range(min(n, rows * cols)):
        x = 130 + (i % cols) * 24; y = 650 + (i // cols) * 24
        c.drawCircle(x, y, 8, P(SUNC, 0.85))
    big(c, counter(5840, k), CX, 1220, 100, GOLD, seg(u, 0.05, 0.12), t, land=at(b, 0.78))
    lib.text(c, "1 dot = 10 sunrises", CX, 1150 + 10 - 30, lib.F_SANS, 32, MUTED, seg(u, 0.1, 0.2), stroke=6)


# ------------------------------------------------------------------ beat 5: sleeping through sunrises
def s_sleep(c, t, u, b):
    # a sleeping bag strapped to the wall, the window flashes day/night every orbit
    win = skia.Rect.MakeXYWH(560, 640, 300, 300)
    ph = (t * 1.2) % 1
    day = ph < 0.5
    c.drawRRect(skia.RRect.MakeRectXY(win, 150, 150), P((255, 200, 120) if day else (10, 14, 40)))
    if day: sun_at(c, 710, 790, 40)
    c.drawRRect(skia.RRect.MakeRectXY(win, 150, 150), P((180, 190, 210), stroke=14))
    bag = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(200, 620, 170, 420), 70, 70)
    c.drawRRect(bag, P((70, 90, 160))); c.drawRRect(bag, P(INK_, stroke=5))
    c.drawCircle(285, 660, 46, P((246, 238, 220))); c.drawCircle(285, 660, 46, P(INK_, stroke=4))
    for k in range(3):
        zz = (t * 0.8 + k / 3) % 1
        lib.text(c, "z", 360 + 60 * zz, 640 - 160 * zz, lib.F_CAP, 40 + 20 * zz, WHITE, 1 - zz, stroke=6)
    big(c, "8 H SLEEP = 5", CX, 1150, 76, GOLD, seg(u, 0.3, 0.4), t, land=at(b, 0.35))
    lib.text(c, "sunrises missed", CX, 1215, lib.F_CAP, 42, WHITE, seg(u, 0.35, 0.45), stroke=8)


# ------------------------------------------------------------------ beat 6: question – how many did you watch?
def s_question(c, t, u, b):
    zq = ease(clamp((t - b["start"]) / 7.0))
    c.save(); c.translate(CX, 880); c.scale(1 + 0.18 * zq, 1 + 0.18 * zq); c.translate(-CX, -880)
    for k in range(14):
        th = math.radians(k * 360 / 14 + t * 30)
        p = skia.Path(); p.moveTo(CX, 880)
        p.lineTo(CX + 1500 * math.cos(th - 0.08), 880 + 1500 * math.sin(th - 0.08))
        p.lineTo(CX + 1500 * math.cos(th + 0.08), 880 + 1500 * math.sin(th + 0.08)); p.close()
        c.drawPath(p, P(GOLD if k % 2 else TEAL, 0.12 * seg(u, 0.1, 0.3)))
    sun_at(c, CX, 880, 90)
    c.restore()
    big(c, "HOW MANY DID YOU SEE?", CX, 1130, 62, GOLD, seg(u, 0.25, 0.32) * (1 - seg(u, 0.55, 0.65)), t, land=at(b, 0.3))   # gone before the end card


SPEC = dict(
    num=6, name="SS6_SixteenSunrises", style="synthwave", bpm=112, tint=(24, 40, 96), speed=1.0,
    title="16 sunrises a day on the space station",
    hook=("You: *365* sunrises a year.", "Astronauts: *5,840*."),
    beats=[
        (s_hook, "You see {365|three hundred sixty-five} sunrises a year. Astronauts see about {5,840|five thousand eight hundred forty}. How many do they sleep through before morning?", dict()),
        (s_orbit, "The space station circles the Earth about every {90 minutes|ninety minutes}.", dict(head="*1* ORBIT · *90* MIN")),
        (s_sixteen, "So in one day, the crew passes through about {16|sixteen} sunrises and sixteen sunsets.", dict(head="*16* SUNRISES A DAY")),
        (s_week, "Your week has seven sunrises. Theirs has about {112|a hundred and twelve}.", dict(head="*7* VS *112*", drop=True)),
        (s_year, "In a year, that's about {5,840|five thousand eight hundred forty} sunrises.", dict(head="*5,840* A YEAR")),
        (s_sleep, "And on a normal eight-hour night, they sleep through about five of them.", dict(head="SLEEPING THROUGH *5*")),
        (s_question, "So be honest: how many sunrises did you actually watch this year?", dict(head="YOUR *SUNRISES*?")),
    ],
    question=("Astronauts: about *16 a day*.", "How many sunrises did", "*you watch this year*?"),
    cover=(28.4, [("*5,840*", 200), ("A YEAR", 150)]),
)

if __name__ == "__main__":
    V.main(SPEC)
