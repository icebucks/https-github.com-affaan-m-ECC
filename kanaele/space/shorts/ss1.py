"""SPACE #1 – How many Earths fit in the Sun? (format: SCALE FILL)
Facts (NASA Sun facts, science.nasa.gov/sun/facts; NASA Jupiter facts; NASA planetary fact sheets, checked 16.11.2026):
  1.3 million Earths fill the Sun's volume · Sun ≈ 109 Earths wide · Sun = 99.8 % of the Solar System's mass ·
  ~1,000 Earths fit inside Jupiter · Sun diameter 1,391,400 km / Jupiter 139,820 km ≈ 10 · Earth volume / Moon volume ≈ 49 (pinned answer)."""
import os, sys, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import vshort as V
from vshort import body, big, bar, fade, P, GOLD, WHITE, MUTED, BLUE, lib, clamp, seg, ease, skia

CX, CY = V.SX, V.SY


def fill(c, t, u, b):
    """Earths raining into the Sun, the tiny real-scale Earth next to it"""
    r = 290
    body(c, "sun", CX, CY + 20, r, t)
    rnd = random.Random(4)
    for i in range(70):
        t0 = rnd.uniform(-1.0, 6.0); sp = rnd.uniform(0.7, 1.2); ang = rnd.uniform(-2.6, -0.5)
        k = (t - t0) * sp
        if 0 < k < 1:
            d = (1 - ease(k)) * rnd.uniform(380, 560)
            x, y = CX + math.cos(ang) * d, CY + 20 + math.sin(ang) * d
            body(c, "earth", x, y, 18 * (1 - 0.7 * k) + 2, t, a=min(1.0, (1 - k) * 3))
    a = seg(u, 0.25, 0.4)
    body(c, "earth", 790, 640, 2.4, t, a)
    if a > 0:
        c.drawCircle(790, 640, 16, P(WHITE, 0.8 * a, stroke=2))
        lib.text(c, "EARTH (to scale)", 790, 600, lib.F_CAP, 28, WHITE, a, stroke=7)


def line(c, t, u, b):
    """109 Earths across the Sun's face"""
    r = 380; y = CY
    body(c, "sun", CX, y, r, t)
    n = 109; er = r / n
    k = int(n * clamp(u / 0.75))
    for i in range(k):
        body(c, "earth", CX - r + er + i * 2 * er, y, er, t)
    c.drawLine(CX - r, y + 18, CX - r + 2 * er * k, y + 18, P(WHITE, 0.8, stroke=3))
    big(c, f"{max(1, k)}", CX, y + 120, 120, WHITE, seg(u, 0.02, 0.1), t, land=b["start"] + 0.75 * (b["end"] - b["start"]) if k == n else None)


def jupiter(c, t, u, b):
    """the biggest planet still only spans a tenth of the Sun"""
    r = 380; y = CY
    body(c, "sun", CX, y, r, t)
    jr = r * 139_820 / 1_391_400
    k = min(10, int(10 * clamp(u / 0.7)) + 1)
    for i in range(k):
        lt = b["start"] + (i / 10) * 0.7 * (b["end"] - b["start"])
        s = V.punch(t, lt, 0.35)
        body(c, "jupiter", CX - r + jr + i * 2 * jr, y, jr * s, t)
    a = seg(u, 0.55, 0.7)
    if a > 0:
        body(c, "jupiter", 230, 1120, 34, t, a)
        lib.text(c, "1 JUPITER ≈ 1,000 EARTHS", 520, 1132, lib.F_CAP, 34, WHITE, a, stroke=8)


def waffle(c, t, frac_fill, zoom=1.0, rest=0.0, ta=1.0):
    """10×10 grid = the Solar System's mass; gold = the Sun"""
    S, G = 56, 6; x0 = CX - (10 * S + 9 * G) / 2; y0 = 590
    last = (x0 + 9 * (S + G) + S * 0.9, y0 + 9 * (S + G) + S / 2)      # the 0.2 % strip
    c.save(); c.clipRect(skia.Rect.MakeLTRB(0, 545, V.W, 1215))
    if zoom > 1:
        c.translate(CX, CY); c.scale(zoom, zoom); c.translate(-last[0], -last[1])
    for i in range(100):
        x = x0 + (i % 10) * (S + G); y = y0 + (i // 10) * (S + G)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, S, S), 8, 8)
        c.drawRRect(rr, P(WHITE, 0.10))
        f = clamp(frac_fill * 100 - i)
        if i == 99: f = min(f, 0.8)
        if f > 0:
            c.save(); c.clipRRect(rr, doAntiAlias=True)
            c.drawRect(skia.Rect.MakeXYWH(x, y, S * f, S), P(GOLD, 0.95))
            c.restore()
    if rest > 0:
        x = x0 + 9 * (S + G) + S * 0.8; y = y0 + 9 * (S + G)
        c.drawRect(skia.Rect.MakeXYWH(x, y, S * 0.2, S), P(BLUE, 0.95 * rest))
        # all the planets live in that strip
        for j, kind in enumerate(["jupiter", "saturn", "neptune", "uranus", "earth", "venus", "mars", "mercury"]):
            body(c, kind, x + S * 0.1, y + 5 + j * 6.4, 1.9 if j < 2 else 1.3, t, rest)
    c.restore()
    return last


def mass(c, t, u, b):
    waffle(c, t, 0.998 * ease(clamp(u / 0.6)))


def rest(c, t, u, b):
    z = 1 + 13 * ease(clamp(u / 0.55))
    waffle(c, t, 0.998, zoom=z, rest=seg(u, 0.0, 0.2))
    a = seg(u, 0.5, 0.62)
    if a > 0:
        for j, ln in enumerate(("EVERY PLANET,", "MOON &", "ASTEROID")):
            lib.text(c, ln, 590, 820 + j * 46, lib.F_CAP, 36, WHITE, a, align="left", stroke=8)


def moons(c, t, u, b):
    er = 150; mr = er * 1737.4 / 6371.0
    body(c, "earth", CX - 60, CY + 10, er, t, rot=t * 0.05)
    body(c, "moon", CX + 230, CY - 150, mr, t)
    a = seg(u, 0.3, 0.45)
    lib.text(c, "?", CX - 60, CY + 50, lib.F_CAP, 150, GOLD, a, stroke=16)
    lib.text(c, "EARTH", CX - 60, CY + er + 60, lib.F_CAP, 34, WHITE, 1, stroke=8)
    lib.text(c, "MOON", CX + 230, CY - 150 + mr + 46, lib.F_CAP, 30, WHITE, 1, stroke=8)


SPEC = dict(
    num=1, name="SS1_SunEarths", style="cinematic", bpm=100, tint=(70, 36, 30), speed=1.04,
    title="How many Earths fit inside the Sun?",
    hook=("You could pour *1.3 MILLION*", "Earths into the *Sun*"),
    beats=[
        (fill, "Before you scroll: you could pour {1.3 million|one point three million} Earths into the Sun. But nobody tells you the weirder part.", dict()),
        (line, "Line Earths up across its face, and you need {109|one hundred and nine} of them.", dict(head="*109* EARTHS ACROSS")),
        (jupiter, "Even Jupiter, a planet that could hold {1,000|a thousand} Earths, fits across the Sun only about ten times.", dict(head="ONLY *10* JUPITERS WIDE")),
        (mass, "Now the weird part. The Sun alone holds {99.8%|ninety-nine point eight percent} of all the mass in our Solar System.", dict(head="*99.8%* OF ALL THE MASS", drop=True)),
        (rest, "Every planet, every moon, every asteroid. All of it together is the last {0.2%|zero point two percent}.", dict(head="EVERYTHING ELSE: *0.2%*")),
        (moons, "So, how many Moons would it take to fill the Earth? Write your guess before it loops.", dict(head="YOUR GUESS?")),
    ],
    question=("How many *Moons*", "would fill the *Earth*?", "Comment your guess!"),
    cover=(2.0, [("*1.3 MILLION*", 150), ("INSIDE", 130)]),
)

if __name__ == "__main__":
    V.main(SPEC)
