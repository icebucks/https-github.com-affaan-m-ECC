"""By The Numbers #6: How long to count to 1 billion? (format A · counter cards)
Exact arithmetic, no estimates – 1 number per second, 8 hours a day (28,800 numbers a day):
  1,000 -> 1,000 s = 16 min 40 s · 100,000 -> 3.47 days · 1,000,000 -> 34.7 days (about 5 weeks)
  1,000,000,000 -> 34,722 days = 95.1 years (365.25-day years) -> start at 5, finish at 100.
(No nonstop figure: "$1 a second = 31.7 years" was already in BN1.)"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "beyondexcuses"))
os.environ.setdefault("OUT_DIR", HERE)
from lib import *
sys.path.insert(0, HERE)
from dlib import sfx, finish_data, preview, punch, shake, burst, set_bpm, beats, pulse, music, end_card

BPM = 128                   # synthwave; every event sits on the beat grid
set_bpm(BPM)
T_END = beats(36)           # 16.9 s
HOOK = ("Count to 1,000: *16 minutes*.", "How long to *1 BILLION*?")
STICKY = "WAIT FOR THE BILLION"
END_T = beats(30)           # end card 14.1 s
FOLLOW = beats(33)          # 15.5 s
ROWS = [  # big label, small label, seconds (8 h days), result text, note
    ("TO 1,000", "1 number per second", 1000, "16 MIN 40 S", "a coffee break"),
    ("TO 100,000", "8 hours a day", 100000, "3.5 DAYS", "half a week"),
    ("TO 1 MILLION", "8 hours a day", 1000000, "34.7 DAYS", "about 5 weeks"),
    ("TO 1 BILLION", "8 hours a day, every day", 1000000000, "95 YEARS", "start at 5 -> finish at 100"),
]
R0, RD = beats(2), beats(6)  # first row, gap between rows (2.8 s)
LAND = beats(4)             # counter lands 4 beats after a row appears
Y0, YD = 720, 200           # last card ends at y ~1350, above the TikTok caption area
LOOP_T = beats(34)          # end card fades, the giant counter returns -> loops into frame 0
TURN = R0 + 3 * RD          # last row = the twist
GOLD = (255, 200, 80)


def bg(c, t):
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, H)], [C((26, 36, 92)), C((46, 34, 104)), C((18, 16, 48))], [0, 0.55, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    for x in range(0, W + 1, 90):   # faint grid drifting slowly
        c.drawLine(x, 0, x, H, P((255, 255, 255), 0.045, stroke=2))
    off = (t * 20) % 90
    for y in range(-90, H + 90, 90):
        c.drawLine(0, y + off, W, y + off, P((255, 255, 255), 0.045, stroke=2))
    c.drawCircle(540, 1000, 700, P((255, 190, 90), 0.05 + 0.08 * seg(t, TURN + LAND, TURN + LAND + 1) + 0.05 * pulse(t, 1, 7), blur=200))


def years_text(v, final):
    if final < 100: return f"{v:.1f} YEARS"
    return f"{int(round(v)):,} YEARS"


def row(c, t, i):
    big, small, yrs, start, note = ROWS[i]
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
    card = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(70, y - 72, 880, y + 80), 22, 22)
    c.drawRRect(card, P((255, 255, 255), 0.06 * a * dim))
    c.drawRRect(card, P(GOLD if last and t > TURN else (255, 255, 255), (0.5 if last and t > TURN else 0.12) * a * dim, stroke=3))
    text(c, big, 96, y - 8, F_CAP, 50, (255, 255, 255), a * dim, align="left", stroke=8)
    text(c, small, 96, y + 28, F_SANS, 28, (185, 195, 220), a * dim, align="left")
    # counter rolls up, slows down at the end
    k = 1 - (1 - clamp((t - t0 - 0.2) / (LAND - 0.2))) ** 3
    col = GOLD if last else (120, 220, 255)
    pz = punch(t, t0 + LAND, 0.35 if last else 0.22)
    c.save(); c.translate(856, y - 24); c.scale(pz, pz)
    shown = start if t >= t0 + LAND else f"{int(yrs * k):,}"           # the number ticks up, then the time lands
    text(c, shown, 0, 14, F_CAP, 64 if last else 52, col, a * dim, align="right", stroke=8)
    c.restore()
    text(c, note, 856, y + 28, F_SANS, 28, (185, 195, 220), a * dim * seg(t, t0 + LAND - 0.1, t0 + LAND + 0.2), align="right")
    # log-scale bar (seconds of counting)
    frac = math.log10(max(yrs, 1.0)) / math.log10(1e9)
    bw = 756 * frac * k
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(96, y + 46, 756, 14), 7, 7), P((255, 255, 255), 0.08 * a * dim))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(96, y + 46, max(14, bw), 14), 7, 7), P(col, 0.9 * a * dim))
    c.restore()


def coins(c, t):
    """coin shower after the twist"""
    if t < TURN + LAND + 0.05: return
    rng = np.random.default_rng(9)
    for j in range(26):
        x = rng.uniform(60, 860); sp = rng.uniform(380, 620); ph = rng.uniform(0, 1.2)
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
    text(c, "1 NUMBER PER SECOND · 8 HOURS A DAY", 470, 610, F_SANS, 30, (170, 180, 205), seg(t, R0 - 0.1, R0 + 0.2) * (1 - seg(t, END_T - 0.4, END_T)), spacing=2)
    for i in range(len(ROWS)): row(c, t, i)
    burst(c, t, TURN + LAND, 740, Y0 + 3 * YD - 30, 28)
    hero_loop(c, t)
    c.restore()
    c.restore()
    if TURN + LAND <= t < TURN + LAND + 0.15:
        c.drawRect(skia.Rect.MakeWH(W, H), P((255, 240, 200), 0.35 * (1 - (t - TURN - LAND) / 0.15)))
    grain(c, t, 0.025)
    end_card(c, t, END_T, "Counting to *1 billion*", "takes *95 years*.", "How far would you get?", y=1110, alpha=1 - seg(t, LOOP_T, LOOP_T + 0.3))


def events():
    ev = []
    for i in range(len(ROWS)):
        t0 = R0 + i * RD
        if i < len(ROWS) - 1:
            ev += [sfx(t0 + 0.12, "whoosh-fast-medium", -9), sfx(t0 + LAND - 0.62, "data-countup-short", -10), sfx(t0 + LAND, "data-number-land", -5),
                   sfx(t0 + LAND, f"tone-step-{i + 1}", -12)]
    ev += [sfx(0.0, "time-clock-fast", -10), sfx(TURN + 0.12, "whoosh-fast-medium", -9), sfx(TURN + LAND - 2.0, "riser-2s-strong", -5),
           sfx(TURN + LAND - 1.2, "data-countup-medium", -9), sfx(TURN + LAND, "cinematic-drum-big", -2), sfx(TURN + LAND, "data-number-land", -3),
           sfx(TURN + LAND + 0.2, "shimmer-medium-bright", -9), sfx(LOOP_T + 0.1, "whoosh-fast-medium", -7),
           music("synthwave", BPM, build=TURN, drop=TURN + LAND, outro=END_T, seed=6)]
    return ev


def hero(c, t):
    """giant counter ticking 1, 2, 3 … (one per second) during the hook; shrinks away before the first card lands"""
    if t > R0 + 0.6: return
    k = ease((t - R0 + 0.2) / 0.8)
    n = 1 + int(t)
    pz = punch(t, float(int(t)), 0.25) * (1 - 0.5 * k)
    c.drawCircle(540, 1150, 420, P((120, 220, 255), (0.16 + 0.06 * pulse(t, 1, 7)) * (1 - k), blur=140))
    c.save(); c.translate(520, 1200 - 40 * k); c.scale(pz, pz)
    text(c, f"{n:,}", 0, 0, F_CAP, 230, (255, 255, 255), 1.0 - k, stroke=20)
    text(c, "... 1,000,000,000 ?", 0, 90, F_SANS, 44, GOLD, (1 - k) * seg(t, 0.3, 0.6), spacing=3)
    c.restore()


def hero_loop(c, t):
    """the giant counter returns at the end so the last frame matches the first (seamless loop)"""
    if t < LOOP_T: return
    k = ease((t - LOOP_T) / 0.45)
    c.drawRect(skia.Rect.MakeWH(W, H), P((26, 36, 92), 0.85 * k))
    c.drawCircle(540, 1150, 420, P((120, 220, 255), 0.16 * k, blur=140))
    c.save(); c.translate(520, 1200); s = 0.7 + 0.3 * k; c.scale(s, s)
    text(c, "1", 0, 0, F_CAP, 230, (255, 255, 255), k, stroke=20)
    text(c, "... 1,000,000,000 ?", 0, 90, F_SANS, 44, GOLD, k, spacing=3)
    c.restore()


def step(t): return sum(1 for i in range(len(ROWS)) if t >= R0 + i * RD)


if __name__ == "__main__":
    if sys.argv[1] == "still":
        preview(frame, 6, *HOOK, FOLLOW, [float(a) for a in sys.argv[2:]] or [0.05, 0.5, 2.0, 3.0, 4.5, 6.5, 8.6, 10.0, 11.3, 12.4, 14.5, 16.0, 16.8],
                os.path.join(HERE, "check_bn6"), sticky=STICKY, hook_end=beats(8), step_fn=step, steps=len(ROWS))
    elif sys.argv[1] == "cover":
        import dlib
        lines = [(ln, 190) for ln in " ".join(sys.argv[2:]).split("|")]
        dlib.cover(frame, TURN + LAND + 0.8, lines, os.path.join(HERE, "Cover_BN6.jpg"), 6)
    else:
        finish_data("BN6_CountBillion", frame, T_END, events(), TURN, 6, *HOOK, FOLLOW, sticky=STICKY, hook_end=beats(8), step_fn=step, steps=len(ROWS))
