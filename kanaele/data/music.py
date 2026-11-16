"""Own procedural music for the data channel – 5 styles, arranged to the video.
Everything is synthesised here (no samples, no foreign music), so every track is original and free to use.

render(style, bpm, dur, sec, seed) -> stereo float32 array at 44.1 kHz
sec: dict with times in seconds
  build: drums drop out, snare roll + filter sweep (tension before the reveal)
  drop:  everything hits again with a crash (the reveal)
  outro: drums out, pads + melody (end text)
Styles: trap, synthwave, lofi, cinematic, upbeat."""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
rng0 = np.random.default_rng(0)


def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)


def _t(sec): return np.arange(int(sec * SR)) / SR


def lp(x, f, order=2): return sosfilt(butter(order, min(f, SR / 2 - 100) / (SR / 2), "low", output="sos"), x)
def hp(x, f, order=2): return sosfilt(butter(order, f / (SR / 2), "high", output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)], "band", output="sos"), x)


# ------------------------------------------------------------------ instruments (mono)
def kick(punch=1.0, length=0.45, low=45):
    t = _t(length); f = low + 110 * punch * np.exp(-t * 35)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    y += np.sin(2 * np.pi * 2.1 * np.cumsum(f) / SR) * np.exp(-t * 18) * 0.35
    y += bp(rng0.standard_normal(len(t)), 2000, 9000) * np.exp(-t * 250) * 0.5
    return np.tanh(y * 1.6)


def snare(length=0.25, tone=185):
    t = _t(length)
    return np.sin(2 * np.pi * tone * t) * np.exp(-t * 22) * 0.5 + bp(rng0.standard_normal(len(t)), 1200, 8000) * np.exp(-t * 15)


def clap(length=0.3):
    t = _t(length); n = rng0.standard_normal(len(t)); env = np.zeros(len(t))
    for d in (0.0, 0.011, 0.022): env += (t >= d) * np.exp(-np.maximum(t - d, 0) * 60)
    env += np.exp(-t * 9) * 0.35
    return bp(n, 900, 4500) * env


def hat(open_=False, length=None):
    length = length or (0.28 if open_ else 0.05); t = _t(length)
    return hp(rng0.standard_normal(len(t)), 7000) * np.exp(-t * (9 if open_ else 70)) * 0.5


def crash(length=2.0):
    t = _t(length)
    return hp(rng0.standard_normal(len(t)), 3500) * np.exp(-t * 1.8) * 0.55


def tom(f0=90, length=0.6):
    t = _t(length); f = f0 + 60 * np.exp(-t * 20)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 1.5 + bp(rng0.standard_normal(len(t)), 100, 900) * np.exp(-t * 25) * 0.3)


def sub808(freq, length, drive=2.4):
    t = _t(length)
    env = np.minimum(1, t / 0.005) * np.exp(-t * 1.1)
    y = np.sin(2 * np.pi * freq * t) * 0.6 + np.sin(2 * np.pi * 2 * freq * t) * 0.45 + np.sin(2 * np.pi * 3 * freq * t) * 0.15
    return np.tanh(y * env * drive) * 0.8


def saw(freq, t, phase=0.0): return 2 * ((freq * t + phase) % 1.0) - 1


def supersaw(freqs, length, detune=0.12, voices=3, attack=0.02, release=0.3):
    t = _t(length); L = np.zeros(len(t)); R = np.zeros(len(t))
    for f in freqs:
        for v in range(voices):
            d = 2 ** ((v - (voices - 1) / 2) * detune / 12)
            ph = rng0.random()
            (L if v % 2 == 0 else R)[:] += saw(f * d, t, ph)
            (R if v % 2 == 0 else L)[:] += saw(f * d * 1.002, t, ph + 0.3) * 0.6
    env = np.minimum(1, t / attack) * np.minimum(1, (length - t) / release).clip(0)
    k = 1 / (len(freqs) * voices)
    return L * env * k, R * env * k


def pluck(freq, length=0.6, bright=2.0):
    t = _t(length)
    return np.sin(2 * np.pi * freq * t + bright * np.exp(-t * 9) * np.sin(2 * np.pi * 2 * freq * t)) * np.exp(-t * 5.5)


def keys(freq, length=1.2):   # electric-piano-ish
    t = _t(length)
    y = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 3)
    return y * np.exp(-t * 1.6) * (1 + 0.15 * np.sin(2 * np.pi * 5 * t))


def string(freq, length):
    t = _t(length)
    y = lp(saw(freq, t) + saw(freq * 1.003, t, 0.4), 2200)
    return y * np.minimum(1, t / 0.15) * np.minimum(1, (length - t) / 0.2).clip(0) * 0.5


# ------------------------------------------------------------------ styles
STYLES = {
    # key root (midi), scale (minor/major), progressions, bpm range
    "trap":      dict(root=57, minor=True,  progs=[[0, 8, 3, 10], [0, 5, 8, 7], [0, 10, 8, 7]]),
    "synthwave": dict(root=54, minor=True,  progs=[[0, 8, 10, 5], [0, 8, 3, 10], [0, 5, 10, 8]]),
    "lofi":      dict(root=62, minor=False, progs=[[2, 7, 0, 9], [9, 2, 7, 0], [5, 4, 2, 0]]),
    "cinematic": dict(root=50, minor=True,  progs=[[0, 8, 5, 7], [0, 3, 8, 7], [0, 8, 3, 7]]),
    "upbeat":    dict(root=60, minor=False, progs=[[0, 7, 9, 5], [5, 0, 7, 9], [0, 5, 9, 7]]),
}
MINOR = [0, 2, 3, 5, 7, 8, 10]
MAJOR = [0, 2, 4, 5, 7, 9, 11]


def chord(root, deg, minor, seventh=False):
    scale = MINOR if minor else MAJOR
    # build a diatonic triad on the scale degree closest to `deg`
    idx = min(range(7), key=lambda i: abs(scale[i] - deg % 12))
    notes = [root + deg]
    for step in (2, 4) + ((6,) if seventh else ()):
        j = idx + step
        notes.append(root + scale[j % 7] + 12 * (j // 7) + (deg - scale[idx]))
    return notes


def render(style, bpm, dur, sec, seed=1):
    st = STYLES[style]; rng = np.random.default_rng(seed)
    beat = 60.0 / bpm; bar = 4 * beat
    n = int((dur + 3) * SR)
    D = np.zeros((n, 2)); B = np.zeros((n, 2)); M = np.zeros((n, 2)); Mb = np.zeros((n, 2))   # drums, bass, music, bright music
    build, drop, outro = sec.get("build", 1e9), sec.get("drop", 1e9), sec.get("outro", 1e9)
    prog = st["progs"][rng.integers(len(st["progs"]))]
    root = st["root"] + int(rng.integers(-2, 3))
    minor = st["minor"]
    kicks = []

    def put(buf, x, at, gain=1.0, pan=0.0):
        i = int(at * SR)
        if i >= n or i + len(x) <= 0: return
        if i < 0: x = x[-i:]; i = 0
        x = x[: n - i]
        buf[i:i + len(x), 0] += x * gain * (1 - max(0, pan))
        buf[i:i + len(x), 1] += x * gain * (1 + min(0, pan))

    def put2(buf, L, R, at, gain=1.0):
        i = int(at * SR)
        if i >= n: return
        L = L[: n - i]; R = R[: n - i]
        buf[i:i + len(L), 0] += L * gain; buf[i:i + len(R), 1] += R * gain

    def section(tb):
        if tb >= outro: return "outro"
        if build <= tb < drop: return "build"
        return "full"

    nbars = int(dur / bar) + 2
    swing = 0.12 * beat if style == "lofi" else 0.0
    # ---------------- drums
    for b in range(nbars * 16):          # 16th grid
        tb = b * beat / 4
        if tb > dur + 0.5: break
        pos = b % 16; barno = b // 16; sec_ = section(tb)
        sw = swing if (pos % 4 == 2) else 0.0
        fill = (barno % 4 == 3) and pos >= 12
        if sec_ == "build":
            # snare roll that gets denser towards the drop
            prog_b = (tb - build) / max(0.01, drop - build)
            div = 4 if prog_b < 0.5 else (2 if prog_b < 0.85 else 1)
            if pos % div == 0:
                put(D, snare(0.15) if style != "cinematic" else tom(110 + 60 * prog_b, 0.3), tb, 0.25 + 0.6 * prog_b)
            continue
        if sec_ == "outro":
            if style in ("lofi", "synthwave") and pos % 4 == 2: put(D, hat(), tb + sw, 0.25)
            continue
        if style == "trap":
            if pos in (0, 10) or (barno % 2 == 1 and pos == 7): put(D, kick(1.0, 0.5), tb); kicks.append(tb)
            if pos in (8,): put(D, clap(), tb, 0.8); put(D, snare(), tb, 0.35)
            roll = (barno % 2 == 1 and pos >= 12)
            if pos % 2 == 0 or roll:
                put(D, hat(), tb, 0.45 if pos % 4 == 0 else 0.3, pan=0.2)
                if roll: put(D, hat(), tb + beat / 8, 0.25, pan=0.2)
        elif style == "synthwave":
            if pos % 4 == 0: put(D, kick(1.0, 0.4, 50), tb); kicks.append(tb)
            if pos in (4, 12): put(D, snare(0.3, 200), tb, 0.6); put(D, clap(), tb, 0.35)
            if pos % 4 == 2: put(D, hat(True), tb, 0.35, pan=-0.2)
            if pos % 2 == 1: put(D, hat(), tb, 0.18, pan=0.25)
            if fill and pos % 1 == 0: put(D, tom(140 - (pos - 12) * 15, 0.25), tb, 0.35)
        elif style == "lofi":
            if pos in (0, 7, 10): put(D, kick(0.7, 0.35, 48), tb + sw, 0.8); kicks.append(tb)
            if pos in (4, 12): put(D, lp(snare(0.2, 170), 5000), tb + sw, 0.45)
            if pos % 2 == 0: put(D, lp(hat(), 9000), tb + sw, 0.22, pan=0.2)
        elif style == "cinematic":
            if pos in (0, 6, 8) or (barno % 2 and pos == 14): put(D, tom(70, 0.8), tb, 0.9); kicks.append(tb)
            if pos in (4, 12): put(D, tom(130, 0.4), tb, 0.5)
            if pos % 2 == 1: put(D, hat(), tb, 0.12)
        elif style == "upbeat":
            if pos in (0, 6, 8): put(D, kick(0.9, 0.35, 52), tb); kicks.append(tb)
            if pos in (4, 12): put(D, clap(), tb, 0.7)
            if pos % 2 == 0: put(D, hat(pos % 8 == 4), tb, 0.25, pan=0.2)
            if pos % 4 == 3: put(D, hat(), tb, 0.15, pan=-0.2)
    for at in [0.0] + ([drop] if drop < dur else []):
        put(D, crash(1.6), at, 0.5); put(D, kick(1.2, 0.6), at, 1.0); kicks.append(at)

    # ---------------- harmony + bass + melody, one chord per bar
    scale = MINOR if minor else MAJOR
    motif = [int(x) for x in rng.integers(0, 5, 8)]       # melody motif on a pentatonic-ish set
    rhythm = [int(x) for x in rng.integers(0, 2, 8)]
    for bi in range(nbars):
        tb = bi * bar
        if tb > dur + 0.5: break
        deg = prog[bi % len(prog)]
        notes = chord(root, deg, minor, seventh=(style in ("lofi", "upbeat")))
        sec_ = section(tb)
        # pads / chords
        if style in ("trap", "synthwave", "upbeat", "cinematic"):
            L, R = supersaw([mtof(m) for m in notes], bar + 0.05, detune=0.16 if style == "synthwave" else 0.1)
            dark = lp(L, 900), lp(R, 900)
            put2(M, dark[0], dark[1], tb, 0.55)
            put2(Mb, lp(L, 5000), lp(R, 5000), tb, 0.45)
        if style == "lofi":
            for k, m in enumerate(notes):
                put(M, keys(mtof(m), bar * 0.95), tb + k * 0.012 + swing, 0.22, pan=(k - 1.5) * 0.2)
        if style == "cinematic":
            for k in range(8):   # string ostinato in 8ths
                m = notes[k % 3] + 12
                put(M, string(mtof(m), beat / 2 * 0.95), tb + k * beat / 2, 0.22, pan=0.3 * (1 if k % 2 else -1))
        # bass
        if sec_ != "build":
            r = mtof(notes[0] - 24)
            if style == "trap":
                for p in (0, 2.5) if bi % 2 == 0 else (0, 1.75, 2.5):
                    put(B, sub808(r, beat * 1.4), tb + p * beat, 0.9)
            elif style == "synthwave":
                for k in range(8):
                    x = lp(saw(r * 2, _t(beat / 2 * 0.9)), 700) * np.exp(-_t(beat / 2 * 0.9) * 4)
                    put(B, x, tb + k * beat / 2, 0.55)
            elif style == "lofi":
                put(B, lp(sub808(r * 2, bar * 0.9, 1.0), 400), tb + swing, 0.7)
            elif style == "upbeat":
                for k, p in enumerate((0, 0.75, 1.5, 2, 2.75, 3.5)):
                    put(B, lp(saw(r * 2, _t(beat * 0.4)), 900) * np.exp(-_t(beat * 0.4) * 6), tb + p * beat, 0.5)
            elif style == "cinematic":
                put(B, sub808(r, bar * 0.95, 1.2), tb, 0.6)
        # arp (synthwave/upbeat)
        if style in ("synthwave", "upbeat") and sec_ != "outro":
            for k in range(16):
                m = notes[k % len(notes)] + 12 * (1 + (k // 4) % 2)
                put(M, lp(saw(mtof(m), _t(beat / 4 * 0.8)), 3000) * np.exp(-_t(beat / 4 * 0.8) * 14), tb + k * beat / 4, 0.12,
                    pan=0.35 * (1 if k % 2 else -1))
        # lead melody: motif A A' B A'' over 4 bars
        if sec_ != "build":
            var = bi % 4
            for k in range(8):
                if not rhythm[(k + var) % 8] and var != 2: continue
                deg_i = (motif[(k + var * 3) % 8] + (2 if var == 2 else 0)) % 5
                pent = [0, 2, 4, 7, 9] if not minor else [0, 3, 5, 7, 10]
                m = root + 12 + pent[deg_i] + (12 if style in ("trap", "lofi") else 0)
                inst = pluck(mtof(m), beat * 1.2) if style != "lofi" else keys(mtof(m), beat * 1.5)
                g = 0.16 if sec_ == "full" else 0.22
                put(M, inst, tb + k * beat / 2 + (swing if k % 2 else 0), g, pan=0.15)

    # ---------------- mix: sidechain, build sweep, outro
    t = np.arange(n) / SR
    duck = np.ones(n)
    for k in kicks:
        i = int(k * SR); m = min(n, i + int(0.3 * SR))
        if i < n: duck[i:m] = np.minimum(duck[i:m], 1 - 0.55 * np.exp(-(t[i:m] - k) / 0.09))
    # bright layer: on in full sections, sweeping up during the build, dim in the outro
    bright = np.where(t < build, 1.0, 0.0)
    if drop < 1e8:
        bright = np.where((t >= build) & (t < drop), ((t - build) / max(0.01, drop - build)) ** 2, bright)
        bright = np.where(t >= drop, 1.0, bright)
    bright = np.where(t >= outro, np.exp(-(t - outro) * 1.5), bright)
    music = M + Mb * bright[:, None]
    D = D - lp(D.T, 70).T * 0.45          # tame the drum sub, keep the punch
    mix = D * 0.75 + B * 0.5 * duck[:, None] + music * 1.6 * duck[:, None] ** 0.7
    mix = hp(mix.T, 38).T
    fade = np.minimum(1, (dur + 0.3 - t) / 0.6).clip(0)
    mix *= fade[:, None]
    mix = np.tanh(mix * 1.2)
    mix /= max(1e-6, np.abs(mix).max()) / 0.9
    return mix[: int(dur * SR)].astype(np.float32)


if __name__ == "__main__":   # quick listening test: python3 music.py style bpm out.wav
    import sys, soundfile as sf
    style, bpm, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    sf.write(out, render(style, bpm, 16, dict(build=9.6, drop=11.2, outro=13.6), seed=3), SR)
