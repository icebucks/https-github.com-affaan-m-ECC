"""Profilbilder für die neuen Kanäle (1080x1080, Motiv im inneren Kreis, damit der runde Zuschnitt passt)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "beyondexcuses"))
from lib import *
from PIL import Image

S = 1080
GOLD = (255, 200, 80)


def save(surf, name):
    Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]).save(os.path.join(HERE, name), quality=94)


def coin(c, x, y, r):
    c.drawCircle(x, y, r + 5, P(INK)); c.drawCircle(x, y, r, P(GOLD)); c.drawCircle(x, y, r * 0.62, P((255, 230, 140), 0.9, stroke=r * 0.08))
    text(c, "$", x, y + r * 0.36, F_CAP, r * 1.0, (190, 130, 30), 1.0)


def money_pfp():
    surf = skia.Surface(S, S); c = surf.getCanvas()
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, S)], [C((30, 20, 50)), C((150, 70, 80)), C((255, 170, 100))], [0, 0.55, 1])
    c.drawRect(skia.Rect.MakeWH(S, S), skia.Paint(Shader=sh))
    c.drawCircle(540, 560, 300, P((255, 210, 140), 0.35, blur=80))
    c.drawRect(skia.Rect.MakeLTRB(0, 860, S, S), P((40, 26, 40)))
    c.drawLine(0, 860, S, 860, P(INK, stroke=8))
    # money tree
    c.drawLine(640, 860, 640, 520, P(INK, stroke=30)); c.drawLine(640, 860, 640, 520, P((120, 85, 55), stroke=18))
    for dx, dy, r in ((-90, 40, 95), (85, 30, 100), (0, -40, 115), (-50, -110, 80), (60, -105, 78)):
        c.drawCircle(640 + dx, 470 + dy, r + 7, P(INK)); c.drawCircle(640 + dx, 470 + dy, r, P((90, 170, 90)))
    for i in range(9):
        a = i * 2.3; rr = 60 + (i % 3) * 45
        coin(c, 640 + math.cos(a) * rr, 450 + math.sin(a) * rr * 0.8, 24)
    figure(c, 400, 860, cheer(0.4), s=2.0, facing=1, body=(255, 242, 228), rim=((255, 200, 120), 0.6))
    save(surf, "profil_broke_vs_rich.jpg")


def data_pfp():
    surf = skia.Surface(S, S); c = surf.getCanvas()
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, S)], [C((14, 18, 34)), C((26, 34, 64))])
    c.drawRect(skia.Rect.MakeWH(S, S), skia.Paint(Shader=sh))
    for x in range(0, S + 1, 90): c.drawLine(x, 0, x, S, P((255, 255, 255), 0.05, stroke=2))
    for y in range(0, S + 1, 90): c.drawLine(0, y, S, y, P((255, 255, 255), 0.05, stroke=2))
    c.drawCircle(540, 600, 360, P(GOLD, 0.12, blur=120))
    hs = [180, 290, 400, 560]
    for i, h in enumerate(hs):
        x = 250 + i * 160
        r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x, 800 - h, x + 110, 800), 14, 14)
        col = GOLD if i == 3 else (120, 140, 190)
        c.drawRRect(r, P(col)); c.drawRRect(r, P(INK, stroke=8))
    c.drawLine(200, 800, 880, 800, P((230, 235, 245), stroke=8))
    pts = [(305, 560), (465, 450), (625, 340), (785, 190)]
    c.drawPath(poly(pts, close=False), P((255, 255, 255), stroke=12))
    for p in pts: c.drawCircle(p[0], p[1], 16, P((255, 255, 255))); c.drawCircle(p[0], p[1], 16, P(INK, stroke=5))
    text(c, "#", 300, 330, F_CAP, 170, GOLD, 1.0, stroke=16)
    save(surf, "profil_by_the_numbers.jpg")


money_pfp(); data_pfp()
