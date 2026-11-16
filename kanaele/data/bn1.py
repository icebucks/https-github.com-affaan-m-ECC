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
sys.path.insert(0, HERE)
from dlib import sfx, finish_data, preview, punch, shake, burst, set_bpm, beats, pulse, music

BPM = 150                   # trap, beat = 0.4 s; every event sits on the grid
set_bpm(BPM)
T_END = beats(40)           # 16.0 s
HOOK = ("How long to earn *$1 BILLION*?", "The last one is *insane*.")
STICKY = "WAIT FOR THE LAST ONE"
END_T = beats(34)           # end text 13.6 s
FOLLOW = beats(37)          # 14.8 s
ROWS = [  # big label, small label, years, start-year text
    ("$7.25 / hour", "US minimum wage · 40 h a week", 66313, "start ≈ 64,300 BC"),
    ("$50,000 / year", "a solid full-time salary", 20000, "start ≈ 18,000 BC · Ice Age"),
    ("$100,000 / year", "six figures", 10000, "start ≈ 8,000 BC · before the pyramids"),
    ("$1,000,000 / year", "a millionaire's salary", 1000, "start: 1026 AD · Viking age"),
    ("$1 every second", "nonstop – even while you sleep", 31.7, "start: 1994"),
]
R0, RD = 0.0, beats(6)      # first row, gap between rows (2.4 s)
LAND = beats(4)             # counter lands 4 beats after a row appears
Y0, YD = 690, 190           # row layout
TURN = R0 + 4 * RD          # last row = the twist (9.5)
GOLD = (255, 200, 80)


def bg(c, t):
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, H)], [C((14, 18, 34)), C((22, 28, 52)), C((10, 12, 24))], [0, 0.55, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    for x in range(0, W + 1, 90):   # faint grid drifting slowly
        c.drawLine(x, 0, x, H, P((255, 255, 255), 0.03, stroke=2))
    off = (t * 20) % 90
    for y in range(-90, H + 90, 90):
        c.drawLine(0, y + off, W, y + off, P((255, 255, 255), 0.03, stroke=2))
    c.drawCircle(540, 1000, 700, P((255, 190, 90), 0.05 + 0.08 * seg(t, TURN + LAND, TURN + LAND + 1) + 0.05 * pulse(t, 1, 7), blur=200))


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
    dim *= 1 - 0.75 * seg(t, END_T - 0.4, END_T)              # make room for the end text
    slide = (1 - ease((t - t0) / 0.35)) * 60
    c.save(); c.translate(-slide, 0)
    # card
    card = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(70, y - 70, 940, y + 86), 22, 22)
    c.drawRRect(card, P((255, 255, 255), 0.06 * a * dim))
    c.drawRRect(card, P(GOLD if last and t > TURN else (255, 255, 255), (0.5 if last and t > TURN else 0.12) * a * dim, stroke=3))
    text(c, big, 100, y - 8, F_CAP, 50, (255, 255, 255), a * dim, align="left", stroke=8)
    text(c, small, 100, y + 30, F_SANS, 24, (170, 180, 205), a * dim, align="left")
    # counter rolls up, slows down at the end
    k = 1 - (1 - clamp((t - t0 - 0.2) / (LAND - 0.2))) ** 3
    v = yrs * k
    col = GOLD if last else (255, 120, 110)
    pz = punch(t, t0 + LAND, 0.35 if last else 0.22)
    c.save(); c.translate(915, y - 22); c.scale(pz, pz)
    text(c, years_text(v, yrs), 0, 14, F_CAP, 60 if last else 52, col, a * dim, align="right", stroke=8)
    c.restore()
    text(c, start, 915, y + 30, F_SANS, 24, (170, 180, 205), a * dim * seg(t, t0 + LAND - 0.1, t0 + LAND + 0.2), align="right")
    # log-scale bar
    frac = math.log10(max(yrs, 1.0)) / math.log10(70000)
    bw = 800 * frac * k
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(100, y + 50, 800, 14), 7, 7), P((255, 255, 255), 0.08 * a * dim))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(100, y + 50, max(14, bw), 14), 7, 7), P(col, 0.9 * a * dim))
    c.restore()


def coins(c, t):
    """coin shower after the twist"""
    if t < TURN + LAND + 0.05: return
    rng = np.random.default_rng(9)
    for j in range(26):
        x = rng.uniform(60, 920); sp = rng.uniform(380, 620); ph = rng.uniform(0, 1.2)
        yy = -60 + (t - TURN - 1.8 - ph) * sp
        if -60 < yy < 1640 and t - TURN - 1.8 > ph:
            a = 0.85 * (1 - seg(t, END_T - 0.4, END_T))
            c.save(); c.translate(x, yy); c.scale(1, abs(math.cos(t * 6 + j)) * 0.8 + 0.2)
            c.drawCircle(0, 0, 16, P(INK, a)); c.drawCircle(0, 0, 13, P(GOLD, a)); c.restore()


def frame(c, t):
    dx, dy = shake(t, TURN + LAND, 18)
    zoom = 1 + 0.03 * ((t - R0) % RD) / RD if t < TURN + LAND else 1.0   # slow push-in, snaps back on every new row
    c.save(); c.translate(540, 1000); c.scale(zoom, zoom); c.translate(-540, -1000)
    c.save(); c.translate(dx, dy)
    bg(c, t)
    hero(c, t)
    text(c, "TIME TO EARN  $1,000,000,000", 540, 600, F_SANS, 30, (170, 180, 205), seg(t, beats(6) - 0.1, beats(6) + 0.1) * (1 - seg(t, END_T - 0.4, END_T)), spacing=3)
    for i in range(len(ROWS)): row(c, t, i)
    burst(c, t, TURN + LAND, 800, Y0 + 4 * YD - 30, 28)
    coins(c, t)
    c.restore()
    c.restore()
    if TURN + LAND <= t < TURN + LAND + 0.15:
        c.drawRect(skia.Rect.MakeWH(W, H), P((255, 240, 200), 0.35 * (1 - (t - TURN - LAND) / 0.15)))
    grain(c, t, 0.025)
    end_text(c, t, END_T, "Even $1 every second", "takes 31.7 years.", "What's your number?", y=1430)


def events():
    ev = []
    for i in range(len(ROWS)):
        t0 = R0 + i * RD
        if i < len(ROWS) - 1:
            ev += [sfx(t0 + 0.12, "whoosh-fast-medium", -9), sfx(t0 + LAND - 0.62, "data-countup-short", -10), sfx(t0 + LAND, "data-number-land", -5)]
    ev += [sfx(TURN + 0.12, "whoosh-fast-medium", -9), sfx(TURN + LAND, "riser-2s-strong", -5), sfx(TURN + LAND, "cinematic-drum-big", -2),
           sfx(TURN + LAND, "data-number-land", -3), sfx(TURN + LAND + 0.1, "money-coins-pour", -7), sfx(TURN + LAND + 0.2, "shimmer-medium-bright", -9),
           music("trap", BPM, build=TURN, drop=TURN + LAND, outro=END_T, seed=7)]
    return ev


def hero(c, t):
    """giant gold $1,000,000,000 that fills the empty screen during the hook; shrinks away before row 2 arrives"""
    if t > beats(6): return
    k = ease((t - beats(5)) / beats(1))
    pz = punch(t, 0.25, 0.3) * (1 - 0.5 * k)
    c.drawCircle(540, 1150, 380, P(GOLD, (0.10 + 0.05 * pulse(t, 1, 7)) * (1 - k), blur=140))
    c.save(); c.translate(540, 1180 - 40 * k); c.scale(pz, pz)
    text(c, "$1,000,000,000", 0, 0, F_CAP, 118, GOLD, 1.0 - k, stroke=18)
    text(c, "ONE BILLION DOLLARS", 0, 70, F_SANS, 34, (220, 225, 240), (1 - k) * seg(t, 0.4, 0.7), spacing=6)
    c.restore()


def step(t): return sum(1 for i in range(len(ROWS)) if t >= R0 + i * RD)


if __name__ == "__main__":
    if sys.argv[1] == "still":
        preview(frame, 1, *HOOK, FOLLOW, [0.05, 0.5, 2.0, 3.0, 4.0, 9.0, 10.5, 11.25, 12.4, 14.0, 15.5], os.path.join(HERE, "check_bn1"),
                sticky=STICKY, hook_end=beats(8), step_fn=step, steps=len(ROWS))
    else:
        finish_data("BN1_Billion", frame, T_END, events(), TURN, 1, *HOOK, FOLLOW, sticky=STICKY, hook_end=beats(8), step_fn=step, steps=len(ROWS))
