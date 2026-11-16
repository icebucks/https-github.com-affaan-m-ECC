"""SPACE #2 – The 5 biggest moons in the Solar System (format: RANK, countdown 5 -> 1)
Facts (checked 16.11.2026): mean diameters – Ganymede 5,268 km (NASA JPL Ganymede fact sheet; largest moon, larger than Mercury) ·
Titan 5,150 km (NASA Science: second-largest moon, larger than Mercury, dense atmosphere) · Callisto 4,821 km (NASA Science Callisto facts) ·
Io 3,643 km (NASA Science Io facts; most volcanically active world in the Solar System) · Moon 3,475 km (NASA Moon facts) ·
Mercury 4,879 km (NASA Mercury facts). Pinned answer: Io, Callisto and Ganymede orbit Jupiter."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import vshort as V
from vshort import body, big, counter, P, GOLD, WHITE, MUTED, BLUE, RED, lib, clamp, seg, ease, skia, burst

CX, CY = V.SX, 780
MOONS = [("OUR MOON", "moon", 3475), ("IO", "io", 3643), ("CALLISTO", "callisto", 4821), ("TITAN", "titan", 5150), ("GANYMEDE", "ganymede", 5268)]
MERCURY = 4879
K = 205 / 2634            # px per km of radius: Ganymede gets r = 205


def dashed_circle(c, x, y, r, col, a):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=5, Color=skia.Color4f(col[0] / 255, col[1] / 255, col[2] / 255, a),
                   PathEffect=skia.DashPathEffect.Make([22, 14], 0))
    c.drawCircle(x, y, r, p)


def row(c, t, upto, y=1150):
    """the moons already counted, small, in a row under the stage"""
    for k in range(upto):
        name, kind, d = MOONS[k]
        x = 130 + k * 165
        body(c, kind, x, y, d / 2 * K * 0.17, t)
        lib.text(c, name.replace("OUR ", ""), x, y + 52, lib.F_CAP, 28, MUTED, 1.0, stroke=6)


def hook(c, t, u, b):
    rm = MERCURY / 2 * K * 0.85; rg = 5268 / 2 * K * 0.85
    body(c, "mercury", 265, CY + 40, rm, t)
    lib.text(c, "MERCURY (PLANET)", 265, CY + 40 + rm + 50, lib.F_CAP, 32, WHITE, 1.0, stroke=8)
    a = 1.0
    pul = 0.5 + 0.5 * math.sin(t * 5)
    g = skia.GradientShader.MakeRadial((680, CY + 40), rg * 1.6, [V.C(GOLD, 0.55 + 0.2 * pul), V.C(GOLD, 0.0)], [0.3, 1.0])
    c.drawCircle(680, CY + 40, rg * 1.6, skia.Paint(Shader=g, AntiAlias=True))
    c.drawCircle(680, CY + 40, rg, P((60, 50, 90), a)); dashed_circle(c, 680, CY + 40, rg, GOLD, a)
    lib.text(c, "?", 680, CY + 95, lib.F_CAP, 160, GOLD, a, stroke=16)
    lib.text(c, "MOON", 680, CY + 40 + rg + 50, lib.F_CAP, 34, GOLD, a, stroke=8)


def rank(i):
    name, kind, d = MOONS[i]

    def scene(c, t, u, b):
        r = d / 2 * K
        rm = MERCURY / 2 * K
        if i >= 2:      # Mercury as a dashed outline from No. 3 on
            beat = i == 3 and u > 0.35
            col = RED if beat else MUTED
            dashed_circle(c, CX, CY, rm, col, 0.9)
            lib.text(c, "MERCURY", CX + rm * 0.72, CY - rm * 0.78, lib.F_CAP, 30, col, 0.95, align="left", stroke=7)
        k = V.dlib._back(clamp(u / 0.14)) * (1 + 0.035 * math.sin(t * 3.1))
        g = skia.GradientShader.MakeRadial((CX, CY), r * 1.7, [V.C(BLUE, 0.35), V.C(BLUE, 0.0)], [0.5, 1.0])
        c.drawCircle(CX, CY, r * 1.7 * k, skia.Paint(Shader=g, AntiAlias=True))
        body(c, kind, CX + 8 * math.sin(t * 1.3), CY + 10 * math.sin(t * 1.7), r * k, t)
        lt = b["start"] + 0.3 * (b["end"] - b["start"])
        big(c, counter(d, clamp(u / 0.3)) + " km", CX, CY + 290, 68, GOLD, seg(u, 0.02, 0.08), t, land=lt)
        if i == 3:
            burst(c, t, b["start"] + 0.35 * (b["end"] - b["start"]), CX + rm, CY, n=26, col=GOLD)
            a = seg(u, 0.35, 0.45)
            if a > 0:
                rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(CX - 250, CY - r - 92, 500, 60), 30, 30)
                c.drawRRect(rr, P(RED, 0.95 * a))
                lib.text(c, "BIGGER THAN A PLANET", CX, CY - r - 50, lib.F_CAP, 34, WHITE, a)
        row(c, t, i)
    return scene


def final(c, t, u, b):
    s = 0.46; gap = 26
    rs = [d / 2 * K * s for _, _, d in MOONS]
    total = sum(2 * r for r in rs) + gap * 4
    x = CX - total / 2
    for (name, kind, d), r in zip(MOONS, rs):
        x += r
        body(c, kind, x, CY + 20, r, t)
        lib.text(c, name.replace("OUR ", ""), x, CY + 20 + 100 + 40, lib.F_CAP, 28, WHITE, 1.0, stroke=6)
        x += r + gap
    a = seg(u, 0.25, 0.4)
    lib.text(c, "?", CX, CY - 140, lib.F_CAP, 130, GOLD, a, stroke=16)


SPEC = dict(
    num=2, name="SS2_BiggestMoons", style="synthwave", bpm=112, tint=(24, 40, 96), speed=1.08,
    title="The 5 biggest moons in the Solar System",
    hook=("Your *Moon* is only *No. 5*", "2 moons beat a *planet*"),
    beats=[
        (hook, "Your Moon is only number five. Which two moons are bigger than a planet, and why have you never heard of them?", dict()),
        (rank(0), "Number five: our own Moon. {3,475|three thousand four hundred seventy-five} kilometers.", dict(head="*No. 5* · OUR MOON")),
        (rank(1), "Number four: Io, the most volcanic world we know.", dict(head="*No. 4* · IO")),
        (rank(2), "Number three: Callisto. {4,821|four thousand eight hundred twenty-one} kilometers, almost as big as Mercury.", dict(head="*No. 3* · CALLISTO")),
        (rank(3), "Number two: Titan. {5,150|five thousand one hundred fifty} kilometers. Bigger than the planet Mercury.", dict(head="*No. 2* · TITAN", drop=True)),
        (rank(4), "And number one: Ganymede. {5,268|five thousand two hundred sixty-eight} kilometers. The biggest moon of them all.", dict(head="*No. 1* · GANYMEDE")),
        (final, "Three of these five orbit the same planet. Which one? Tell me before it loops.", dict(head="WHICH *PLANET*?")),
    ],
    question=("3 of these 5 moons", "orbit the *same planet*.", "Which one?"),
    cover=(36.0, [("OURS IS", 140), ("*5TH*", 210)]),
)

if __name__ == "__main__":
    V.main(SPEC)
