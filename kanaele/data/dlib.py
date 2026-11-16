"""Helpers for the data channel: country flags (lipis/flag-icons, MIT) and sound-effect events (wyzowl/sfx-kit, CC0)."""
import os, subprocess
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
FLAGS = os.path.join(HERE, "assets", "flags")
os.environ.setdefault("SOUND_PY", os.path.join(HERE, "dsound.py"))
os.environ.setdefault("MBLUR", "1")      # crisp graphics: no motion blur (ghosting on fast zooms)
_cache = {}


def flag(c, code, x, y, w, a=1.0, border=(22, 24, 34)):
    """draw the 4:3 flag of an ISO country code with its top-left corner at (x, y) and width w"""
    code = code.lower()
    if code not in _cache:
        p = os.path.join(FLAGS, code + ".svg")
        if not os.path.exists(p):
            subprocess.run(["curl", "-sS", "-f", "-o", p, f"https://cdn.jsdelivr.net/gh/lipis/flag-icons@7.2.3/flags/4x3/{code}.svg"], check=True)
        _cache[code] = skia.SVGDOM.MakeFromStream(skia.Stream.MakeFromFile(p))
    dom = _cache[code]
    h = w * 0.75
    c.saveLayerAlpha(skia.Rect.MakeXYWH(x - 4, y - 4, w + 8, h + 8), int(255 * a))
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), w * 0.08, w * 0.08)
    c.save(); c.clipRRect(rr, doAntiAlias=True); c.translate(x, y); c.scale(w / 640, h / 480)
    dom.setContainerSize(skia.Size(640, 480)); dom.render(c); c.restore()
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=max(2, w * 0.04), Color=skia.Color(*border))
    c.drawRRect(rr, p)
    c.restore()


def sfx(t, sound_id, gain_db=0.0):
    """event for dsound.py: the sound's sync point lands on t"""
    return ["sfx", t, sound_id, gain_db]
