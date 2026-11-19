"""YouTube channel banner for Virlix (2560x1440, safe area 1546x423 in the centre = visible on every device).
Style taken from the logo: deep navy, neon red + cyan lines, glow. No game art (rights), no Rockstar marks.
  python3 clips/banner.py <logo.png|jpg> <out.jpg>"""
import math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "beyondexcuses"))
import skia
import lib
from lib import P, C, F_CAP, F_SANS
from PIL import Image

W, H = 2560, 1440
SAFE = (W - 1546) / 2, (H - 423) / 2, 1546, 423          # x, y, w, h
RED, CYAN, NAVY, WHITE = (255, 60, 80), (70, 210, 230), (10, 14, 26), (244, 246, 250)


def glow_line(c, x0, y0, x1, y1, col, w, a=1.0):
    c.drawLine(x0, y0, x1, y1, P(col, 0.35 * a, stroke=w * 4, blur=w * 3))
    c.drawLine(x0, y0, x1, y1, P(col, a, stroke=w))


def main(logo_path, out):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    g = skia.GradientShader.MakeRadial((W / 2, H / 2), W * 0.7, [C((22, 26, 46)), C(NAVY), C((4, 6, 12))], [0.0, 0.55, 1.0])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=g))
    rng = np.random.default_rng(11)
    sx, sy, sw, sh = SAFE
    # vertical neon "rain" (like the logo's lines), denser outside the text
    for _ in range(170):
        x = rng.uniform(0, W); top = rng.uniform(-200, H * 0.7); ln = rng.uniform(120, 520)
        col = RED if rng.random() < 0.55 else CYAN
        a = rng.uniform(0.15, 0.6) * (0.45 if sx + 120 < x < sx + sw - 60 and top + ln > sy and top < sy + sh else 1.0)
        glow_line(c, x, top, x, top + ln, col, rng.uniform(1.5, 4), a)
        if rng.random() < 0.3: c.drawCircle(x, top, rng.uniform(4, 8), P((255, 200, 170), a))
    # horizontal speed lines left and right of the safe area
    for k in range(26):
        y = sy + rng.uniform(-60, sh + 60); col = CYAN if k % 3 else RED
        glow_line(c, rng.uniform(0, 300), y, sx - rng.uniform(20, 160), y, col, 2.5, rng.uniform(0.3, 0.8))
        y = sy + rng.uniform(-60, sh + 60)
        glow_line(c, sx + sw + rng.uniform(20, 160), y, W - rng.uniform(0, 300), y, col, 2.5, rng.uniform(0.3, 0.8))
    # logo, left inside the safe area
    im = Image.open(logo_path).convert("RGBA")
    arr = np.asarray(im)
    logo = skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType)
    L = 400; lx, ly = sx + 10, sy + (sh - L) / 2
    c.drawCircle(lx + L / 2, ly + L / 2, L * 0.55, P(RED, 0.25, blur=60))
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(lx, ly, L, L), 60, 60)
    c.save(); c.clipRRect(rr, doAntiAlias=True)
    c.drawImageRect(logo, skia.Rect.MakeXYWH(lx, ly, L, L), skia.SamplingOptions(skia.FilterMode.kLinear))
    c.restore()
    c.drawRRect(rr, P(CYAN, 0.8, stroke=4))
    # name + tagline
    tx = lx + L + 70
    f = skia.Font(F_CAP, 210); f.setEmbolden(False)
    name = "VIRLIX"
    for dx, col, a in ((6, CYAN, 0.9), (-6, RED, 0.9)):        # chromatic split like the logo's red/cyan
        c.drawString(name, tx + dx, sy + 215, f, P(col, a))
    c.drawString(name, tx, sy + 215, f, P(WHITE))
    nw = f.measureText(name)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(tx, sy + 248, nw, 10), 5, 5), P(RED))
    room = sx + sw - 20 - tx                                    # keep every word inside the safe area
    t1 = "GTA 6 GAMEPLAY · NO COMMENTARY"; s1 = 58 * min(1.0, room / (skia.Font(F_SANS, 58).measureText(t1) + 2 * len(t1)))
    lib.text(c, t1, tx, sy + 330, F_SANS, s1, WHITE, 1.0, align="left", spacing=2)
    lib.text(c, "2 NEW VIDEOS EVERY DAY", tx, sy + 400, F_SANS, 46, CYAN, 1.0, align="left", spacing=6)
    arr = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]
    Image.fromarray(arr).save(out, quality=92, optimize=True)
    # preview with the safe area marked
    pv = Image.fromarray(arr).resize((1280, 720))
    from PIL import ImageDraw
    d = ImageDraw.Draw(pv); d.rectangle([sx / 2, sy / 2, (sx + sw) / 2, (sy + sh) / 2], outline=(255, 255, 0), width=2)
    pv.save(out.replace(".jpg", "_preview.jpg"), quality=85)
    print(out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
