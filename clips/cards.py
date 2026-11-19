"""Animated intro and outro (1920x1080, 30 fps, AAC 48 kHz stereo – same format as the compile.py segments, so concat -c copy works).
  intro: logo pops in with a glow ring, title slides up, gold line, subtitle; boom + whoosh + shimmer, short synth bed.
  outro: 12 s end screen – logo + "SUBSCRIBE" left (room for YouTube's round subscribe element), two 16:9 "WATCH NEXT"
         frames right (place YouTube's end-screen video elements exactly over them in YouTube Studio)."""
import json, math, os, subprocess, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "beyondexcuses")); sys.path.insert(0, os.path.join(ROOT, "kanaele", "data"))
import skia
import lib
from lib import P, C, F_CAP, F_SANS, ease, seg, clamp, lerp
from PIL import Image, ImageFilter, ImageEnhance

W, H, FPS, SR = 1920, 1080, 30, 48000
GOLD = (255, 200, 80)
LOGO = os.path.join(HERE, "assets", "logo_badge.png")
SFX = os.path.join(ROOT, "kanaele", "data", "assets", "sfx")
# end-screen layout (pixels): subscribe circle and two video frames
SUB = (420, 470, 170)                         # centre x, y, radius
VIDS = [(1010, 150, 760, 428), (1010, 620, 520, 292)]   # x, y, w, h (16:9)


def _bg(src, t_at, blur=18, dark=0.55):
    """blurred, darkened still from the game footage (or a plain gradient)"""
    if src:
        tmp = tempfile.mktemp(suffix=".png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t_at), "-i", src, "-frames:v", "1", "-vf", f"scale={W}:{H}", tmp], check=True)
        im = Image.open(tmp).convert("RGB"); os.remove(tmp)
        im = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(blur))).enhance(dark)
    else:
        im = Image.new("RGB", (W, H), (14, 16, 30))
    arr = np.dstack([np.asarray(im), np.full((H, W), 255, np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType)


def _logo():
    arr = np.asarray(Image.open(LOGO).convert("RGBA"))
    return skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType)


def _back(x):   # overshoot ease
    x = clamp(x); s = 1.9
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def _draw_bg(c, bg, t, dur, zoom=0.06):
    z = 1 + zoom * t / dur
    c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    c.drawImageRect(bg, skia.Rect.MakeWH(W, H))
    c.restore()
    vg = skia.GradientShader.MakeRadial((W / 2, H / 2), W * 0.75, [C((0, 0, 0), 0.0), C((0, 0, 0), 0.65)], [0.45, 1.0])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=vg))


def _particles(c, t, n=60, seed=3, a=1.0):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x0, y0, sp, r, ph = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(10, 40), rng.uniform(1.2, 3.2), rng.uniform(0, 6.3)
        y = (y0 - t * sp) % H
        c.drawCircle(x0 + 12 * math.sin(t * 0.8 + ph), y, r, P(GOLD, a * (0.25 + 0.25 * math.sin(t * 2 + ph))))


def _logo_at(c, logo, x, y, size, a=1.0):
    if size < 2 or a <= 0: return
    paint = skia.Paint(AntiAlias=True); paint.setAlphaf(a)
    c.drawImageRect(logo, skia.Rect.MakeXYWH(x - size / 2, y - size / 2, size, size), skia.SamplingOptions(skia.FilterMode.kLinear), paint)


def _fit(s, size, maxw, tf=None):
    tf = tf or F_CAP
    w = skia.Font(tf, size).measureText(s)
    return size * min(1.0, maxw / w) if w else size


def intro_frame(c, t, bg, logo, title, subtitle, dur):
    _draw_bg(c, bg, t, dur)
    _particles(c, t)
    # logo pop + glow ring
    k = _back(t / 0.45)
    cx, cy = W / 2, 330
    ring = seg(t, 0.05, 0.9)
    if 0 < ring < 1:
        c.drawCircle(cx, cy, 120 + 260 * ring, P(GOLD, 0.6 * (1 - ring), stroke=8))
    c.drawCircle(cx, cy, 150, P(GOLD, 0.25 * seg(t, 0.1, 0.4), blur=40))
    _logo_at(c, logo, cx, cy, 240 * max(0.0, k), seg(t, 0.0, 0.08))
    # title slides up
    a = seg(t, 0.55, 0.85); dy = 60 * (1 - ease((t - 0.55) / 0.4))
    size = _fit(title, 118, 1700)
    lib.text(c, title, W / 2, 610 + dy, F_CAP, size, (255, 255, 255), a, stroke=14)
    # gold line grows from the centre
    g = ease((t - 0.85) / 0.4)
    if g > 0:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(W / 2 - 420 * g, 650, W / 2 + 420 * g, 662), 6, 6), P(GOLD))
    lib.text(c, subtitle, W / 2, 740, F_SANS, 54, GOLD, seg(t, 1.0, 1.3), stroke=8)
    # flash in, whip out
    if t < 0.12: c.drawRect(skia.Rect.MakeWH(W, H), P((255, 255, 255), 0.6 * (1 - t / 0.12)))
    out = seg(t, dur - 0.35, dur)
    if out > 0: c.drawRect(skia.Rect.MakeWH(W, H), P((255, 255, 255), 0.55 * out))


def outro_frame(c, t, bg, logo, dur):
    _draw_bg(c, bg, t, dur, zoom=0.04)
    c.drawRect(skia.Rect.MakeWH(W, H), P((10, 12, 24), 0.35))
    _particles(c, t, 70, seed=5)
    a = seg(t, 0.0, 0.5)
    x, y, r = SUB
    k = _back(t / 0.5)
    pulse = 1 + 0.04 * math.sin(t * 3.2)
    c.drawCircle(x, y, (r + 26) * pulse, P(GOLD, 0.35 * a, blur=30))
    c.drawCircle(x, y, (r + 12) * max(0, k), P(GOLD, a, stroke=10))
    c.save(); c.clipPath(skia.Path().addCircle(x, y, r * max(0.0, k)), doAntiAlias=True)
    _logo_at(c, logo, x, y, 2.3 * r * max(0.0, k), a)   # badge filled into the round subscribe spot
    c.restore()
    lib.text(c, "SUBSCRIBE", x, y + r + 120, F_CAP, 92, (255, 255, 255), seg(t, 0.3, 0.7), stroke=12)
    lib.text(c, "new GTA 6 videos every day", x, y + r + 190, F_SANS, 44, GOLD, seg(t, 0.5, 0.9), stroke=6)
    lib.text(c, "WATCH NEXT", VIDS[0][0] + VIDS[0][2] / 2, VIDS[0][1] - 30, F_CAP, 52, (255, 255, 255), seg(t, 0.6, 1.0), stroke=8)
    for i, (vx, vy, vw, vh) in enumerate(VIDS):
        b = seg(t, 0.7 + 0.2 * i, 1.1 + 0.2 * i)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(vx, vy, vw, vh), 18, 18)
        c.drawRRect(rr, P((0, 0, 0), 0.45 * b))
        c.drawRRect(rr, P(GOLD if i == 0 else (230, 232, 245), 0.9 * b, stroke=6))
        lib.text(c, "▶", vx + vw / 2, vy + vh / 2 + 30, F_SANS, 90, (255, 255, 255), 0.5 * b)
    out = seg(t, dur - 0.6, dur)
    if out > 0: c.drawRect(skia.Rect.MakeWH(W, H), P((0, 0, 0), out))


def _audio(path, dur, sfx, style, bpm, seed, fade_in=0.0, fade_out=0.6, gain=0.32):
    import soundfile as sf
    from scipy.signal import resample_poly
    import music
    n = int(dur * SR)
    bed = music.render(style, bpm, dur + 0.5, dict(build=1e9, drop=0.0, outro=1e9), seed=seed)   # full groove from the start
    bed = resample_poly(bed, SR, music.SR, axis=0)[:n]
    bed = np.pad(bed, ((0, max(0, n - len(bed))), (0, 0)))
    env = np.ones(n)
    if fade_in: env[:int(fade_in * SR)] = np.linspace(0, 1, int(fade_in * SR))
    env[-int(fade_out * SR):] *= np.linspace(1, 0, int(fade_out * SR))
    mix = bed * env[:, None] * gain
    meta = {m["id"]: m for m in json.load(open(os.path.join(SFX, "sounds.json")))["sounds"]}
    for sid, at, g in sfx:
        x, sr = sf.read(os.path.join(SFX, meta[sid]["file"]), dtype="float32")
        if x.ndim == 1: x = np.stack([x, x], 1)
        if sr != SR: x = resample_poly(x, SR, sr, axis=0)
        i = max(0, int((at - meta[sid]["sync"]["at"]) * SR))
        mix[i:i + len(x)] += x[: n - i] * 10 ** (g / 20)
    mix = np.tanh(mix * 1.1) / 1.1
    sf.write(path, mix.astype(np.float32), SR)


def _render(frame_fn, dur, wav, out):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2", "-shortest", out],
                          stdin=subprocess.PIPE)
    for f in range(int(dur * FPS)):
        t = f / FPS
        c.clear(skia.ColorBLACK); frame_fn(c, t)
        ff.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    ff.stdin.close(); ff.wait()
    return out


def intro(src, t_at, title, subtitle, out, dur=4.0):
    bg, logo = _bg(src, t_at), _logo()
    wav = out + ".wav"
    _audio(wav, dur, [("boom-hit-medium", 0.03, -2), ("whoosh-fast-medium", 0.5, -6), ("shimmer-medium-bright", 0.9, -9),
                      ("whoosh-fast-medium", dur - 0.3, -6)], "synthwave", 120, 7, fade_out=0.35)
    _render(lambda c, t: intro_frame(c, t, bg, logo, title, subtitle, dur), dur, wav, out)
    os.remove(wav)
    return out


def outro(src, t_at, out, dur=12.0):
    bg, logo = _bg(src, t_at, blur=24, dark=0.45), _logo()
    wav = out + ".wav"
    _audio(wav, dur, [("whoosh-slow-medium", 0.05, -6), ("pop-large-in", 0.45, -8), ("shimmer-long-sparkle", 0.8, -10)],
           "synthwave", 120, 9, fade_in=0.3, fade_out=1.5, gain=0.28)
    _render(lambda c, t: outro_frame(c, t, bg, logo, dur), dur, wav, out)
    os.remove(wav)
    return out


if __name__ == "__main__":   # preview stills: python3 clips/cards.py <video> <t> <out_prefix>
    src, t_at, pre = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    bg, logo = _bg(src, t_at), _logo()
    surf = skia.Surface(W, H); c = surf.getCanvas()
    shots = []
    for name, fn, ts in (("intro", lambda c, t: intro_frame(c, t, bg, logo, "GTA 6 · PURE GAMEPLAY", "No Commentary · Spoilers", 4.0), (0.2, 1.6)),
                         ("outro", lambda c, t: outro_frame(c, t, bg, logo, 12.0), (0.3, 3.0))):
        for t in ts:
            c.clear(skia.ColorBLACK); fn(c, t)
            shots.append(Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]).resize((960, 540)))
    sheet = Image.new("RGB", (1920, 1080))
    for i, im in enumerate(shots): sheet.paste(im, ((i % 2) * 960, (i // 2) * 540))
    sheet.save(pre + "_cards.jpg", quality=88); print(pre + "_cards.jpg")
