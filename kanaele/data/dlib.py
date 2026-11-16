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


# ------------------------------------------------------------------ hook kit (retention)
import math as _m
import sys as _sys
_sys.path.insert(0, os.path.join(HERE, "..", "..", "beyondexcuses"))
import lib as _lib

GOLD = (255, 200, 80)


def _back(x):
    """ease-out with overshoot (pop)"""
    x = max(0.0, min(1.0, x)); c1 = 1.9
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def rich(c, s, cx, y, size, a=1.0, base=(255, 255, 255), hi=GOLD, tf=None, stroke=16, maxw=880):
    """centred text; words between *stars* are drawn in the highlight colour"""
    tf = tf or _lib.F_CAP
    parts = s.split("*")
    f = skia.Font(tf, size)
    w = sum(f.measureText(p) for p in parts)
    if w > maxw:
        size *= maxw / w; f = skia.Font(tf, size); w = sum(f.measureText(p) for p in parts)
    x = cx - w / 2
    for k, p in enumerate(parts):
        if not p: continue
        col = hi if k % 2 else base
        c.drawString(p, x, y, f, _lib.P((0, 0, 0), a * 0.85, stroke=stroke))
        c.drawString(p, x, y, f, _lib.P(col, a))
        x += f.measureText(p)


def hook_overlay(c, t, num, l1, l2, end_at, sticky="WAIT FOR #1", hook_end=3.0, step=None, steps=None):
    """retention overlay for the data channel:
    0 s flash, two big hook lines that pop in (gold *keywords*), then a sticky reminder chip,
    a progress bar (step/steps), the series tag and the follow call at the end"""
    W = _lib.W
    # flash on the very first frames
    if t < 0.14:
        c.drawRect(skia.Rect.MakeWH(W, _lib.H), _lib.P((255, 255, 255), 0.4 * (1 - t / 0.14)))
    _lib.text(c, f"BY THE NUMBERS #{num}", 540, 236, _lib.F_SANS, 26, GOLD, 0.95, spacing=4, stroke=6)
    # progress bar
    if steps and t > 0.2:
        a = min(1.0, (t - 0.2) / 0.3) * (1 - _lib.seg(t, end_at - 0.6, end_at - 0.2))
        x0, x1, y = 300, 780, 262
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y, x1, y + 10), 5, 5), _lib.P((255, 255, 255), 0.18 * a))
        fr = max(0.0, min(1.0, step / steps))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y, x0 + (x1 - x0) * fr, y + 10), 5, 5), _lib.P(GOLD, 0.95 * a))
        _lib.text(c, f"{int(step)}/{steps}", x1 + 18, y + 11, _lib.F_SANS, 22, (220, 225, 240), a, align="left")
    # hook lines
    out = _lib.seg(t, hook_end, hook_end + 0.3)
    if out < 1:
        for i, (ln, t0) in enumerate(((l1, 0.0), (l2, 0.35))):
            if not ln or t < t0: continue
            k = _back((t - t0) / 0.32)
            s = 1.15 - 0.15 * k
            shake = 6 * _m.exp(-(t - t0) * 9) * _m.sin((t - t0) * 70)
            y = 400 + i * 96 - out * 40
            c.save(); c.translate(540 + shake, y); c.scale(s, s)
            rich(c, ln, 0, 0, 80 if i == 0 else 64, (1 - out) * min(1.0, (t - t0) / 0.08))
            c.restore()
    # sticky reminder
    if sticky and t > hook_end + 0.2:
        a = _lib.seg(t, hook_end + 0.2, hook_end + 0.5) * (1 - _lib.seg(t, end_at - 0.6, end_at - 0.2))
        pulse = 1 + 0.04 * _m.sin(t * 6)
        f = skia.Font(_lib.F_CAP, 34); w = f.measureText(sticky) + 48
        c.save(); c.translate(540, 322); c.scale(pulse, pulse)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -32, w, 50), 25, 25)
        c.drawRRect(rr, _lib.P(GOLD, 0.95 * a)); c.drawRRect(rr, _lib.P((14, 16, 30), a, stroke=4))
        _lib.text(c, sticky, 0, 6, _lib.F_CAP, 34, (20, 20, 30), a)
        c.restore()
    b = _lib.seg(t, end_at, end_at + 0.4)
    if b > 0:
        rich(c, f"Follow for part *{num + 1}*", 540, 330, 58, b)


def punch(t, t_land, amount=0.28, speed=7.0):
    """scale factor that jumps up when a number lands and settles back"""
    if t < t_land: return 1.0
    return 1 + amount * _m.exp(-(t - t_land) * speed) * _m.cos((t - t_land) * 18)


def shake(t, t_hit, amp=14, dur=0.35):
    """screen-shake offset (dx, dy) after a big hit"""
    if not (t_hit <= t < t_hit + dur): return 0.0, 0.0
    d = 1 - (t - t_hit) / dur
    return amp * d * _m.sin((t - t_hit) * 90), amp * 0.6 * d * _m.cos((t - t_hit) * 77)


def burst(c, t, t0, x, y, n=22, col=GOLD, seed=3):
    """particle burst at (x, y) starting at t0"""
    if not (t0 <= t < t0 + 0.9): return
    import random
    rnd = random.Random(seed); k = (t - t0) / 0.9
    for i in range(n):
        ang = rnd.uniform(0, 2 * _m.pi); sp = rnd.uniform(180, 420)
        px, py = x + _m.cos(ang) * sp * k, y + _m.sin(ang) * sp * k + 200 * k * k
        c.drawCircle(px, py, 7 * (1 - k) + 1, _lib.P(col, 0.9 * (1 - k)))


def finish_data(name, frame_fn, t_end, events, turn, num, l1, l2, end_at, off=0.0, sticky="WAIT FOR #1", hook_end=3.0,
                step_fn=None, steps=None):
    """like lib.finish_v2, but with the data-channel hook overlay and an opening bass hit"""
    def wrapped(c, t):
        frame_fn(c, t + off)
        hook_overlay(c, t, num, l1, l2, end_at - off, sticky, hook_end, step_fn(t + off) if step_fn else None, steps)
    ev = [list(e) for e in events]
    for e in ev: e[1] = max(0.0, e[1] - off)
    ev += [sfx(0.02, "boom-hit-medium", -3), sfx(0.05, "whoosh-fast-medium", -6), sfx(0.38, "pop-medium-in", -6)]
    _lib.finish(name, wrapped, t_end - off, ev, turn - off)


def preview(frame_fn, num, l1, l2, end_at, ts, out, off=0.0, sticky="WAIT FOR #1", hook_end=3.0, step_fn=None, steps=None):
    """contact sheet with the same overlay as the final video"""
    _lib.stills(lambda c, t: (frame_fn(c, t + off), hook_overlay(c, t, num, l1, l2, end_at - off, sticky, hook_end,
                                                                   step_fn(t + off) if step_fn else None, steps)), ts, out)
