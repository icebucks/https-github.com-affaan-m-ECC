"""SPACE #4 – Saturn would float in water (format: WHAT IF, thought experiment with real numbers)
Facts (NASA NSSDC Saturn Fact Sheet, nssdc.gsfc.nasa.gov/planetary/factsheet/saturnfact.html, last updated 18 Mar 2025;
JPL Horizons physical data for Saturn 699; NASA Science "Saturn: Facts" – checked 18.11.2026):
  mean density 687 kg/m³ = 0.687 g/cm³ (Horizons: 0.687 ± 0.001) · water 1 g/cm³
  mass 568.32 ×10^24 kg = 95.16 Earths · volume 82,713 ×10^10 km³ = 763.59 Earths (≈ 764)
  equatorial radius (1 bar) 60,268 km -> diameter 120,536 km · ratio to Earth 9.449 -> "about 9.4 Earths across"
  NASA Science: "Saturn is the only planet in our solar system with an average density that is less than water."
  Mostly hydrogen and helium (NASA). Floating object: submerged fraction = density ratio = 0.687 (Archimedes, exact).
  Hypothetical – no ocean is that big (said in the video).
Pinned answer: Earth is the densest planet (NSSDC planetary fact sheet: Earth 5,513/5,514 kg/m³ > Mercury 5,429 > Venus 5,243).
Not used: Earth's density value (already in SS3), any gravity value, any travel/day/light numbers (reserved for long videos)."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import vshort as V
from vshort import body, big, bar, counter, P, GOLD, WHITE, MUTED, BLUE, RED, lib, clamp, seg, ease, skia, burst

CX, CY = V.SX, V.SY
SAT = (230, 205, 150)
WATER = (60, 150, 230)
VIOLET = (190, 150, 255)


def at(b, f):
    return b["start"] + f * (b["end"] - b["start"])


def ocean(c, t, y, x0=-60, x1=1140, a=0.9, amp=10):
    """water surface with moving waves, filled down to the bottom of the stage"""
    p = skia.Path(); p.moveTo(x0, 1260)
    for k in range(61):
        x = x0 + (x1 - x0) * k / 60
        p.lineTo(x, y + amp * math.sin(k * 0.55 + t * 3.2) + 0.5 * amp * math.sin(k * 1.3 - t * 2.1))
    p.lineTo(x1, 1260); p.close()
    sh = skia.GradientShader.MakeLinear([(0, y - 10), (0, 1260)], [V.C(WATER, a), V.C((20, 50, 120), a)], [0, 1])
    c.drawPath(p, skia.Paint(Shader=sh, AntiAlias=True))
    for k in range(7):   # glints
        gx = (k * 170 + t * 60) % (x1 - x0) + x0
        c.drawLine(gx, y + 18 + 6 * (k % 3), gx + 46, y + 18 + 6 * (k % 3), P(WHITE, 0.35 * a, stroke=3))


# ------------------------------------------------------------------ beat 0: the drop
def s_drop(c, t, u, b):
    r = 170
    y = 600 + 210 * ease(clamp(u * 1.1))                     # Saturn lowers toward the sea
    sh = 0.25 + 0.75 * ease(clamp(u * 1.1))
    c.drawOval(skia.Rect.MakeXYWH(CX - r * 1.6 * sh, 1035, r * 3.2 * sh, 40), P((0, 0, 0), 0.25 * sh))
    body(c, "saturn", CX, y, r, t)
    ocean(c, t, 1050)
    lib.text(c, "?", CX + 250, 760, lib.F_CAP, 140, GOLD, seg(u, 0.55, 0.65), stroke=16)
    big(c, "95 EARTHS HEAVY", CX, 1170, 54, WHITE, seg(u, 0.5, 0.6), t, land=at(b, 0.55))


# ------------------------------------------------------------------ beat 1: width, a row of Earths across the equator
def s_width(c, t, u, b):
    r = 300; y = 850
    body(c, "saturn", CX, y, r, t)
    er = r / 9.449
    n = 9.449 * clamp((u - 0.1) / 0.6)
    for k in range(int(math.ceil(n))):
        frac = min(1.0, n - k)
        x = CX - r + er + 2 * er * k
        if frac >= 1: body(c, "earth", x, y, er, t, rot=t * 0.05)
        else:
            c.save(); c.clipRect(skia.Rect.MakeLTRB(x - er, y - er, x - er + 2 * er * frac, y + er))
            body(c, "earth", x, y, er, t, rot=t * 0.05); c.restore()
    c.drawLine(CX - r, y + r + 30, CX + r, y + r + 30, P(GOLD, 0.8, stroke=4))
    for xx in (CX - r, CX + r): c.drawLine(xx, y + r + 15, xx, y + r + 45, P(GOLD, 0.8, stroke=4))
    lib.text(c, counter(120536, clamp((u - 0.1) / 0.6)) + " km", CX, y + r + 88, lib.F_CAP, 46, WHITE, seg(u, 0.05, 0.15), stroke=8)
    big(c, f"{n:.1f}", CX, y + 150, 110, GOLD, seg(u, 0.1, 0.2), t, land=at(b, 0.72))
    lib.text(c, "EARTHS", CX, y + 215, lib.F_CAP, 44, WHITE, seg(u, 0.1, 0.2), stroke=8)


# ------------------------------------------------------------------ beat 2: volume, Earths fill the globe
def s_volume(c, t, u, b):
    r = 300; y = 870
    k = clamp((u - 0.08) / 0.7); k = 1 - (1 - k) ** 2
    n = int(round(764 * k))
    body(c, "saturn", CX, y, r, t, a=0.45)
    c.save(); c.clipPath(skia.Path().addCircle(CX, y, r - 4), doAntiAlias=True)
    d = 2 * r / 28            # 764 tiny Earths on a hex grid, filled bottom-up
    pts = []
    for row in range(40):
        for col in range(40):
            x = CX - r + d / 2 + col * d + (row % 2) * d / 2; yy = y + r - d / 2 - row * d * 0.87
            if (x - CX) ** 2 + (yy - y) ** 2 < (r - d * 0.4) ** 2: pts.append((x, yy))
    pts = pts[:764] if len(pts) >= 764 else pts
    m = int(len(pts) * n / 764)
    for x, yy in pts[:m]:
        c.drawCircle(x, yy, d * 0.42, P(BLUE)); c.drawCircle(x - d * 0.1, yy - d * 0.08, d * 0.2, P((60, 170, 90), 0.9))
    c.restore()
    c.drawCircle(CX, y, r, P(SAT, 0.9, stroke=5))
    big(c, f"{n}", CX, y + 40, 170, GOLD, seg(u, 0.05, 0.12), t, land=at(b, 0.8))
    lib.text(c, "EARTHS", CX, y + 110, lib.F_CAP, 50, WHITE, seg(u, 0.05, 0.12), stroke=10)


# ------------------------------------------------------------------ beat 3 (drop): space vs weight
def s_mass(c, t, u, b):
    x0, w = 150, 660
    a1 = seg(u, 0.0, 0.08)
    lib.text(c, "SPACE", x0, 700, lib.F_CAP, 44, WHITE, a1, align="left", stroke=8)
    bar(c, x0, 720, w, 60, 1.0, BLUE, a1)
    lib.text(c, "764 EARTHS", x0 + w - 10, 765, lib.F_CAP, 40, (10, 20, 40), a1, align="right")
    k = clamp((u - 0.12) / 0.4); k = 1 - (1 - k) ** 3
    a2 = seg(u, 0.1, 0.18)
    lib.text(c, "WEIGHT", x0, 900, lib.F_CAP, 44, WHITE, a2, align="left", stroke=8)
    bar(c, x0, 920, w, 60, 95.16 / 763.59 * k, GOLD, a2)
    big(c, f"{int(round(95 * k))} EARTHS", x0 + w * 95.16 / 763.59 * k + 190, 968, 56, GOLD, a2, t, land=at(b, 0.55))
    lib.text(c, "1/8 of what 764 Earths would weigh", CX, 1100, lib.F_SANS, 34, MUTED, seg(u, 0.6, 0.7), stroke=6)
    if u > 0.55: burst(c, t, at(b, 0.55), x0 + w * 0.125, 950, n=22, col=GOLD)


# ------------------------------------------------------------------ beat 4: density, a cube of "Saturn" floats in a tank
def s_density(c, t, u, b):
    tx0, tx1, ty0, ty1 = 170, 790, 700, 1150
    lvl = 880
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(tx0, ty0, tx1, ty1), 18, 18), P(WHITE, 0.08))
    c.save(); c.clipRect(skia.Rect.MakeLTRB(tx0 + 6, ty0, tx1 - 6, ty1 - 6)); ocean(c, t, lvl, tx0, tx1, 0.85, 6); c.restore()
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(tx0, ty0, tx1, ty1), 18, 18), P((200, 220, 255), 0.8, stroke=6))
    s = 250
    drop_k = ease(clamp((u - 0.1) / 0.3))
    bob = 6 * math.sin(t * 2.6) * seg(u, 0.4, 0.5)
    sub = 0.687 * s                                            # Archimedes: 68.7 % under water
    y_top = lerp_(560, lvl - (s - sub), drop_k) + bob
    cx = (tx0 + tx1) / 2
    cube = skia.Rect.MakeXYWH(cx - s / 2, y_top, s, s)
    sh = skia.GradientShader.MakeLinear([(cx - s / 2, y_top), (cx + s / 2, y_top + s)], [V.C((250, 225, 170)), V.C((200, 160, 100))], [0, 1])
    c.drawRRect(skia.RRect.MakeRectXY(cube, 14, 14), skia.Paint(Shader=sh, AntiAlias=True))
    c.drawRRect(skia.RRect.MakeRectXY(cube, 14, 14), P((60, 40, 20), 1.0, stroke=5))
    lib.text(c, "SATURN", cx, y_top + 70, lib.F_CAP, 38, (60, 40, 20), 1.0)
    lib.text(c, "0.687", cx, y_top + 118, lib.F_CAP, 44, (60, 40, 20), 1.0)
    lib.text(c, "g/cm³", cx, y_top + 156, lib.F_CAP, 30, (60, 40, 20), 1.0)
    a = seg(u, 0.45, 0.55)
    lib.text(c, "WATER  1.0 g/cm³", cx, ty1 - 30, lib.F_CAP, 40, WHITE, a, stroke=10)
    big(c, "IT FLOATS", cx, 650, 70, GOLD, seg(u, 0.5, 0.58), t, land=at(b, 0.55))


def lerp_(a, b_, k): return a + (b_ - a) * k


# ------------------------------------------------------------------ beat 5: the only planet that floats – H and He
def s_float(c, t, u, b):
    r = 230
    sea = 980
    lo, hi = 0.0, 2.0                                              # Archimedes: 68.7 % of the sphere's volume under water
    for _ in range(30):
        h = (lo + hi) / 2
        if h * h * (3 - h) / 4 < 0.687: lo = h
        else: hi = h
    y = sea + (h - 1) * r + 8 * math.sin(t * 1.8)
    body(c, "saturn", CX, y, r, t)
    ocean(c, t, sea, a=0.82, amp=12)
    for k, (sym, dx, dy) in enumerate((("H", -120, -80), ("He", 60, -120), ("H", 130, 10), ("H", -40, 20), ("He", -150, 40))):
        a = seg(u, 0.2 + 0.08 * k, 0.28 + 0.08 * k)
        yy = y + dy - 30 * math.sin(t * 1.5 + k)
        c.drawCircle(CX + dx, yy, 34, P((30, 20, 60), 0.75 * a)); c.drawCircle(CX + dx, yy, 34, P(VIOLET, a, stroke=3))
        lib.text(c, sym, CX + dx, yy + 12, lib.F_CAP, 34, WHITE, a)
    if sys.argv[1:2] != ["cover"]:          # the thumbnail words sit here
        big(c, "H + He", CX, 650, 80, VIOLET, seg(u, 0.3, 0.38), t, land=at(b, 0.35))
    lib.text(c, "(if an ocean were big enough)", CX, 1150, lib.F_SANS, 32, MUTED, seg(u, 0.55, 0.65), stroke=6)


# ------------------------------------------------------------------ beat 6: question – which planet is the densest?
PLANETS = [("mercury", 0.38), ("venus", 0.95), ("earth", 1.0), ("mars", 0.53), ("jupiter", 2.4), ("saturn", 2.0), ("uranus", 1.5), ("neptune", 1.45)]


def s_question(c, t, u, b):
    zq = ease(clamp((t - b["start"]) / 7.0))
    c.save(); c.translate(CX, 880); c.scale(1 + 0.25 * zq, 1 + 0.25 * zq); c.rotate(-6 * zq); c.translate(-CX, -880)
    for k in range(14):        # slowly turning rays: keeps the end card alive
        th = math.radians(k * 360 / 14 + t * 40)
        p = skia.Path(); p.moveTo(CX, 880)
        p.lineTo(CX + 1500 * math.cos(th - 0.08), 880 + 1500 * math.sin(th - 0.08))
        p.lineTo(CX + 1500 * math.cos(th + 0.08), 880 + 1500 * math.sin(th + 0.08)); p.close()
        c.drawPath(p, P(GOLD if k % 2 else VIOLET, 0.13 * seg(u, 0.1, 0.3)))
    x = 70
    for k, (kind, rel) in enumerate(PLANETS):
        r = 16 + 21 * math.sqrt(rel)
        a = seg(u, 0.03 * k, 0.03 * k + 0.1)
        yy = 860 + 26 * math.sin(t * 2.4 + k)
        body(c, kind, x + r, yy, r, t, a)
        lib.text(c, "?", x + r, yy - r - 26, lib.F_CAP, 46, GOLD, a * (0.6 + 0.4 * math.sin(t * 4 + k)), stroke=8)
        x += 2 * r + 10
    c.restore()
    big(c, "DENSEST?", CX, 1090, 80, GOLD, seg(u, 0.25, 0.32), t, land=at(b, 0.3))


SPEC = dict(
    num=4, name="SS4_SaturnFloats", style="lofi", bpm=86, tint=(50, 30, 90), speed=1.05,
    title="Saturn would float in water",
    hook=("Drop *Saturn* in the ocean?", "*95* Earths heavy … it floats"),
    beats=[
        (s_drop, "What if you dropped Saturn into an ocean? You'd lose that bet: it weighs {95|ninety-five} Earths and would never sink. Why?", dict()),
        (s_width, "Saturn is over {120,000 km|a hundred and twenty thousand kilometers} wide: {9.4|nine point four} Earths across.", dict(head="*9.4* EARTHS ACROSS")),
        (s_volume, "About {764|seven hundred sixty-four} Earths would fill it.", dict(head="*764* EARTHS FILL IT")),
        (s_mass, "The twist: all that weighs only {95|ninety-five} Earths.", dict(head="ONLY *95* EARTHS OF WEIGHT", drop=True)),
        (s_density, "A cubic centimeter of Saturn: just {0.687|zero point six eight seven} grams. Water: one. So it floats.", dict(head="*0.687* g/cm³ · WATER *1.0*")),
        (s_float, "It's the only planet less dense than water: mostly hydrogen and helium.", dict(head="THE *ONLY* PLANET THAT FLOATS")),
        (s_question, "Your turn: which planet is the densest?", dict(head="WHICH IS *DENSEST*?")),
    ],
    question=("Saturn would float.", "Which planet is the", "*densest of all*?"),
    cover=(31.0, [("IT", 170), ("*FLOATS*", 230)]),
)

if __name__ == "__main__":
    V.main(SPEC)
