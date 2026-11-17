"""Prototype: 'clean' figure look on a dark glossy stage (own style test, not a copy of any channel).
python3 proto/proto_clean.py  -> proto/proto_clean.mp4 (4 s, silent) + proto/proto_clean.jpg"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
os.environ["FIG_STYLE"] = "clean"
os.environ["VID_LANG"] = "en"
import lib
from lib import *

FLOOR = 1240
MONO = skia.Typeface.MakeFromFile("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf") if os.path.exists(
    "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf") else F_SANS
WHITE_FIG = (244, 244, 246)
GREY_FIG = (150, 156, 170)


def stage(c, t):
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, FLOOR)], [C((10, 11, 16)), C((22, 24, 32))])
    c.drawRect(skia.Rect.MakeWH(W, FLOOR), skia.Paint(Shader=sh))
    c.drawRect(skia.Rect.MakeLTRB(0, FLOOR, W, H), P((8, 9, 13)))
    sp = skia.GradientShader.MakeRadial((540, FLOOR - 300), 700, [C((255, 255, 255), 0.07), C((255, 255, 255), 0.0)], [0, 1])
    c.drawRect(skia.Rect.MakeWH(W, FLOOR), skia.Paint(Shader=sp))           # soft spotlight
    c.drawLine(0, FLOOR, W, FLOOR, P((230, 232, 240), 0.9, stroke=3))
    rng = np.random.default_rng(3)                                          # light rain
    for i in range(70):
        x = rng.uniform(0, W); sp_ = rng.uniform(1100, 1500); off = rng.uniform(0, 3000)
        y = (off + t * sp_) % (FLOOR + 200) - 100
        c.drawLine(x, y, x - 4, y + 34, P((200, 205, 220), 0.25, stroke=2))


def caption(c, t, s1, s2):
    a = seg(t, 0.0, 0.3)
    n1 = int(len(s1) * clamp(t / 0.6)); n2 = int(len(s2) * clamp((t - 0.6) / 0.6))   # typewriter
    text(c, s1[:n1], 540, 420, MONO, 44, (240, 240, 245), a, spacing=10)
    text(c, s2[:n2], 540, 486, MONO, 44, (255, 120, 120), a, spacing=10)


def runner(t):
    x = -80 + 360 * t
    return dict(x=x, y=FLOOR, p=run(t * 11), f=1)


def stander(t):
    p = arms_crossed(head=-6)
    p["lean"] = -4 + 2 * math.sin(t * 2)
    return dict(x=760, y=FLOOR, p=p, f=-1)


def draw_figs(c, t, refl=False):
    r = smooth(runner, t); st = smooth(stander, t)
    for o, col in ((st, GREY_FIG), (r, WHITE_FIG)):
        figure(c, o["x"], o["y"], o["p"], s=1.35, facing=o["f"], body=col, style="clean")


def frame(c, t):
    stage(c, t)
    # glossy floor reflection: mirrored figures, faded with depth
    c.save(); c.clipRect(skia.Rect.MakeLTRB(0, FLOOR + 2, W, H))
    c.saveLayerAlpha(skia.Rect.MakeWH(W, H), 70)
    c.translate(0, 2 * FLOOR); c.scale(1, -1); draw_figs(c, t, True)
    c.restore()
    fade = skia.GradientShader.MakeLinear([(0, FLOOR), (0, FLOOR + 320)], [C((8, 9, 13), 0.0), C((8, 9, 13), 1.0)])
    c.drawRect(skia.Rect.MakeLTRB(0, FLOOR, W, FLOOR + 320), skia.Paint(Shader=fade))
    c.restore()
    draw_figs(c, t)
    caption(c, t, "WHO GETS THERE", "FIRST?")


if __name__ == "__main__":
    lib.render(frame, 4.0, os.path.join(HERE, "proto_clean.mp4"))
    stills(frame, [0.6, 1.4, 2.2, 3.0], os.path.join(HERE, "proto_clean"))
