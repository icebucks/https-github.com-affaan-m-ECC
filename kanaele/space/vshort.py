"""Narrated vertical Shorts for By The Numbers – SPACE series (George voice, word-by-word captions).

An episode file (shorts/ssN.py) defines a SPEC dict and its own scene functions, then calls vshort.main(SPEC).
    SPEC = dict(
        num=1, name="SS1_SunEarths", style="cinematic", bpm=96, tint=(30, 26, 70), speed=0.97,
        hook=("You could pour *1.3 MILLION*", "Earths into the Sun"),       # on-screen hook, gold *words*
        beats=[ (scene_fn, "spoken text with {display|spoken} numbers", dict(head="1.3 MILLION EARTHS", drop=False)), ...],
        question=("Guess before it loops:", "how many *Moons* fit in Earth?"),   # end card (comment bait)
    )
    scene_fn(c, t, u, b) draws the stage for one beat: t = video time, u = 0..1 progress of the beat, b = the beat dict
    (b["start"], b["end"], b["words"], b["i"], b["head"] ...). Draw inside the STAGE box; the engine adds background
    camera, headline, captions, hook, tag, progress bar and the end card.

Layout (TikTok/Shorts safe zones, audit.py):
    y < 210 nothing · tag y 238 · hook / headline y 300–520 · STAGE y 560–1180 · captions y 1230–1400 · y ≥ 1450 nothing
    important text ends at x 880 between y 760 and 1660 (button column).
Usage: python3 shorts/ssN.py still | render | cover
"""
import os, sys, json, math, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "beyondexcuses"))
sys.path.insert(0, os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
os.environ.setdefault("MBLUR", "1")
import skia
import lib
from lib import P, C, F_CAP, F_SANS, ease, seg, clamp, lerp
import dlib
from dlib import rich, punch, burst, GOLD
import voice

W, H, FPS = 1080, 1920, 30
WHITE, MUTED, BLUE, RED = (245, 246, 250), (175, 182, 210), (140, 200, 255), (255, 120, 110)
STAGE = (60, 560, 1020, 1180)          # x0, y0, x1, y1
SX, SY = 480, 870                       # stage centre (left of the button column)
GAP, LEAD, TAIL = 0.28, 0.15, 3.2       # pause between beats, start offset, end card length

# ------------------------------------------------------------------ drawing kit
BODIES = {   # base colour, second colour (bands / shade), glow
    "sun": ((255, 196, 70), (255, 120, 30), (255, 170, 60)), "mercury": ((170, 160, 150), (110, 104, 98), None),
    "venus": ((235, 200, 140), (190, 150, 90), None), "earth": ((70, 140, 230), (60, 170, 90), None),
    "moon": ((200, 200, 205), (140, 140, 150), None), "mars": ((215, 100, 60), (160, 70, 40), None),
    "jupiter": ((215, 180, 140), (170, 110, 70), None), "saturn": ((230, 205, 150), (190, 160, 100), None),
    "uranus": ((150, 220, 230), (110, 190, 210), None), "neptune": ((70, 110, 230), (50, 80, 190), None),
    "pluto": ((210, 185, 160), (150, 120, 100), None), "redstar": ((255, 110, 70), (200, 60, 40), (255, 90, 60)),
    "bluestar": ((170, 200, 255), (110, 150, 255), (150, 190, 255)), "neutron": ((230, 240, 255), (160, 190, 255), (180, 210, 255)),
    "blackhole": ((0, 0, 0), (255, 170, 80), None),
}
_rng = np.random.default_rng(7)
STARS = [(_rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(0.6, 2.6), _rng.uniform(0.25, 0.95), _rng.uniform(0, 6.28)) for _ in range(380)]


def space(c, t, tint=(28, 30, 80)):
    """deep-space background with a coloured nebula glow and twinkling, slowly drifting stars"""
    sh = skia.GradientShader.MakeRadial((W * 0.62, H * 0.38), H * 0.75, [C(tint), C((6, 7, 18))], [0.0, 1.0])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    for x, y, r, a, ph in STARS:
        tw = 0.65 + 0.35 * math.sin(t * 1.7 + ph)
        c.drawCircle((x + t * 9 * r) % W, (y - t * 3 * r) % H, r, P(WHITE, a * tw))


def body(c, kind, x, y, r, t=0.0, a=1.0, label=None, label_col=WHITE, rot=0.0):
    """shaded sphere for a planet / star / moon; label under it"""
    if r < 0.4 or a <= 0: return
    base, sec, glow = BODIES[kind]
    c.saveLayerAlpha(skia.Rect.MakeXYWH(x - r * 3, y - r * 3, r * 6, r * 6), int(255 * a)) if a < 1 else c.save()
    if kind == "blackhole":
        for k in range(3):
            c.drawCircle(x, y, r * (1.35 + 0.25 * k), P(sec, 0.35 - 0.1 * k, stroke=max(1, r * 0.12)))
        c.drawCircle(x, y, r, P((0, 0, 0)))
        c.restore(); return
    if glow:
        g = skia.GradientShader.MakeRadial((x, y), r * 1.9, [C(glow, 0.55), C(glow, 0.0)], [0.45, 1.0])
        c.drawCircle(x, y, r * 1.9, skia.Paint(Shader=g, AntiAlias=True))
    if kind == "saturn":
        ring = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=max(1.5, r * 0.22), Color=skia.Color(*sec, 200))
        c.save(); c.translate(x, y); c.rotate(-18); c.drawOval(skia.Rect.MakeLTRB(-r * 2.1, -r * 0.55, r * 2.1, r * 0.55), ring); c.restore()
    sh = skia.GradientShader.MakeRadial((x - r * 0.35, y - r * 0.4), r * 1.45, [C(tuple(min(255, v + 40) for v in base)), C(base), C(tuple(int(v * 0.35) for v in base))], [0.0, 0.55, 1.0])
    c.drawCircle(x, y, r, skia.Paint(Shader=sh, AntiAlias=True))
    if kind in ("jupiter", "saturn") and r > 6:
        c.save(); c.clipPath(skia.Path().addCircle(x, y, r), doAntiAlias=True)
        for k, yy in enumerate((-0.45, -0.15, 0.2, 0.5)):
            c.drawRect(skia.Rect.MakeLTRB(x - r, y + yy * r, x + r, y + (yy + 0.1 + 0.04 * (k % 2)) * r), P(sec, 0.55))
        if kind == "jupiter": c.drawOval(skia.Rect.MakeXYWH(x + r * 0.15, y + r * 0.22, r * 0.32, r * 0.18), P((200, 90, 60), 0.85))
        c.restore()
    if kind == "earth" and r > 5:
        c.save(); c.clipPath(skia.Path().addCircle(x, y, r), doAntiAlias=True)
        for dx, dy, s in ((-0.3, -0.2, 0.42), (0.35, 0.25, 0.34), (0.1, -0.55, 0.22), ((-0.1 + rot) % 2 - 1, 0.5, 0.25)):
            c.drawOval(skia.Rect.MakeXYWH(x + (dx - s / 2) * r, y + (dy - s / 3) * r, s * r, s * r * 0.7), P(sec, 0.95))
        c.restore()
    if kind in ("sun", "redstar", "bluestar"):
        # hot core + limb darkening + fine granulation
        core = skia.GradientShader.MakeRadial((x, y), r, [C((255, 250, 225), 0.85), C(base, 0.0)], [0.0, 0.7])
        c.drawCircle(x, y, r, skia.Paint(Shader=core, AntiAlias=True))
        limb = skia.GradientShader.MakeRadial((x, y), r, [C(sec, 0.0), C(sec, 0.0), C(sec, 0.75)], [0.0, 0.72, 1.0])
        c.drawCircle(x, y, r, skia.Paint(Shader=limb, AntiAlias=True))
        if r > 40:
            rnd = np.random.default_rng(5)
            for k in range(46):
                ang = rnd.uniform(0, 6.283) + t * 0.05; rr = r * math.sqrt(rnd.uniform(0, 0.85))
                c.drawCircle(x + math.cos(ang) * rr, y + math.sin(ang) * rr, r * rnd.uniform(0.03, 0.07), P(sec, 0.10 + 0.06 * math.sin(t * 2 + k)))
    c.restore()
    if label:
        lib.text(c, label, x, y + r + 46, F_CAP, 34, label_col, a, stroke=8)


def big(c, s, x, y, size, col=GOLD, a=1.0, t=0.0, land=None):
    """big number / word with a punch when it lands"""
    if a <= 0: return
    k = punch(t, land) if land is not None else 1.0
    c.save(); c.translate(x, y); c.scale(k, k)
    lib.text(c, s, 0, 0, F_CAP, size, col, a, stroke=18)
    c.restore()


def counter(v, u, decimals=0):
    """value that counts up with ease-out over u in 0..1, formatted with thousands separators"""
    x = v * (1 - (1 - clamp(u)) ** 3)
    return f"{x:,.{decimals}f}"


def bar(c, x, y, w, h, frac, col, a=1.0):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), h / 2, h / 2), P(WHITE, 0.12 * a))
    if frac > 0:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, max(h, w * clamp(frac)), h), h / 2, h / 2), P(col, 0.95 * a))


def fade(u, a=0.08, b=0.92):
    """alpha that fades in at the start and out at the end of a beat"""
    return seg(u, 0, a) * (1 - seg(u, b, 1.0))


# ------------------------------------------------------------------ timeline
def build(spec):
    d = os.path.join(HERE, "shorts", "audio", spec["name"]); os.makedirs(d, exist_ok=True)
    t = LEAD; beats = []
    for i, (fn, text, opt) in enumerate(spec["beats"]):
        wav = os.path.join(d, f"b{i:02d}.wav")
        dur = voice.synth(text, wav, spec.get("speed", 0.97))
        ws = [(w, t + a, t + b) for w, a, b in voice.words(text, wav)]
        beats.append(dict(opt, i=i, fn=fn, text=text, wav=wav, start=t, end=t + dur, words=ws))
        t += dur + opt.get("pause", GAP)
    spec["beats_tl"] = beats
    spec["q_at"] = beats[-1]["end"] + 0.25
    spec["t_end"] = spec["q_at"] + TAIL
    return spec


def current(spec, t):
    bs = spec["beats_tl"]
    for k, b in enumerate(bs):
        nxt = bs[k + 1]["start"] if k + 1 < len(bs) else spec["t_end"]
        if t < nxt: return b, clamp((t - b["start"]) / max(0.01, nxt - b["start"]))
    return bs[-1], 1.0


# ------------------------------------------------------------------ overlay
def captions(c, spec, t):
    """2–3 words at a time, the spoken word in gold with a pop; under the stage, above the TikTok caption"""
    words = [w for b in spec["beats_tl"] for w in b["words"]]
    cur = None
    for k, (w, a, b) in enumerate(words):
        if a - 0.05 <= t < (words[k + 1][1] if k + 1 < len(words) else b + 0.4): cur = k; break
    if cur is None: return
    # chunk: split before a word when the previous one ends a sentence or the chunk has 3 words
    chunks, ch = [], []
    for k, (w, a, b) in enumerate(words):
        if ch and (len(ch) == 3 or words[ch[-1]][0][-1] in ".,?!:;" or a - words[ch[-1]][2] > 0.35):
            chunks.append(ch); ch = []
        ch.append(k)
    chunks.append(ch)
    grp = next(g for g in chunks if cur in g)
    f = skia.Font(F_CAP, 76)
    texts = [words[k][0].upper() for k in grp]
    sp = f.measureText(" ") * 1.4
    widths = [f.measureText(s) for s in texts]
    total = sum(widths) + sp * (len(texts) - 1)
    scale = min(1.0, 780 / total)
    x = 470 - total * scale / 2; y = 1330
    c.save(); c.translate(x, y); c.scale(scale, scale)
    xx = 0
    for k, s, wd in zip(grp, texts, widths):
        on = k == cur
        pk = 1 + 0.12 * math.exp(-(t - words[k][1]) * 14) if on and t >= words[k][1] else 1.0
        c.save(); c.translate(xx + wd / 2, 0); c.scale(pk, pk)
        c.drawString(s, -wd / 2, 0, f, P((0, 0, 0), 0.9, stroke=20))
        c.drawString(s, -wd / 2, 0, f, P(GOLD if on else WHITE))
        c.restore()
        xx += wd + sp
    c.restore()


def overlay(c, spec, t):
    b, u = current(spec, t)
    q = spec["q_at"]
    if t < 0.14: c.drawRect(skia.Rect.MakeWH(W, H), P(WHITE, 0.4 * (1 - t / 0.14)))
    lib.text(c, f"BY THE NUMBERS · SPACE #{spec['num']}", 540, 238, F_SANS, 30, GOLD, 0.95, spacing=4, stroke=6)
    # progress bar: beats done
    n = len(spec["beats_tl"])
    a = seg(t, 0.2, 0.5) * (1 - seg(t, q - 0.4, q))
    if a > 0:
        x0, x1, y = 300, 780, 262
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y, x1, y + 10), 5, 5), P(WHITE, 0.18 * a))
        fr = clamp((b["i"] + u) / n)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y, x0 + (x1 - x0) * fr, y + 10), 5, 5), P(GOLD, 0.95 * a))
    # hook: two big lines during the first beat, then the per-beat headline
    h_end = spec["beats_tl"][0]["end"]
    out = seg(t, h_end - 0.1, h_end + 0.25)
    if out < 1:
        for i, (ln, t0) in enumerate(zip(spec["hook"], (0.0, 0.3))):
            if t < t0: continue
            k = dlib._back((t - t0) / 0.3)
            s = 1.15 - 0.15 * k
            c.save(); c.translate(540, 400 + i * 96 - out * 30); c.scale(s, s)
            rich(c, ln, 0, 0, 82 if i == 0 else 66, (1 - out) * min(1.0, (t - t0) / 0.08))
            c.restore()
    elif b.get("head") and t < q:
        k = dlib._back((t - b["start"]) / 0.3)
        a = min(1.0, (t - b["start"]) / 0.1) * (1 - seg(u, 0.94, 1.0) if b["i"] + 1 < n else 1.0) * (1 - seg(t, q - 0.3, q))
        c.save(); c.translate(540, 440); c.scale(0.85 + 0.15 * k, 0.85 + 0.15 * k)
        rich(c, b["head"], 0, 0, 74, a, maxw=900)
        c.restore()
    if t < q: captions(c, spec, t)
    dlib.end_card(c, t, q, spec["question"][0], spec["question"][1], spec["question"][2], y=1080)


LOOP = 0.5     # last seconds cross-fade into the opening frame -> seamless loop


def frame_fn(spec):
    def raw(c, t):
        b, u = current(spec, t)
        space(c, t, spec.get("tint", (28, 30, 80)))
        if t < 1.4:   # bright, colourful first second: warm glow behind the hook
            g = skia.GradientShader.MakeRadial((SX, SY), 900, [C(GOLD, 0.30 * (1 - t / 1.4)), C(GOLD, 0.0)], [0.0, 1.0])
            c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=g))
        # camera: punch-in at each beat start, steady push and a slow floating drift (never a static frame)
        ts = t - b["start"]
        z = 1 + 0.07 * math.exp(-max(0, ts) * 5) + 0.06 * ease(u)
        dx, dy = dlib.shake(t, b["start"], 10, 0.3) if b.get("drop") else (0, 0)
        dx += 14 * math.sin(t * 0.9); dy += 10 * math.sin(t * 0.7 + 1.0)
        rot = 0.8 * math.sin(t * 0.5)
        c.save(); c.translate(SX + dx, SY + dy); c.rotate(rot); c.scale(z, z); c.translate(-SX, -SY)
        b["fn"](c, t, u, b)
        c.restore()
        if b.get("drop") and ts < 0.18: c.drawRect(skia.Rect.MakeWH(W, H), P(WHITE, 0.35 * (1 - ts / 0.18)))
        overlay(c, spec, t)

    def frame(c, t):
        raw(c, t)
        k = seg(t, spec["t_end"] - LOOP, spec["t_end"] - 1 / FPS)
        if k > 0:
            c.saveLayerAlpha(skia.Rect.MakeWH(W, H), int(255 * k))
            raw(c, 0.5)
            c.restore()
    return frame


# ------------------------------------------------------------------ sound
def build_audio(spec, out):
    import soundfile as sf
    from scipy.signal import resample_poly
    import music
    SR = 44100; T = spec["t_end"]; n = int(T * SR) + SR
    vo = np.zeros(n, np.float32)
    for b in spec["beats_tl"]:
        x, sr = sf.read(b["wav"], dtype="float32")
        if sr != SR: x = resample_poly(x, SR, sr).astype(np.float32)
        i = int(b["start"] * SR); vo[i:i + len(x)] += x[: n - i]
    drops = [b["start"] for b in spec["beats_tl"] if b.get("drop")]
    drop = drops[0] if drops else spec["beats_tl"][len(spec["beats_tl"]) // 2]["start"]
    bed = music.render(spec["style"], spec["bpm"], T + 0.5, dict(build=max(0.5, drop - 4.0), drop=drop, outro=spec["q_at"]), seed=spec["num"] * 7 + 3)
    bed = np.pad(bed, ((0, max(0, n - len(bed))), (0, 0)))[:n]
    env = np.convolve(np.abs(vo), np.ones(int(0.2 * SR)) / int(0.2 * SR), mode="same")
    duck = 1 - 0.7 * np.clip(env / (env.max() * 0.12 + 1e-9), 0, 1)
    mix = bed * (0.30 * duck)[:, None] + vo[:, None] * 0.95
    meta = {m["id"]: m for m in json.load(open(os.path.join(HERE, "..", "data", "assets", "sfx", "sounds.json")))["sounds"]}
    def add(sid, at, g):
        x, sr = sf.read(os.path.join(HERE, "..", "data", "assets", "sfx", meta[sid]["file"]), dtype="float32")
        if x.ndim == 1: x = np.stack([x, x], 1)
        if sr != SR: x = resample_poly(x, SR, sr, axis=0).astype(np.float32)
        i = int((at - meta[sid]["sync"]["at"]) * SR)
        if i < 0: x = x[-i:]; i = 0
        mix[i:i + len(x)] += x[: n - i] * 10 ** (g / 20)
    add("boom-hit-medium", 0.02, -3); add("whoosh-fast-medium", 0.05, -8)
    for b in spec["beats_tl"][1:]:
        add("whoosh-fast-medium" if b["i"] % 2 else "whoosh-slow-medium", b["start"], -15)
        if b.get("head"): add("pop-medium-in", b["start"] + 0.05, -14)
    for d in drops: add("cinematic-drum-big", d, -7)
    add("pop-medium-in", spec["q_at"], -8)
    mix = np.tanh(mix * 1.05) / 1.05
    sf.write(out + ".raw.wav", mix[: int(T * SR)], SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out + ".raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", out], check=True)
    os.remove(out + ".raw.wav")


def render(spec):
    d = os.path.join(HERE, "shorts"); name = spec["name"]
    frame = frame_fn(spec)
    surf = skia.Surface(W, H); c = surf.getCanvas()
    tmp = os.path.join(d, name + "_v.part.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(int(spec["t_end"] * FPS)):
        t = f / FPS; lib.NOW = t
        c.clear(skia.ColorBLACK); frame(c, t)
        ff.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    ff.stdin.close(); ff.wait()
    audio = os.path.join(d, name + "_a.wav"); build_audio(spec, audio)
    out = os.path.join(d, name + "_EN.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", out], check=True)
    os.remove(tmp); os.remove(audio)
    return out


def stills(spec, out):
    from PIL import Image
    frame = frame_fn(spec)
    ts = [0.05, 0.6, 1.6] + [(b["start"] + b["end"]) / 2 for b in spec["beats_tl"][1:]] + [spec["q_at"] + 1.5, spec["t_end"] - 0.05]
    tiles = []
    for t in ts:
        surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.ColorBLACK); lib.NOW = t; frame(c, t)
        im = Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]).resize((360, 640))
        tiles.append(im)
    cols = 5; rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (360 * cols, 640 * rows))
    for i, im in enumerate(tiles): sheet.paste(im, ((i % cols) * 360, (i // cols) * 640))
    sheet.save(out, quality=88)
    return out


def cover(spec, t, lines):
    """thumbnail (1080x1920) from a frame of the video: bright scene, 2–3 huge lines on a soft dark band (inside the 3:4 crop y 240–1680)"""
    from PIL import Image
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.ColorBLACK); lib.NOW = t
    b, u = current(spec, t); space(c, t, spec.get("tint", (28, 30, 80)))
    c.save(); c.translate(SX, SY + 120); c.scale(1.1, 1.1); c.translate(-SX, -SY); b["fn"](c, t, u, b); c.restore()
    hgt = sum(sz * 1.12 for _, sz in lines)
    y0 = 420
    sh = skia.GradientShader.MakeLinear([(0, y0 - 120), (0, y0 + hgt + 80)], [C((6, 7, 18), 0.0), C((6, 7, 18), 0.78), C((6, 7, 18), 0.0)], [0, 0.5, 1])
    c.drawRect(skia.Rect.MakeXYWH(0, y0 - 120, W, hgt + 200), skia.Paint(Shader=sh))
    lib.text(c, "BY THE NUMBERS · SPACE", 540, y0 - 40, F_SANS, 34, GOLD, 1.0, spacing=4, stroke=6)
    y = y0 + lines[0][1] * 0.8
    for ln, size in lines:
        rich(c, ln, 540, y, size, 1.0, stroke=22, maxw=980); y += size * 1.12
    out = os.path.join(HERE, "shorts", f"Cover_{spec['name'].split('_')[0]}.jpg")
    Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]).save(out, quality=93)
    return out


def main(spec):
    import overlap
    overlap.check(spec)
    build(spec)
    print(f"{spec['name']}: {spec['t_end']:.1f} s, {len(spec['beats_tl'])} beats", file=sys.stderr)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "still"
    if cmd == "still":
        print(stills(spec, os.path.join(HERE, "shorts", f"check_{spec['name']}.jpg")))
    elif cmd == "render":
        print(render(spec))
    elif cmd == "cover":
        print(cover(spec, spec["cover"][0], spec["cover"][1]))
