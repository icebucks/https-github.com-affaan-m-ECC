"""Retention standard v2 helpers (episodes.md "Retention-Standard v2"), used by epNN_v2.py.
- no idle skip, no focus zoom: the first frame already shows the action
- camera punch-in at the start is mirrored at the end, so the last 0.5 s match the first 0.5 s (loop)
- hook = open question (line 1 big from frame 0, line 2 after 0.45 s), gone by HOOK_OUT
- ONE amber end line over the running action (lib.end_line), faded out before the loop frame
- CTA chip "Part N next: …" only in the last 1.2 s
- counters (chips) big and readable; sound: opening hit, turn shimmer, whoosh into the loop"""
import lib
from lib import *

HOOK_OUT = 2.6


def chip(c, x, y, s, col, size=40, a=1.0, pop=1.0):
    if a <= 0: return
    w_ = skia.Font(F_SANS, size).measureText(tr(s)) + size * 1.3
    h_ = size * 1.6
    c.save(); c.translate(x, y); c.scale(pop, pop)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w_ / 2, -h_ / 2, w_, h_), h_ / 2, h_ / 2)
    c.drawRRect(rr, P((20, 20, 30), 0.86 * a)); c.drawRRect(rr, P(col, a, stroke=4))
    text(c, s, 0, size * 0.36, F_SANS, size, col, a)
    c.restore()


def overlay(c, t, dur, num, hook, cta, end_t0, end_txt):
    text(c, f"MINDSET-SERIE #{num}", 540, 300, F_SANS, 32, AMBER, 0.95, spacing=3, stroke=7)
    a = 1 - seg(t, HOOK_OUT - 0.4, HOOK_OUT)
    if a > 0:
        for i, ln in enumerate(hook.split("\n")):
            t0 = 0.45 * i
            if t < t0: continue
            k = t - t0
            pop = 1 + (0.12 if i == 0 else 0.1) * (1 - ease(k / 0.25))
            size = 86 if i == 0 else 64
            w_ = skia.Font(F_CAP, size).measureText(tr(ln)); size *= min(1.0, 860 / w_) if w_ else 1
            y = 392 if i == 0 else 480
            c.save(); c.translate(540, y); c.scale(pop, pop)
            text(c, ln, 0, 0, F_CAP, size, (255, 255, 255) if i == 0 else (255, 226, 160), a * min(1.0, k / 0.06), stroke=16)
            c.restore()
    # the save-worthy line, over the action, gone before the loop frame
    fa = 1 - seg(t, dur - 0.75, dur - 0.45)
    if t >= end_t0 and fa > 0:
        c.saveLayerAlpha(None, int(255 * fa)); lib.end_line(c, t, end_t0, end_txt); c.restore()
    # CTA chip: last 1.2 s only
    t0 = dur - 1.2
    if t >= t0 and cta:
        b = seg(t, t0, t0 + 0.2) * (1 - seg(t, dur - 0.3, dur - 0.04)); pop = 1 + 0.12 * (1 - ease((t - t0) / 0.25))
        l1, l2 = (cta.split("\n") + [""])[:2]
        c.save(); c.translate(540, 420); c.scale(pop, pop)
        w_ = max(skia.Font(F_CAP, 46).measureText(tr(l1)), skia.Font(F_CAP, 40).measureText(tr(l2))) + 70
        w_ = min(w_, 900); sc = min(1.0, 830 / (w_ - 70))
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w_ / 2, -56, w_, 132), 34, 34)
        c.drawRRect(rr, P((20, 20, 30), 0.8 * b)); c.drawRRect(rr, P(AMBER, b, stroke=4))
        text(c, l1, 0, -2, F_CAP, 46 * sc, AMBER, b)
        text(c, l2, 0, 52, F_CAP, 40 * sc, (255, 255, 255), b)
        c.restore()


_GR = None


def camera_z(t, dur):
    """punch-in at the start, mirrored at the end (loop), slight drift in between"""
    return 1 + 0.08 * (1 - ease(t / 0.6)) + 0.08 * ease((t - (dur - 0.55)) / 0.55) + 0.02 * math.sin(math.pi * t / dur)


def wrap(frame_fn, dur, num, hook, cta, end_t0, end_txt):
    global _GR
    if _GR is None: _GR = lib._grade_paint()

    def wrapped(c, t):
        z = camera_z(t, dur)
        c.save(); c.translate(540, 900); c.scale(z, z); c.translate(-540, -900)
        c.saveLayer(None, _GR); frame_fn(c, t); c.restore(); c.restore()
        overlay(c, t, dur, num, hook, cta, end_t0, end_txt)
    return wrapped


def finish_loop(name, frame_fn, dur, events, turn, num, hook, cta, end_t0, end_txt):
    ev = [list(e) for e in events] + [["pop", 0.05]]
    dsound = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kanaele", "data", "dsound.py")
    if os.path.exists(dsound):
        os.environ.setdefault("SOUND_PY", dsound)
        ev += [["sfx", 0.02, "boom-hit-medium", -5], ["sfx", 0.06, "whoosh-medium-soft", -6],
               ["sfx", turn, "shimmer-medium-bright", -8], ["sfx", turn, "pop-large-in", -8],
               ["sfx", dur - 0.45, "whoosh-medium-soft", -8]]
    lib.finish(name, wrap(frame_fn, dur, num, hook, cta, end_t0, end_txt), dur, ev, turn)


def main(name, frame_fn, dur, events, turn, num, hook, cta, end_t0, end_txt, tag, still_ts):
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        ts = [float(a) for a in sys.argv[2:]] or still_ts
        os.makedirs("check", exist_ok=True)
        stills(wrap(frame_fn, dur, num, hook, cta, end_t0, end_txt), ts, f"check/{tag}")
        print(f"check/{tag}_sheet.jpg")
    elif cmd == "qa":
        probs = figure_qa(frame_fn, dur, fps=15)
        print(f"figure QA: {len(probs)} problem(s)"); print("\n".join(probs[:40]))
    else:
        finish_loop(name, frame_fn, dur, events, turn, num, hook, cta, end_t0, end_txt)
