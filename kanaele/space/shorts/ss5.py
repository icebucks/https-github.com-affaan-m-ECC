"""SPACE #5 – A sugar cube of neutron star (format: ZOOM, from a sugar cube out to the Sun)
Facts (checked 19.11.2026):
  NASA Goddard "Imagine the Universe – Neutron Stars" (imagine.gsfc.nasa.gov/science/objects/neutron_stars1.html):
    "one sugar cube of neutron star material would weigh about 1 trillion kilograms (or 1 billion tons) on Earth –
     about as much as a mountain" · neutron stars are "about 20 kilometers (12.5 miles) across"
    · "the mass of a sun squished down to the size of a city" · the most dense object known (besides black holes)
  NASA Science "Sun: Facts" (science.nasa.gov/sun/facts): the Sun is about 1.4 million km (865,000 miles) across
Exact math: 1,400,000 km / 20 km = 70,000 -> squeeze the Sun 70,000 times narrower.
Not used: 1.4 solar masses or 22–26 km (sources differ), 109 Earths across (already in SS1), anything about light, travel or cold
(reserved for long videos). Pinned answer: whatever you lifted, the sugar cube beats it by about a billion tons."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import vshort as V
from vshort import body, big, bar, counter, P, GOLD, WHITE, MUTED, BLUE, RED, lib, clamp, seg, ease, skia, burst

CX, CY = V.SX, V.SY
ICE = (190, 215, 255)
PINK = (255, 120, 150)


def at(b, f):
    return b["start"] + f * (b["end"] - b["start"])


def cube(c, x, y, s, t, a=1.0, glow=1.0):
    """a glowing sugar cube of neutron-star matter, seen at an angle (front + top + side face)"""
    if a <= 0 or s < 1: return
    c.saveLayerAlpha(None, int(255 * a)) if a < 1 else c.save()
    g = skia.GradientShader.MakeRadial((x, y), s * 2.2, [V.C(ICE, 0.45 * glow), V.C(ICE, 0.0)], [0.2, 1.0])
    c.drawCircle(x, y, s * 2.2, skia.Paint(Shader=g, AntiAlias=True))
    h = s / 2; d = s * 0.35
    front = skia.Rect.MakeLTRB(x - h, y - h + d / 2, x + h, y + h + d / 2)
    top = lib.poly([(x - h, y - h + d / 2), (x - h + d, y - h - d / 2), (x + h + d, y - h - d / 2), (x + h, y - h + d / 2)])
    side = lib.poly([(x + h, y - h + d / 2), (x + h + d, y - h - d / 2), (x + h + d, y + h - d / 2), (x + h, y + h + d / 2)])
    c.drawRect(front, P((235, 242, 255)))
    c.drawPath(top, P((250, 252, 255))); c.drawPath(side, P((170, 190, 230)))
    for pth in (top, side): c.drawPath(pth, P((40, 50, 90), stroke=max(1.5, s * 0.025)))
    c.drawRect(front, P((40, 50, 90), stroke=max(1.5, s * 0.025)))
    rnd = __import__("random").Random(4)
    for k in range(int(10 + s * 0.06)):          # sugar grains sparkling
        gx, gy = x - h + rnd.random() * s, y - h + d / 2 + rnd.random() * s
        c.drawCircle(gx, gy, max(1, s * 0.012), P((150, 170, 220), 0.5 + 0.5 * math.sin(t * 6 + k)))
    c.restore()


def mountain(c, x, y, w, h, a=1.0):
    """a snow-capped mountain silhouette, base centred at (x, y)"""
    if a <= 0: return
    p = lib.poly([(x - w / 2, y), (x - w * 0.18, y - h * 0.72), (x - w * 0.05, y - h * 0.6), (x + w * 0.08, y - h), (x + w / 2, y)])
    c.drawPath(p, P((96, 70, 96), a)); c.drawPath(p, P((30, 20, 40), a, stroke=4))
    snow = lib.poly([(x + w * 0.08, y - h), (x - w * 0.02, y - h * 0.78), (x + w * 0.05, y - h * 0.82), (x + w * 0.1, y - h * 0.75), (x + w * 0.19, y - h * 0.8)])
    c.drawPath(snow, P((210, 205, 225), a))


def pulsar(c, x, y, r, t, a=1.0, beams=True):
    """neutron star: small white-blue sphere, spinning beams"""
    if beams and a > 0:
        ang = t * 2.6
        for s_ in (0, math.pi):
            th = ang + s_
            p = skia.Path(); p.moveTo(x, y)
            L = 900
            p.lineTo(x + L * math.cos(th - 0.06), y + L * math.sin(th - 0.06)); p.lineTo(x + L * math.cos(th + 0.06), y + L * math.sin(th + 0.06)); p.close()
            c.drawPath(p, P((200, 220, 255), 0.22 * a, blur=6))
    body(c, "neutron", x, y, r, t, a)


# ------------------------------------------------------------------ beat 0: the impossible sugar cube
def s_cube(c, t, u, b):
    c.drawRect(skia.Rect.MakeLTRB(-100, 1010, 1180, 1260), P((40, 18, 30), 0.9))           # dark table
    c.drawLine(-100, 1010, 1180, 1010, P(PINK, 0.4, stroke=3))
    s = 190 + 40 * ease(u)
    wob = 4 * math.sin(t * 9) * seg(u, 0.5, 0.6)
    cube(c, CX + wob, 1010 - s / 2 - s * 0.18, s, t)
    lib.text(c, "1 SUGAR CUBE", CX, 1110, lib.F_CAP, 50, WHITE, seg(u, 0.05, 0.15), stroke=10)
    big(c, "?", CX + 230, 760, 130, GOLD, seg(u, 0.55, 0.65), t, land=at(b, 0.6))


# ------------------------------------------------------------------ beat 1: the scale and the mountain
def s_scale(c, t, u, b):
    k = clamp((u - 0.1) / 0.55)
    mountain(c, CX + 40, 1040, 820 * (0.4 + 0.6 * ease(clamp((u - 0.35) / 0.4))), 210 * ease(clamp((u - 0.35) / 0.4)), seg(u, 0.35, 0.45))   # peak stays below the text
    # weighing plate: sinks as the number climbs
    sink = 26 * ease(k)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(CX - 220, 1060 + sink, CX + 220, 1085 + sink), 10, 10), P((150, 160, 190)))
    c.drawRect(skia.Rect.MakeLTRB(CX - 20, 1085 + sink, CX + 20, 1170), P((110, 115, 140)))
    cube(c, CX, 1060 + sink - 70, 110, t)
    lib.text(c, counter(1e12, k) + " kg", CX, 700, lib.F_CAP, 64, WHITE, seg(u, 0.05, 0.12), stroke=12)
    big(c, "= A MOUNTAIN", CX, 790, 66, GOLD, seg(u, 0.6, 0.68), t, land=at(b, 0.62))
    if u > 0.62: burst(c, t, at(b, 0.62), CX, 1000, n=20, col=GOLD)


# ------------------------------------------------------------------ beat 2 (drop): zoom out – the whole star
def s_star(c, t, u, b):
    z = ease(clamp(u / 0.45))
    cube(c, CX, 880, 120 * (1 - z) + 2, t, a=1 - seg(u, 0.35, 0.5))
    r = 40 + 160 * ease(clamp((u - 0.25) / 0.4))
    pulsar(c, CX, 880, r, t, seg(u, 0.25, 0.4))
    a = seg(u, 0.55, 0.65)
    c.drawLine(CX - r, 880 + r + 40, CX + r, 880 + r + 40, P(GOLD, 0.85 * a, stroke=4))
    for xx in (CX - r, CX + r): c.drawLine(xx, 880 + r + 25, xx, 880 + r + 55, P(GOLD, 0.85 * a, stroke=4))
    big(c, "20 km", CX, 880 + r + 105, 70, GOLD, a, t, land=at(b, 0.6))
    body(c, "sun", 210, 680, 46, t, a=seg(u, 0.7, 0.8))
    lib.text(c, "MASS OF", 210, 765, lib.F_CAP, 30, WHITE, seg(u, 0.7, 0.8), stroke=6)
    lib.text(c, "THE SUN", 210, 800, lib.F_CAP, 30, WHITE, seg(u, 0.7, 0.8), stroke=6)


# ------------------------------------------------------------------ beat 3: the size of a city
def skyline(c, x0, x1, base, t, a=1.0):
    rnd = __import__("random").Random(9)
    x = x0
    while x < x1:
        w = rnd.uniform(18, 46); hh = rnd.uniform(40, 190)
        c.drawRect(skia.Rect.MakeLTRB(x, base - hh, min(x1, x + w), base), P((60, 40, 70), a))
        for yy in range(int(base - hh + 10), int(base - 8), 16):
            if rnd.random() < 0.5: c.drawRect(skia.Rect.MakeXYWH(x + 5, yy, 5, 6), P((255, 210, 140), 0.6 * a))
        x += w + rnd.uniform(2, 8)


def s_city(c, t, u, b):
    base = 1090
    rise = 160 * ease(clamp(u / 0.5))   # the star (780 px = 20 km) rises behind a 20 km wide city
    c.save(); c.clipRect(skia.Rect.MakeLTRB(-50, 0, 1130, base - 4))
    pulsar(c, CX, base + 300 - rise, 390, t, seg(u, 0.05, 0.2), beams=False)
    c.restore()
    skyline(c, 90, 870, base, t, seg(u, 0.0, 0.15))
    c.drawLine(60, base, 900, base, P(PINK, 0.5, stroke=3))
    a = seg(u, 0.3, 0.4)
    c.drawLine(90, base + 40, 870, base + 40, P(GOLD, 0.85 * a, stroke=4))
    for xx in (90, 870): c.drawLine(xx, base + 25, xx, base + 55, P(GOLD, 0.85 * a, stroke=4))
    big(c, "20 km = ONE CITY", CX, base + 115, 60, GOLD, a, t, land=at(b, 0.35))


# ------------------------------------------------------------------ beat 4: the Sun, 70,000 times wider
def s_sun(c, t, u, b):
    z = ease(clamp(u / 0.6))
    R = 2400 * (1 - z) + 520 * z
    body(c, "sun", CX + 140 + R * 0.55, 880, R, t)
    pulsar(c, 200, 880, 9, t, 1.0, beams=True)
    a = seg(u, 0.35, 0.45)
    c.drawLine(200, 910, 200, 990, P(GOLD, a, stroke=3)); lib.text(c, "20 km", 200, 1030, lib.F_CAP, 40, GOLD, a, stroke=8)
    big(c, "1.4 MILLION km", CX + 20, 1150, 66, WHITE, seg(u, 0.15, 0.25), t, land=at(b, 0.2))


# ------------------------------------------------------------------ beat 5: question – what's the heaviest thing you've lifted?
def s_question(c, t, u, b):
    zq = ease(clamp((t - b["start"]) / 7.0))
    c.save(); c.translate(CX, 880); c.scale(1 + 0.2 * zq, 1 + 0.2 * zq); c.rotate(6 * zq); c.translate(-CX, -880)
    for k in range(14):
        th = math.radians(k * 360 / 14 + t * 36)
        p = skia.Path(); p.moveTo(CX, 880)
        p.lineTo(CX + 1500 * math.cos(th - 0.08), 880 + 1500 * math.sin(th - 0.08))
        p.lineTo(CX + 1500 * math.cos(th + 0.08), 880 + 1500 * math.sin(th + 0.08)); p.close()
        c.drawPath(p, P(GOLD if k % 2 else PINK, 0.12 * seg(u, 0.1, 0.3)))
    cube(c, CX, 880 + 14 * math.sin(t * 2), 200, t)
    c.restore()
    big(c, "HEAVIEST LIFT?", CX, 1130, 76, GOLD, seg(u, 0.25, 0.32), t, land=at(b, 0.3))


SPEC = dict(
    num=5, name="SS5_NeutronSugarCube", style="cinematic", bpm=100, tint=(90, 24, 40), speed=1.0,
    title="A sugar cube of neutron star",
    hook=("*1 sugar cube* =", "about *1 trillion kg*"),
    beats=[
        (s_cube, "You'd lose any bet against this sugar cube before you touch it: about {1 trillion kg|a trillion kilograms}. What is it made of?", dict()),
        (s_scale, "A neutron star. That's NASA's number for one sugar cube of it, weighed on Earth. About as much as a mountain.", dict(head="*1 TRILLION* KG")),
        (s_star, "Now zoom out. The whole star packs about the mass of our Sun into a ball only {20 km|twenty kilometers} across.", dict(head="THE SUN'S MASS IN *20 KM*", drop=True)),
        (s_city, "That's the size of a city.", dict(head="THE SIZE OF A *CITY*")),
        (s_sun, "Our Sun is about {1.4 million km|one point four million kilometers} wide. Squeeze it {70,000|seventy thousand} times narrower, and every sugar cube weighs a mountain.", dict(head="*70,000x* NARROWER")),
        (s_question, "So what's the heaviest thing you've ever lifted?", dict(head="YOUR *HEAVIEST* LIFT?")),
    ],
    question=("1 sugar cube = *1 billion tons*.", "What's the heaviest thing", "*you've ever lifted*?"),
    cover=(14.2, [("ONE", 170), ("*MOUNTAIN*", 190)]),
)

if __name__ == "__main__":
    V.main(SPEC)
