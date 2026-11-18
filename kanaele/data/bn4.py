"""By The Numbers #4: Your heart vs. a blue whale's heart (format D · duel)
Numbers (checked 18.11.2026):
  human resting heart rate 60–100 beats per minute (American Heart Association)
  blue whale, Goldbogen et al. 2019, PNAS "Extreme bradycardia and tachycardia in the world's largest animal"
  (first ECG of a free-swimming blue whale, Stanford):
    after a dive, at the surface: 25–37 bpm · on a feeding dive: typically 4–8 bpm · lowest recorded: 2 bpm
Exact math: 2 bpm = 1 beat every 30 s; in those 30 s a resting human heart (60–100 bpm) beats 30–50 times.
The human heart pulses at 90 bpm (inside the normal range) = exactly on the 90 BPM music grid.
No heart weights (sources disagree)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "beyondexcuses"))
os.environ.setdefault("OUT_DIR", HERE)
from lib import *
sys.path.insert(0, HERE)
from dlib import sfx, finish_data, preview, punch, shake, burst, set_bpm, beats, pulse, music, end_card, rich

BPM = 90                    # cinematic; beat = 0.667 s = one human heartbeat at 90 bpm
set_bpm(BPM)
HOOK = ("Your heart: *60–100* a minute.", "How slow can a *blue whale's* go?")
STICKY = "WAIT FOR THE LOWEST"
GOLD = (255, 200, 80)
RED = (255, 92, 110)
HX, WX, HY = 260, 640, 880           # heart centres (you | whale)

# round: whale state, label, sub, (low, high) or None, colour
ROUNDS = [
    ("you",     "YOU, AT REST",        "a normal adult heart",        (60, 100), RED),
    ("surface", "AT THE SURFACE",      "catching its breath",         (25, 37),  (120, 220, 255)),
    ("dive",    "ON A DEEP DIVE",      "typical, while feeding",      (4, 8),    (150, 170, 255)),
    ("lowest",  "LOWEST EVER RECORDED", "first ECG of a wild blue whale", (2, 2), GOLD),
]
APPEAR = [beats(0), beats(5), beats(10), beats(14)]      # 0, 3.3, 6.7, 9.3 s
LANDS = [beats(2), beats(7), beats(12), beats(16)]       # 1.3, 4.7, 8.0 / 10.7 s = drop (bar start)
BUILD = APPEAR[3]
DROP = LANDS[3]
EVERY_T = beats(17)         # 11.3 s: "= 1 beat every 30 seconds"
YOURS_T = beats(18.5)       # 12.3 s: "your heart meanwhile: 30–50 beats"
END_T = beats(20)           # 13.3 s end card
FOLLOW = beats(23)          # 15.3 s
LOOP_T = beats(24)          # 16.0 s: back to the opening
T_END = beats(25.5)         # 17.0 s


def cur(t):
    i = 0
    for k, a in enumerate(APPEAR):
        if t >= a: i = k
    return i


def human_beats(t): return [k * beats(1) for k in range(int(t / beats(1)) + 1)]


def whale_beats(t):
    bs = []
    tt = LANDS[1]
    while tt < APPEAR[2] and tt <= t: bs.append(tt); tt += 2.0        # ~30 bpm at the surface
    if t >= LANDS[2]: bs.append(LANDS[2])                             # one beat on the dive, then a long silence
    if t >= DROP: bs.append(DROP)                                     # the 2 bpm beat
    return bs


def env(t, bs, k=7.0):
    past = [b for b in bs if b <= t]
    return math.exp(-(t - past[-1]) * k) if past else 0.0


# ------------------------------------------------------------------ drawing
def heart_path(cx, cy, r):
    p = skia.Path()
    p.moveTo(cx, cy + r * 0.95)
    p.cubicTo(cx - r * 1.25, cy + r * 0.15, cx - r * 1.05, cy - r * 0.95, cx, cy - r * 0.42)
    p.cubicTo(cx + r * 1.05, cy - r * 0.95, cx + r * 1.25, cy + r * 0.15, cx, cy + r * 0.95)
    p.close()
    return p


def heart(c, cx, cy, r, e, col, a=1.0):
    s = 1 + 0.16 * e
    c.drawCircle(cx, cy, r * 1.4, P(col, (0.12 + 0.35 * e) * a, blur=r * 0.6))
    p = heart_path(cx, cy, r * s)
    sh = skia.GradientShader.MakeRadial((cx - r * 0.35, cy - r * 0.3), r * 1.6 * s, [C(lerpc(col, (255, 255, 255), 0.35), a), C(col, a), C(lerpc(col, (60, 10, 30), 0.5), a)], [0, 0.5, 1])
    c.drawPath(p, skia.Paint(AntiAlias=True, Shader=sh))
    c.drawPath(p, P((20, 14, 30), a, stroke=6))
    c.drawCircle(cx - r * 0.42 * s, cy - r * 0.32 * s, r * 0.14, P((255, 255, 255), 0.35 * a))


def whale_icon(c, x, y, s, col, a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    body = skia.Path(); body.moveTo(-60, 0); body.cubicTo(-50, -26, 30, -24, 52, -6); body.lineTo(70, -18); body.lineTo(66, 0)
    body.lineTo(72, 16); body.lineTo(52, 6); body.cubicTo(30, 22, -40, 22, -60, 0); body.close()
    c.drawPath(body, P(col, a)); c.drawPath(body, P((14, 16, 30), a, stroke=4))
    c.drawCircle(-38, -4, 3.5, P((14, 16, 30), a))
    c.restore()


def bg(c, t):
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, H)], [C((40, 110, 170)), C((36, 70, 150)), C((40, 30, 96))], [0, 0.45, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    for i in range(5):                                  # light shafts from the surface
        x = 120 + i * 210 + 30 * math.sin(t * 0.5 + i)
        c.drawPath(poly([(x - 40, -50), (x + 40, -50), (x + 160, 1300), (x - 10, 1300)]), P((200, 240, 255), 0.05 + 0.02 * math.sin(t + i), blur=30))
    rng = np.random.default_rng(7)
    for _ in range(60):                                 # rising bubbles
        x, y0, r, v = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 6), rng.uniform(40, 110)
        y = (y0 - t * v) % (H + 40) - 20
        c.drawCircle(x + 8 * math.sin(t * 2 + y0), y, r, P((220, 245, 255), 0.25, stroke=2))
    # a huge whale gliding far behind (decoration)
    wx = 1300 - ((t * 38) % 1900)
    c.save(); c.translate(wx, 1560); c.scale(5.2, 5.2)
    whale_icon(c, 0, 0, 1.0, (30, 50, 110), 0.55)
    c.restore()
    c.drawCircle(WX, HY, 380, P((120, 200, 255), 0.06 + 0.06 * pulse(t, 1, 6), blur=150))


def ecg(c, t, x0, x1, y, bs, col, a, span=3.0):
    """scrolling heart trace: one spike per beat in the last `span` seconds"""
    if a <= 0: return
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0 - 14, y - 70, x1 + 14, y + 50), 18, 18), P((8, 14, 36), 0.45 * a))
    pts = []
    n = 90
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        tt = t - span * (1 - k / n)
        v = 0.0
        for b in bs:
            d = tt - b
            if -0.08 < d < 0.22:
                v += (-0.25 * math.exp(-((d + 0.04) / 0.02) ** 2) + 1.0 * math.exp(-(d / 0.018) ** 2) - 0.35 * math.exp(-((d - 0.05) / 0.025) ** 2)
                      + 0.18 * math.exp(-((d - 0.16) / 0.04) ** 2))
        pts.append((x, y - 52 * v))
    c.drawPath(poly(pts, close=False), P(col, a, stroke=5))
    c.drawCircle(pts[-1][0], pts[-1][1], 7, P((255, 255, 255), a))


def counter(c, t, i, x, y, a):
    kind, lab, sub, (lo, hi), col = ROUNDS[i]
    a0, l0 = APPEAR[i], LANDS[i]
    last = i == 3
    if t < l0:              # rolling number toward the low value
        prev = ROUNDS[i - 1][3][0] if i > 0 else 0
        k = clamp((t - a0 - 0.1) / (l0 - a0 - 0.1))
        k = 1 - (1 - k) ** 2
        s = f"{int(round(lerp(prev, lo, k)))}"
        colr = (255, 255, 255)
    else:
        s = f"{lo}–{hi}" if hi != lo else f"{lo}"
        colr = GOLD if last else col
    pz = punch(t, l0, 0.5 if last else 0.28)
    c.save(); c.translate(x, y); c.scale(pz, pz)
    text(c, s, 0, 0, F_CAP, 150 if last else 96, colr, a, stroke=18)
    c.restore()
    text(c, "beats per minute", x, y + 48, F_SANS, 30, (225, 232, 250), a, stroke=6)


def scene(c, t, loop=False):
    bg(c, t)
    i = 0 if loop else cur(t)
    endfade = 1.0 if loop else 1 - seg(t, END_T - 0.4, END_T)
    # YOU (always)
    e_h = pulse(t, 1, 7)
    heart(c, HX, HY, 88, e_h, RED)
    figure(c, HX - 64, 1066, dict(stand(), arm_f=20, elb_f=60), s=0.32, facing=1, body=(255, 214, 200), rim=(RED, 0.4))
    text(c, "YOU", HX + 6, 1060, F_CAP, 46, (255, 255, 255), 1.0, stroke=10)
    if loop or t < APPEAR[1]:
        counter(c, t if not loop else LANDS[0] + 1, 0, HX, 1180, 1.0 if loop else seg(t, 0.05, 0.25))
    else:
        text(c, "60–100", HX, 1180, F_CAP, 74, RED, endfade, stroke=14)
        text(c, "beats per minute", HX, 1222, F_SANS, 28, (225, 232, 250), endfade, stroke=6)
    ecg(c, t, 70, 440, 1365, human_beats(t), RED, 0.95 * (1.0 if loop else seg(t, 0.4, 0.8)) * (endfade if not loop else 1))
    # BLUE WHALE
    wa = 1.0 if loop else 1.0
    bs = whale_beats(t) if not loop else []
    e_w = env(t, bs, 3.5 if t >= DROP else 5.0) * (1.6 if t >= DROP else 1.0)
    heart(c, WX, HY, 140, e_w, (90, 150, 255) if i < 3 else (120, 170, 255), 0.55 if i == 0 else 1.0)
    whale_icon(c, WX - 120, 1046, 0.72, (120, 180, 255))
    rich(c, "BLUE *WHALE*", WX + 34, 1062, 46, 1.0, stroke=10, maxw=300)
    if i == 0:
        text(c, "?", WX, 1200, F_CAP, 110, (255, 255, 255), 0.7 + 0.3 * pulse(t, 1, 5), stroke=16)
    else:
        a0 = APPEAR[i]
        sl = (1 - ease((t - a0) / 0.3)) * 40
        c.save(); c.translate(sl, 0)
        counter(c, t, i, WX, 1180 if i < 3 else 1200, seg(t, a0, a0 + 0.2) * endfade)
        c.restore()
        lab, sub, col = ROUNDS[i][1], ROUNDS[i][2], ROUNDS[i][4]
        la = seg(t, a0, a0 + 0.25) * endfade
        rich(c, f"*{lab}*" if i == 3 else lab, 470, 610, 50, la, base=(255, 255, 255), hi=GOLD, stroke=12, maxw=800)
        text(c, sub, 470, 656, F_SANS, 32, (215, 225, 250), la * (1 - seg(t, EVERY_T - 0.2, EVERY_T)), stroke=6)
    ecg(c, t, 500, 870, 1365, bs, (150, 200, 255) if t < DROP else GOLD, 0.95 * seg(t, APPEAR[1], APPEAR[1] + 0.4) * endfade)
    if not loop and i == 0 and t > 0.6:   # main search phrase, big, once
        rich(c, "BLUE WHALE *HEART RATE*", 470, 630, 54, seg(t, 0.6, 0.9) * (1 - seg(t, APPEAR[1] - 0.3, APPEAR[1])), stroke=12)
    if loop: return
    # after the drop: the math
    if t >= EVERY_T:
        b = seg(t, EVERY_T, EVERY_T + 0.15) * endfade
        pz = punch(t, EVERY_T, 0.3)
        c.save(); c.translate(470, 666); c.scale(pz, pz)
        rich(c, "= 1 beat every *30 seconds*", 0, 0, 46, b, stroke=12, maxw=800)
        c.restore()


def frame(c, t):
    dx, dy = shake(t, DROP, 24, 0.5)
    zoom = 1 + 0.02 * pulse(t, 4, 3) + 0.04 * seg(t, BUILD, DROP) * (1 - seg(t, DROP, DROP + 0.6)) + 0.08 * seg(t, END_T, LOOP_T) * (1 - seg(t, LOOP_T, LOOP_T + 0.5))
    c.save(); c.translate(470, 960); c.scale(zoom, zoom); c.translate(-470, -960)
    c.save(); c.translate(dx, dy)
    scene(c, t)
    burst(c, t, DROP, WX, HY, 36)
    burst(c, t, DROP + 0.05, WX, 1180, 22, col=(150, 200, 255), seed=8)
    c.restore(); c.restore()
    if BUILD <= t < DROP:       # the whale's heart is silent: dim everything else
        c.drawRect(skia.Rect.MakeWH(W, H), P((6, 10, 30), 0.25 * seg(t, BUILD, BUILD + 0.8)))
    if t >= YOURS_T and t < END_T:
        b = seg(t, YOURS_T, YOURS_T + 0.15) * (1 - seg(t, END_T - 0.4, END_T))
        pz = punch(t, YOURS_T, 0.3)
        c.save(); c.translate(470, 724); c.scale(pz, pz)
        rich(c, "Yours meanwhile: *30–50 beats*", 0, 0, 44, b, stroke=12, maxw=800)
        c.restore()
    if DROP <= t < DROP + 0.16:
        c.drawRect(skia.Rect.MakeWH(W, H), P((255, 240, 210), 0.45 * (1 - (t - DROP) / 0.16)))
    if t >= LOOP_T:     # crossfade back into the opening frame
        k = seg(t, LOOP_T, LOOP_T + 0.5)
        c.saveLayerAlpha(skia.Rect.MakeWH(W, H), int(255 * k))
        scene(c, t, loop=True)
        c.restore()
    grain(c, t, 0.02)
    if t < LOOP_T + 0.3:
        end_card(c, t, END_T, "Blue whale on a deep dive:", "as low as *2 beats* a minute.", "What's your resting heart rate?", y=1110,
                 alpha=1 - seg(t, LOOP_T - 0.2, LOOP_T + 0.2))


def events():
    ev = []
    for i in range(3):
        a, l = APPEAR[i], LANDS[i]
        ev += [sfx(a + 0.1, "whoosh-fast-medium", -9), sfx(l - 0.6, "data-countup-short", -11), sfx(l, "data-number-land", -5),
               sfx(l, f"tone-step-{i + 1}", -12)]
    ev += [sfx(BUILD + 0.1, "whoosh-slow-medium", -6), sfx(DROP - 2.0, "riser-2s-strong", -4),
           sfx(DROP, "cinematic-drum-big", -1), sfx(DROP, "data-number-land", -2), sfx(DROP + 0.15, "shimmer-medium-bright", -8),
           sfx(EVERY_T, "pop-large-in", -6), sfx(YOURS_T, "pop-medium-in", -6), sfx(END_T, "whoosh-medium-soft", -8),
           sfx(LOOP_T, "whoosh-fast-medium", -6),
           music("cinematic", BPM, build=BUILD, drop=DROP, outro=END_T, seed=4)]
    return ev


def step(t): return sum(1 for a in APPEAR if t >= a)


if __name__ == "__main__":
    if sys.argv[1] == "still":
        preview(frame, 4, *HOOK, FOLLOW, [0.05, 0.5, 1.4, 2.0, 3.5, 4.8, 6.0, 7.0, 8.1, 9.6, 10.75, 11.5, 12.5, 13.8, 15.5, 16.8],
                os.path.join(HERE, "check_bn4"), sticky=STICKY, hook_end=beats(5), step_fn=step, steps=len(ROUNDS))
    elif sys.argv[1] == "cover":
        import dlib
        lines = [(ln, 200) for ln in " ".join(sys.argv[2:]).split("|")]
        def cover_frame(c, t):   # clean scene for the grid: the two hearts and their traces under the words
            bg(c, t)
            heart(c, 290, 1250, 105, 0.6, RED)
            heart(c, 700, 1230, 175, 1.0, (120, 170, 255))
            text(c, "YOU", 290, 1440, F_CAP, 56, (255, 255, 255), 1.0, stroke=12)
            rich(c, "BLUE *WHALE*", 700, 1468, 56, 1.0, stroke=12, maxw=420)
            ecg(c, DROP + 0.9, 90, 470, 1600, human_beats(DROP + 0.9), RED, 1.0)
            ecg(c, DROP + 0.9, 530, 960, 1600, [DROP], GOLD, 1.0)
        dlib.cover(cover_frame, DROP + 0.3, lines, os.path.join(HERE, "Cover_BN4.jpg"), 4)
    else:
        finish_data("BN4_WhaleHeart", frame, T_END, events(), BUILD, 4, *HOOK, FOLLOW, sticky=STICKY, hook_end=beats(5),
                    step_fn=step, steps=len(ROUNDS))
