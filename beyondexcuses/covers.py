"""Titelbilder (TikTok-Cover) für alle Folgen: Szene + große Schrift im 3:4-Rasterbereich.
python3 covers.py            -> covers/Cover_<N>.jpg + covers/sheet.jpg"""
import os, sys, importlib
os.environ.setdefault("VID_LANG", "en")
import lib
from lib import *
from PIL import Image

EPS = {  # num: (module, scene time, negative, positive)
    1: ("ep1", 8.0, "PLANNER", "DOER"),
    2: ("ep2", 12.5, "OVERTHINKER", "DOER"),
    3: ("ep3", 10.0, "EGO", "HUMILITY"),
    4: ("ep4", 13.6, "EXCUSES", "DISCIPLINE"),
    5: ("ep5", 14.5, "ENVY", "CONTENTMENT"),
    6: ("ep6", 12.4, "COMFORT ZONE", "GROWTH"),
    7: ("ep7", 13.0, "PEOPLE PLEASER", "BOUNDARIES"),
    8: ("ep8", 14.2, "IMPATIENCE", "PATIENCE"),
    9: ("ep9", 13.2, "SCROLLER", "LEARNER"),
    10: ("ep10", 13.2, "GRUDGE", "LETTING GO"),
    11: ("ep11", 12.4, "VICTIM", "OWNER", "ONLY 1|FIXES", 8),   # optional 5th: thumbnail words (≤ 3, "|" = line break)
    12: ("ep12", 8.4, "VICTIM", "OWNER", "HE TURNED|AROUND", 9),   # optional 6th: part number shown on TikTok
    13: ("ep13", 12.2, "PERFECTIONIST", "FINISHER", "3 WEEKS|0 SOLD", 10),
    14: ("ep14", 7.2, "PEOPLE PLEASER", "BOUNDARIES", "NONE|WERE HIS", 11),
}


def fit(s, maxw, size):
    while size > 40 and skia.Font(F_CAP, size).measureText(s) > maxw: size -= 4
    return size


def cover(num, out):
    mod, t, neg, pos = EPS[num][:4]
    thumb = EPS[num][4] if len(EPS[num]) > 4 else None
    shown = EPS[num][5] if len(EPS[num]) > 5 else num        # TikTok numbering can differ from the file number
    m = importlib.import_module(mod)
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.ColorBLACK)
    lib.NOW = t
    c.save(); c.translate(0, 190); m.frame(c, t); c.restore()
    # calm dark band for the title; fades into the scene below
    c.drawRect(skia.Rect.MakeWH(W, 860), P((14, 16, 26), 0.93))
    sh = skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, 860), (0, 1120)], [C((14, 16, 26), 0.93), C((14, 16, 26), 0.0)]))
    c.drawRect(skia.Rect.MakeXYWH(0, 860, W, 260), sh)
    # episode badge
    text(c, "MINDSET SERIES", 540, 330, F_SANS, 34, AMBER, 1.0, spacing=6, stroke=6)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(440, 370, 200, 110), 26, 26), P(AMBER))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(440, 370, 200, 110), 26, 26), P(INK, stroke=6))
    text(c, f"#{shown}", 540, 452, F_CAP, 80, INK, 1.0)
    if thumb:   # thumbnail words (different from the title, same promise): white line + amber line
        l1, l2 = thumb.split("|")
        text(c, l1, 540, 660, F_CAP, fit(l1, 940, 150), (245, 246, 250), 1.0, stroke=20)
        text(c, l2, 540, 830, F_CAP, fit(l2, 940, 150), AMBER, 1.0, stroke=20)
    else:       # matchup
        s1 = fit(neg, 940, 118); s2 = fit(pos, 940, 118)
        text(c, neg, 540, 640, F_CAP, s1, (235, 236, 242), 1.0, stroke=18)
        text(c, "vs", 540, 735, F_CAP, 64, (255, 255, 255), 0.9, stroke=12)
        text(c, pos, 540, 850, F_CAP, s2, AMBER, 1.0, stroke=18)
    arr = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]
    Image.fromarray(arr).save(out, quality=92)
    return out


if __name__ == "__main__":
    nums = [int(a) for a in sys.argv[1:]] or list(EPS)
    d = os.path.dirname(os.path.abspath(__file__))
    files = [cover(n, f"{d}/covers/Cover_{n:02d}.jpg") for n in nums]
    # profile grid preview: TikTok shows covers cropped to 3:4 (y 240..1680)
    th = [Image.open(f).crop((0, 240, 1080, 1680)).resize((300, 400)) for f in files]
    cols = 3; rows = (len(th) + 2) // 3
    sheet = Image.new("RGB", (cols * 304, rows * 404), (255, 255, 255))
    for i, im in enumerate(th): sheet.paste(im, ((i % cols) * 304, (i // cols) * 404))
    sheet.save(f"{d}/covers/raster_vorschau.jpg", quality=88)
