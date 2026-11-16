"""Profilbild-Varianten im Stil der Videos (1080x1080, kreisrund-sicher)."""
import math
import skia
from lib import *

S = 1080


def base(c, top, mid, hor, horizon):
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, horizon)], [C(top), C(mid), C(hor)], [0, 0.55, 1])
    c.drawRect(skia.Rect.MakeWH(S, S), skia.Paint(Shader=sh))


def peak_variant(c):
    base(c, (40, 26, 60), (190, 90, 90), (255, 180, 110), 760)
    sun(c, 560, 600, 1.0, r=120)
    hills(c, 900, (120, 60, 80), amp=40, off=1.0, height=160)
    mt = poly([(120, 1100), (540, 600), (960, 1100)])
    c.drawPath(mt, P((90, 54, 70))); c.drawPath(mt, P(INK, stroke=9))
    c.drawPath(poly([(540, 600), (960, 1100), (720, 1100), (600, 800)]), P((70, 40, 58), 0.9))
    c.drawPath(poly([(420, 743), (540, 600), (660, 743)], close=False), P((255, 190, 120), 0.9, stroke=8))
    c.drawLine(600, 604, 600, 470, P(INK, stroke=8))
    c.drawPath(poly([(600, 470), (690, 495), (600, 525)]), P((255, 200, 70))); c.drawPath(poly([(600, 470), (690, 495), (600, 525)]), P(INK, stroke=5))
    figure(c, 525, 606, cheer(0.3), s=1.25, facing=1, body=(255, 240, 226))


def walk_variant(c):
    base(c, (10, 14, 34), (30, 44, 86), (230, 140, 90), 700)
    sun(c, 540, 700, 1.0, r=150)
    hills(c, 700, (24, 30, 56), amp=30, off=2.0, height=60)
    c.drawRect(skia.Rect.MakeLTRB(0, 700, S, S), P((14, 18, 32)))
    # path towards the sun
    c.drawPath(poly([(380, S), (700, S), (560, 700), (520, 700)]), P((230, 150, 100), 0.35))
    figure(c, 470, 930, walk(1.2, lean=8, stride=26), s=2.3, facing=1, body=(244, 244, 240))


def rope_variant(c):
    base(c, (16, 22, 44), (34, 52, 96), (70, 100, 150), 1080)
    moon(c, 800, 260, 1.0)
    sky(c, 0, (16, 22, 44), (34, 52, 96), (70, 100, 150), 1080, stars=0.9)
    moon(c, 790, 250, 1.0)
    # cliff edge, figure stepping off into the unknown -> stepping stones
    for i, (x, y) in enumerate([(300, 820), (480, 760), (660, 700), (840, 640)]):
        st = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 70, y, 140, 40), 18, 18)
        c.drawRRect(st, P((110, 120, 150))); c.drawRRect(st, P(INK, stroke=7))
    figure(c, 480, 690, airborne(), s=1.7, facing=1, body=(244, 244, 240), mode="hip")


for name, fn in (("pfp_gipfel", peak_variant), ("pfp_weg", walk_variant), ("pfp_sprung", rope_variant)):
    surf = skia.Surface(S, S); c = surf.getCanvas(); c.clear(skia.ColorBLACK)
    fn(c)
    surf.makeImageSnapshot().save(f"/home/claude/mind/{name}.png", skia.kPNG)

# preview sheet with circular crop like on TikTok
from PIL import Image, ImageDraw
ims = []
for name in ("pfp_gipfel", "pfp_weg", "pfp_sprung"):
    im = Image.open(f"/home/claude/mind/{name}.png").convert("RGB").resize((360, 360))
    mask = Image.new("L", (360, 360), 0); ImageDraw.Draw(mask).ellipse((0, 0, 359, 359), fill=255)
    bg = Image.new("RGB", (360, 360), (245, 245, 245)); bg.paste(im, (0, 0), mask); ims.append(bg)
sheet = Image.new("RGB", (1140, 380), (245, 245, 245))
for i, im in enumerate(ims): sheet.paste(im, (10 + i * 380, 10))
sheet.save("/home/claude/mind/pfp_vorschau.png")
