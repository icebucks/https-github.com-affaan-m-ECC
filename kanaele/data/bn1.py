"""By The Numbers #1: How long would it take to earn $1 billion?
Exact arithmetic, no estimates:
  $7.25/h (US federal minimum wage), 40 h/week, 52 weeks = $15,080/year -> 66,313 years
  $50,000/year -> 20,000 years · $100,000/year -> 10,000 years · $1,000,000/year -> 1,000 years
  $1 every second, nonstop (365.25 days) = $31,557,600/year -> 31.7 years
Start years counted back from 2026 (rounded)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "beyondexcuses"))
os.environ.setdefault("OUT_DIR", HERE)
from lib import *

T_END = 17.4
ROWS = [  # big label, small label, years, start-year text
    ("$7.25 / hour", "US minimum wage · 40 h a week", 66313, "start ≈ 64,300 BC"),
    ("$50,000 / year", "a solid full-time salary", 20000, "start ≈ 18,000 BC · Ice Age"),
    ("$100,000 / year", "six figures", 10000, "start ≈ 8,000 BC · before the pyramids"),
    ("$1,000,000 / year", "a millionaire's salary", 1000, "start: 1026 AD · Viking age"),
    ("$1 every second", "nonstop – even while you sleep", 31.7, "start: 1994"),
]
R0, RD = 1.0, 2.5           # first row, gap between rows
Y0, YD = 660, 190           # row layout
TURN = R0 + 4 * RD          # last row = the twist (11.0)
GOLD = (255, 200, 80)


def bg(c, t):
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, H)], [C((14, 18, 34)), C((22, 28, 52)), C((10, 12, 24))], [0, 0.55, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    for x in range(0, W + 1, 90):   # faint grid drifting slowly
        c.drawLine(x, 0, x, H, P((255, 255, 255), 0.03, stroke=2))
    off = (t * 20) % 90
    for y in range(-90, H + 90, 90):
        c.drawLine(0, y + off, W, y + off, P((255, 255, 255), 0.03, stroke=2))
    c.drawCircle(540, 1000, 700, P((255, 190, 90), 0.05 + 0.08 * seg(t, TURN, TURN + 1), blur=200))


def years_text(v, final):
    if final < 100: return f"{v:.1f} YEARS"
    return f"{int(round(v)):,} YEARS"


def row(c, t, i):
    big, small, yrs, start = ROWS[i]
    t0 = R0 + i * RD
    if t < t0: return
    y = Y0 + i * YD
    a = seg(t, t0, t0 + 0.25)
    last = i == len(ROWS) - 1
    dim = 1.0 if (last or t < t0 + RD) else 0.55            # older rows step back
    dim *= 1 - 0.75 * seg(t, 14.0, 14.4)                     # make room for the end text
    slide = (1 - ease((t - t0) / 0.35)) * 60
    c.save(); c.translate(-slide, 0)
    # card
    card = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(70, y - 70, 940, y + 86), 22, 22)
    c.drawRRect(card, P((255, 255, 255), 0.06 * a * dim))
    c.drawRRect(card, P(GOLD if last and t > TURN else (255, 255, 255), (0.5 if last and t > TURN else 0.12) * a * dim, stroke=3))
    text(c, big, 100, y - 8, F_CAP, 50, (255, 255, 255), a * dim, align="left", stroke=8)
    text(c, small, 100, y + 30, F_SANS, 24, (170, 180, 205), a * dim, align="left")
    # counter rolls up, slows down at the end
    k = 1 - (1 - clamp((t - t0 - 0.25) / 1.5)) ** 3
    v = yrs * k
    col = GOLD if last else (255, 120, 110)
    text(c, years_text(v, yrs), 915, y - 8, F_CAP, 52, col, a * dim, align="right", stroke=8)
    text(c, start, 915, y + 30, F_SANS, 24, (170, 180, 205), a * dim * seg(t, t0 + 1.5, t0 + 1.8), align="right")
    # log-scale bar
    frac = math.log10(max(yrs, 1.0)) / math.log10(70000)
    bw = 800 * frac * k
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(100, y + 50, 800, 14), 7, 7), P((255, 255, 255), 0.08 * a * dim))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(100, y + 50, max(14, bw), 14), 7, 7), P(col, 0.9 * a * dim))
    c.restore()


def coins(c, t):
    """coin shower after the twist"""
    if t < TURN + 1.4: return
    rng = np.random.default_rng(9)
    for j in range(26):
        x = rng.uniform(60, 920); sp = rng.uniform(380, 620); ph = rng.uniform(0, 1.2)
        yy = -60 + (t - TURN - 1.4 - ph) * sp
        if -60 < yy < 1640 and t - TURN - 1.4 > ph:
            a = 0.85 * (1 - seg(t, 14.0, 14.4))
            c.save(); c.translate(x, yy); c.scale(1, abs(math.cos(t * 6 + j)) * 0.8 + 0.2)
            c.drawCircle(0, 0, 16, P(INK, a)); c.drawCircle(0, 0, 13, P(GOLD, a)); c.restore()


def frame(c, t):
    bg(c, t)
    text(c, "TIME TO EARN  $1,000,000,000", 540, 560, F_SANS, 30, (170, 180, 205), seg(t, 0.6, 1.0) * (1 - seg(t, 14.0, 14.4)), spacing=3)
    for i in range(len(ROWS)): row(c, t, i)
    coins(c, t)
    grain(c, t, 0.025)
    end_text(c, t, 14.4, "Even $1 every second", "takes 31.7 years.", "What's your number?", y=1430)


def events():
    ev = [["pop", R0 + i * RD] for i in range(len(ROWS))]
    ev += [["land", R0 + i * RD + 1.75] for i in range(len(ROWS))]
    ev += [["summit", TURN + 1.6], ["sunrise", TURN - 1.0], ["text", 14.4], ["text2", 15.2]]
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "still":
        stills(lambda c, t: (frame(c, t + 0.3), series_overlay(c, t, 1, "How long to earn $1 BILLION?", 15.7, series="BY THE NUMBERS")),
               [0.6, 3.0, 6.0, 9.5, 12.8, 16.2], os.path.join(HERE, "check_bn1"))
    else:
        finish_v2("BN1_Billion", frame, T_END, events(), TURN, 1, "How long to earn $1 BILLION?", 0.3, 16.0, series="BY THE NUMBERS")
