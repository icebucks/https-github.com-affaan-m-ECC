"""SPACE #3 – Earth vs. the Moon in 3 rounds (format: VS, duel in 3 rounds + scoreboard)
Facts (NASA NSSDC Moon Fact Sheet, nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html, last updated 11 Jan 2024; checked 17.11.2026):
  Moon/Earth ratios – volume 0.0203 (2.1968 vs 108.321 ×10^10 km³) -> 1/0.0203 ≈ 49 Moons fill Earth's volume ·
  mass 0.0123 (0.07346 vs 5.9722 ×10^24 kg) -> ≈ 81 Moons match Earth's mass ·
  mean density 3,344 vs 5,514 kg/m³ (ratio 0.606 -> "about 60 % as dense") ·
  surface gravity 1.62 vs 9.80 m/s² (ratio 0.165 -> "about one sixth") -> same throw straight up: height = v²/2g -> 9.80/1.62 ≈ 6× higher.
  Moon radius 1,737.4 km / Earth 6,371 km = 0.273 (drawing scale only, not spoken).
Pinned answer (NASA NSSDC Mars Fact Sheet, updated 19 May 2025): Mars/Earth volume ratio 0.151 -> about 6.6 Mars fill Earth (Mars radius 0.53 Earth)."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import vshort as V
from vshort import body, big, bar, counter, fade, P, GOLD, WHITE, MUTED, BLUE, RED, lib, clamp, seg, ease, skia, burst

CX, CY = V.SX, V.SY
MOON_R = 0.273            # Moon radius / Earth radius
MARS_R = 0.532
TEAL = (90, 225, 200)


def scoreboard(c, t, e, m, y=618, flash=None):
    """EARTH e : m MOON pill at the top of the stage; flash = time the last point landed"""
    if sys.argv[1:2] == ["cover"]: return          # the thumbnail text sits here
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(CX - 250, y - 40, 500, 70), 35, 35)
    c.drawRRect(rr, P((6, 20, 24), 0.82))
    c.drawRRect(rr, P(TEAL, 0.55, stroke=3))
    lib.text(c, "EARTH", CX - 150, y + 12, lib.F_CAP, 36, BLUE, 1.0, stroke=6)
    lib.text(c, "MOON", CX + 150, y + 12, lib.F_CAP, 36, MUTED, 1.0, stroke=6)
    k = V.punch(t, flash, 0.4) if flash is not None and t >= flash else 1.0
    c.save(); c.translate(CX, y + 14); c.scale(k, k)
    lib.text(c, f"{e} : {m}", 0, 0, lib.F_CAP, 52, GOLD, 1.0, stroke=8)
    c.restore()


def at(b, f):
    return b["start"] + f * (b["end"] - b["start"])


# ------------------------------------------------------------------ beat 0: face-off
def faceoff(c, t, u, b):
    er = 165; mr = er * MOON_R
    ex, mx, y = 270, 715, 850
    sl = 1 - ease(clamp((t - b["start"]) / 0.45))
    g = skia.GradientShader.MakeRadial((ex, y), er * 1.6, [V.C(BLUE, 0.4), V.C(BLUE, 0.0)], [0.5, 1.0])
    c.drawCircle(ex, y, er * 1.6, skia.Paint(Shader=g, AntiAlias=True))
    body(c, "earth", ex - 120 * sl, y, er, t, rot=t * 0.05)
    body(c, "moon", mx + 120 * sl, y + 6 * math.sin(t * 2), mr, t)
    lib.text(c, "EARTH", ex, y + er + 55, lib.F_CAP, 40, BLUE, 1.0, stroke=8)
    lib.text(c, "MOON", mx, y + mr + 60, lib.F_CAP, 40, WHITE, 1.0, stroke=8)
    big(c, "VS", 525, y + 30, 120, GOLD, seg(u, 0.15, 0.22), t, land=at(b, 0.18))
    lib.text(c, "(to scale)", mx, y - mr - 26, lib.F_CAP, 26, MUTED, 0.9, stroke=6)
    for k in range(3):   # three empty round pips
        x = CX - 90 + k * 90
        c.drawCircle(x, 1150, 16, P(TEAL, 0.9, stroke=4))
        lib.text(c, f"R{k + 1}", x, 1200, lib.F_CAP, 26, MUTED, 0.9, stroke=5)


# ------------------------------------------------------------------ round 1: volume, Earth fills up with Moons
def r1_fill(c, t, u, b):
    er = 235; y = 915
    n = int(round(49 * (1 - (1 - clamp((u - 0.12) / 0.6)) ** 2))) if u > 0.12 else 0
    body(c, "earth", CX, y, er, t, rot=t * 0.05)
    # moon-grey "liquid" rising inside Earth: level = share of the volume filled (by volume: sphere cap)
    frac = n / 49
    lo, hi = 0.0, 2.0          # solve cap height h/r for volume fraction frac
    for _ in range(30):
        h = (lo + hi) / 2
        if h * h * (3 - h) / 4 < frac: lo = h
        else: hi = h
    level = y + er - h * er
    c.save(); c.clipPath(skia.Path().addCircle(CX, y, er), doAntiAlias=True)
    p = skia.Path(); p.moveTo(CX - er, y + er + 2)
    for k in range(41):
        x = CX - er + k * er / 20
        p.lineTo(x, level + 7 * math.sin(k * 0.8 + t * 6))
    p.lineTo(CX + er, y + er + 2); p.close()
    c.drawPath(p, P((205, 205, 212), 0.74))
    c.restore()
    c.drawCircle(CX, y, er, P(WHITE, 0.5, stroke=3))
    # Moons dropping in from above, one per counted step
    mr = er * MOON_R * 0.55
    for k in range(max(0, n - 3), n + 1):
        if k >= 49: continue
        tk = at(b, 0.12 + 0.6 * (1 - math.sqrt(1 - k / 49)))
        q = (t - tk) / 0.35
        if 0 <= q < 1:
            body(c, "moon", CX + 70 * math.sin(k * 2.3), 610 + (level - 610) * ease(q), mr * (1 - 0.4 * q), t, a=1 - q * 0.6)
    big(c, f"{n}", CX, y + 40, 150, GOLD, seg(u, 0.1, 0.16), t, land=at(b, 0.72))
    lib.text(c, "MOONS", CX, y + 100, lib.F_CAP, 44, WHITE, seg(u, 0.1, 0.16), stroke=8)
    won = u > 0.8
    scoreboard(c, t, 1 if won else 0, 0, flash=at(b, 0.8))
    if won: burst(c, t, at(b, 0.8), CX - 150, 630, n=20, col=GOLD)


# ------------------------------------------------------------------ round 2: mass on a balance (the twist)
def r2_scale(c, t, u, b):
    px, py = CX - 70, 760; L = 275
    n = 49 if u < 0.45 else int(49 + 32 * (1 - (1 - clamp((u - 0.45) / 0.35)) ** 2))
    target = -16 * (1 - clamp((n - 49) / 32)) if u > 0.08 else 0      # Earth side (left) down until 81
    ang = math.radians(target + 1.2 * math.sin(t * 4) * (1 - clamp((n - 49) / 32)))
    lx, ly = px - L * math.cos(ang), py - L * math.sin(ang)
    rx, ry = px + L * math.cos(ang), py + L * math.sin(ang)
    # stand
    c.drawRect(skia.Rect.MakeLTRB(px - 10, py, px + 10, 1120), P((150, 160, 175)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(px - 110, 1110, px + 110, 1135), 10, 10), P((150, 160, 175)))
    c.drawLine(lx, ly, rx, ry, P((220, 225, 235), 1.0, stroke=12))
    c.drawCircle(px, py, 18, P(GOLD))
    for x, yy in ((lx, ly), (rx, ry)):
        c.drawLine(x, yy, x - 90, yy + 150, P(WHITE, 0.6, stroke=3)); c.drawLine(x, yy, x + 90, yy + 150, P(WHITE, 0.6, stroke=3))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 120, yy + 150, x + 120, yy + 166), 8, 8), P((200, 205, 215)))
    body(c, "earth", lx, ly + 150 - 82, 80, t, rot=t * 0.05)
    lib.text(c, "1 EARTH", lx, ly + 220, lib.F_CAP, 36, BLUE, 1.0, stroke=8)
    # pile of n small Moons on the right pan (rows of 9)
    mr = 11.5
    for k in range(n):
        row, col = divmod(k, 9)
        x = rx - 4 * 2 * mr * 1.05 + col * 2 * mr * 1.05 + (row % 2) * mr * 0.5
        yy = ry + 150 - mr - row * mr * 1.8
        body(c, "moon", x, yy, mr, t)
    lt = at(b, 0.8)
    big(c, f"{n} MOONS", rx, ry + 225, 58, GOLD if n == 81 else WHITE, 1.0, t, land=lt if n == 81 else None)
    if 0.12 < u < 0.45:
        lib.text(c, "NOT ENOUGH", rx, ry + 285, lib.F_CAP, 38, RED, seg(u, 0.12, 0.18), stroke=8)
    won = u > 0.82
    if n == 81: burst(c, t, lt, px, py, n=26, col=GOLD)
    scoreboard(c, t, 2 if won else 1, 0, flash=at(b, 0.82))


# ------------------------------------------------------------------ why: density, same cube, different weight
def density(c, t, u, b):
    s = 210; y0 = 770
    for k, (name, col, val, x) in enumerate((("EARTH", (90, 130, 200), 5514, 260), ("MOON", (185, 185, 195), 3344, 680))):
        a = seg(u, 0.05 + 0.12 * k, 0.15 + 0.12 * k)
        if a <= 0: continue
        # isometric cube of rock
        top = skia.Path(); top.moveTo(x - s / 2, y0 + 40); top.lineTo(x, y0); top.lineTo(x + s / 2, y0 + 40); top.lineTo(x, y0 + 80); top.close()
        lf = skia.Path(); lf.moveTo(x - s / 2, y0 + 40); lf.lineTo(x, y0 + 80); lf.lineTo(x, y0 + 80 + s * 0.8); lf.lineTo(x - s / 2, y0 + 40 + s * 0.8); lf.close()
        rf = skia.Path(); rf.moveTo(x + s / 2, y0 + 40); rf.lineTo(x, y0 + 80); rf.lineTo(x, y0 + 80 + s * 0.8); rf.lineTo(x + s / 2, y0 + 40 + s * 0.8); rf.close()
        c.drawPath(top, P(tuple(min(255, v + 50) for v in col), a)); c.drawPath(lf, P(col, a)); c.drawPath(rf, P(tuple(int(v * 0.6) for v in col), a))
        lib.text(c, name, x, y0 - 30, lib.F_CAP, 40, BLUE if k == 0 else WHITE, a, stroke=8)
        frac = val / 5514
        bar(c, x - 170, 1060, 340, 34, frac * clamp((u - 0.2) / 0.4), GOLD if k == 1 else BLUE, a)
        lib.text(c, counter(val, clamp((u - 0.2) / 0.4)) + " kg", x, 1150, lib.F_CAP, 50, GOLD if k == 1 else WHITE, a, stroke=8)
    lib.text(c, "1 m³ OF EACH, ON AVERAGE", CX, 1200, lib.F_CAP, 30, MUTED, seg(u, 0.3, 0.4), stroke=6)
    scoreboard(c, t, 2, 0)


# ------------------------------------------------------------------ round 3: gravity, the same throw straight up
def r3_throw(c, t, u, b):
    gy = 1110; H1 = 62           # Earth peak height in px; Moon = 6×
    T1 = 0.55                     # Earth: time up+down in s; Moon takes 6× as long
    ts = max(0.0, t - at(b, 0.12))
    for k, (name, g, x, ground) in enumerate((("EARTH", 1.0, 270, (60, 120, 90)), ("MOON", 6.05, 690, (150, 150, 158)))):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 170, gy, x + 170, gy + 40), 12, 12), P(ground, 0.95))
        lib.text(c, name, x, gy + 32, lib.F_CAP, 34, WHITE, 1.0, stroke=7)
        Tk = T1 * g; Hk = H1 * g
        ph = (ts % Tk) / Tk if ts > 0 else 0.0
        h = 4 * Hk * ph * (1 - ph)
        # peak marker
        c.drawLine(x - 120, gy - Hk - 14, x + 120, gy - Hk - 14, P(GOLD if k else WHITE, 0.6, stroke=3))
        lib.text(c, "1×" if k == 0 else "6×", x + 125, gy - Hk - 2, lib.F_CAP, 40, GOLD if k else WHITE, 1.0, align="left", stroke=8)
        for j in range(1, 6):   # motion trail
            pj = max(0.0, ph - j * 0.025)
            c.drawCircle(x, gy - 14 - 4 * Hk * pj * (1 - pj), 14 - j * 2, P(GOLD, 0.25 - j * 0.04))
        c.drawCircle(x, gy - 14 - h, 15, P(GOLD))
    lib.text(c, "SAME THROW", CX, 1205, lib.F_CAP, 30, MUTED, 1.0, stroke=6)
    won = u > 0.85
    scoreboard(c, t, 3 if won else 2, 0, flash=at(b, 0.85))


# ------------------------------------------------------------------ verdict + question
def verdict(c, t, u, b):
    er = 160; y = 850
    zq = ease(seg(t, SPEC["q_at"] - 0.5, SPEC["t_end"]))   # slow push-in on the winner under the end card
    c.save(); c.translate(CX, y); c.scale(1 + 0.35 * zq, 1 + 0.35 * zq); c.rotate(-8 * zq); c.translate(-CX, -y)
    ra = seg(u, 0.05, 0.2)                                   # winner's sun-rays, turning (keeps the end card alive)
    if ra > 0:
        for k in range(14):
            th = math.radians(k * 360 / 14 + t * 48)
            p = skia.Path(); p.moveTo(290, y)
            p.lineTo(290 + 1400 * math.cos(th - 0.09), y + 1400 * math.sin(th - 0.09))
            p.lineTo(290 + 1400 * math.cos(th + 0.09), y + 1400 * math.sin(th + 0.09)); p.close()
            c.drawPath(p, P(GOLD if k % 2 else TEAL, 0.16 * ra))
    pul = 0.5 + 0.5 * math.sin(t * 4)
    g = skia.GradientShader.MakeRadial((290, y), er * 1.7, [V.C(GOLD, 0.35 + 0.15 * pul), V.C(GOLD, 0.0)], [0.4, 1.0])
    c.drawCircle(290, y, er * 1.7, skia.Paint(Shader=g, AntiAlias=True))
    oa = t * 2.4                                               # the Moon keeps orbiting the winner (motion under the end card)
    ox, oy = 290 + 260 * math.cos(oa), y + 110 * math.sin(oa)
    if math.sin(oa) < 0: body(c, "moon", ox, oy, er * MOON_R * 1.3, t)
    body(c, "earth", 290, y, er, t, rot=t * 0.05)
    if math.sin(oa) >= 0: body(c, "moon", ox, oy, er * MOON_R * 1.3, t)
    lo = 1 - seg(t, SPEC["q_at"] - 0.3, SPEC["q_at"])      # labels make room for the end card
    lib.text(c, "WINNER", 290, y + er + 60, lib.F_CAP, 44, GOLD, lo, stroke=8)
    a = seg(u, 0.35, 0.45)
    mr = er * MARS_R
    if a > 0:
        c.drawCircle(700, y + 60 + 14 * math.sin(t * 2.5), mr, P((60, 40, 40), a))
        my = y + 60 + 14 * math.sin(t * 2.5)
        body(c, "mars", 700, my, mr, t, a * 0.55)
        lib.text(c, "?", 700, my + 40, lib.F_CAP, 120, GOLD, a, stroke=14)
        lib.text(c, "MARS", 700, y + 60 + mr + 50, lib.F_CAP, 36, RED, a * lo, stroke=8)
    c.restore()
    scoreboard(c, t, 3, 0)


SPEC = dict(
    num=3, name="SS3_EarthVsMoon", style="trap", bpm=144, tint=(20, 70, 70), speed=1.06,
    title="Earth vs the Moon in 3 rounds",
    hook=("*49* Moons fill Earth.", "But it takes *81* to match it"),
    beats=[
        (faceoff, "Earth versus the Moon: you'd never guess why {49|forty-nine} Moons fill Earth, but {81|eighty-one} match its weight. Which one wins?", dict()),
        (r1_fill, "Round one, size. About {49|forty-nine} Moons would fill Earth's volume. Point, Earth.", dict(head="ROUND 1 · SIZE · *49*")),
        (r2_scale, "Round two, weight. Now the weird part: on a scale, those {49|forty-nine} Moons still lose. You need {81|eighty-one}.", dict(head="ROUND 2 · WEIGHT · *81*", drop=True)),
        (density, "Why? The Moon is only about {60%|sixty percent} as dense as Earth. Same cube, far less weight.", dict(head="ONLY *60%* AS DENSE")),
        (r3_throw, "Round three, gravity. The Moon pulls about {1/6|one sixth} as hard. The same throw flies {6x|six times} higher.", dict(head="ROUND 3 · GRAVITY · *1/6*")),
        (verdict, "Earth wins, {3–0|three, nil}. Your turn: how many planets the size of Mars would fill the Earth?", dict(head="EARTH WINS *3 : 0*")),
    ],
    question=("Earth wins 3 : 0.", "Guess: how many *Mars-size*", "*planets* fill the Earth?"),
    cover=(19.2, [("*81*", 230), ("NOT 49", 150)]),
)

if __name__ == "__main__":
    V.main(SPEC)
