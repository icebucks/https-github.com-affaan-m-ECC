#!/usr/bin/env python3
"""Erzeugt Atmo, Musik und Soundeffekte prozedural (100 % selbst erzeugt, keine
Lizenzfragen) und mischt sie mit der Stimme. Ergebnis: Stereo-WAV, -15 LUFS, Erzähler klar im Vordergrund.

Aufruf: python3 audio_mix.py <plan.json>
plan = {
  "seed": 123, "duration": 38.0, "voice": "voice.wav", "out": "mix.wav",
  "atmo": ["regen", "wald"], "musik": "drone_moll",
  "scenes": [{"start": 0, "end": 3.7, "wendepunkt": false, "ton": null}, ...],
  "hook_hit": 0.0, "wende_start": 30.1, "endcard_start": 36.2,
  "events": [{"t": 31.0, "typ": "speer"}, ...]
}
"""
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000


# ---------------------------------------------------------------- Helfer
def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def norm(x, peak=1.0):
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


def smooth_noise(rng, n, rate_hz):
    """Langsam schwankende Kurve 0..1 (für Böen, Flackern)."""
    pts = max(4, int(n / SR * rate_hz) + 2)
    v = rng.random(pts)
    curve = np.interp(np.linspace(0, pts - 1, n), np.arange(pts), v)
    return lp(curve, max(0.5, rate_hz), 1)


def env_points(n, points):
    """points: [(sekunde, wert), ...] -> lineare Hüllkurve"""
    ts = np.array([p[0] for p in points]) * SR
    vs = np.array([p[1] for p in points])
    return np.interp(np.arange(n), ts, vs)


def stereo(rng, mono_fn):
    return np.stack([mono_fn(rng), mono_fn(rng)])


def place(buf, clip, t, gain=1.0):
    i = int(t * SR)
    if i >= buf.shape[1] or i + clip.shape[-1] <= 0:
        return
    if clip.ndim == 1:
        clip = np.stack([clip, clip])
    j = min(buf.shape[1], i + clip.shape[1])
    buf[:, max(0, i):j] += clip[:, max(0, -i):j - i] * gain


# ---------------------------------------------------------------- Atmo
def pink(r, n):
    """rosa Rauschen (1/f) – weicher und natürlicher als weißes Rauschen"""
    w = r.standard_normal(n)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w)


def atmo_regen(rng, n):
    """Regen aus vielen einzelnen Tropfen-Einschlägen + weichem Prasseln (kein Zischen)."""
    def one(r):
        # weiches Prasseln: rosa Rauschen, nur tiefe/mittlere Lagen
        wash = bp(pink(r, n), 250, 2600, 2)
        wash = norm(wash, 0.35) * (0.8 + 0.2 * smooth_noise(r, n, 0.25))
        # Tropfen: kurze, gedämpfte Resonanzen in vier Tonlagen
        drops = np.zeros(n)
        for lo, hi, rate, gain in [(700, 1400, 70, 1.0), (1300, 2400, 110, 0.8), (2200, 3600, 120, 0.55), (3400, 5200, 60, 0.3)]:
            imp = np.zeros(n)
            k = int(n / SR * rate)
            idx = r.integers(0, n, size=k)
            imp[idx] = (r.random(k) ** 2.5) * np.sign(r.random(k) - 0.5)
            res = signal.sosfilt(signal.butter(2, [lo, hi], btype="band", fs=SR, output="sos"), imp)
            drops += res * gain
        drops = norm(drops, 0.6)
        # gelegentliche schwere Tropfen (Blätter, Dach)
        heavy = np.zeros(n)
        k = int(n / SR * 3)
        idx = r.integers(0, n, size=k)
        heavy[idx] = r.random(k) * 0.8
        heavy = bp(heavy, 300, 1200, 2) * 6
        mix_ = wash + drops + norm(heavy, 0.25)
        return lp(mix_, 6500, 4)
    return norm(stereo(rng, one), 0.5)


def atmo_wald(rng, n):  # Wind in Baumkronen
    def one(r):
        w = np.cumsum(r.standard_normal(n))
        w = hp(w, 40)
        w = bp(norm(w), 120, 1400)
        gust = 0.35 + 0.65 * smooth_noise(r, n, 0.15) ** 2
        return w * gust
    return norm(stereo(rng, one), 0.5)


def atmo_feuer(rng, n):
    def one(r):
        rumble = lp(r.standard_normal(n), 300) * 0.6
        crack = np.zeros(n)
        idx = r.integers(0, n, size=int(n / SR * 25))
        crack[idx] = (r.random(len(idx)) ** 3) * np.sign(r.random(len(idx)) - 0.5)
        crack = bp(crack, 1500, 9000) * 6
        hiss = bp(r.standard_normal(n), 2000, 6000) * 0.08
        return rumble + crack + hiss
    return norm(stereo(rng, one), 0.5)


def atmo_stadt(rng, n):  # entferntes Stimmengewirr-artiges Murmeln
    def one(r):
        x = r.standard_normal(n)
        murmur = bp(x, 250, 900) * (0.4 + 0.6 * smooth_noise(r, n, 3.0))
        air = lp(r.standard_normal(n), 400) * 0.4
        return murmur + air
    return norm(stereo(rng, one), 0.4)


def atmo_maschine(rng, n):
    t = np.arange(n) / SR
    hum = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) / (k + 1)
              for k, f in enumerate([48, 96, 144, 61]))
    pulse = (0.5 + 0.5 * np.sin(2 * np.pi * 1.4 * t)) ** 6
    thump = lp(rng.standard_normal(n), 180) * pulse * 3
    roar = bp(rng.standard_normal(n), 80, 700) * 0.5
    mono = hum * 0.4 + thump + roar
    return norm(np.stack([mono, np.roll(mono, 600)]), 0.55)


def atmo_wasser(rng, n):
    def one(r):
        x = r.standard_normal(n)
        return lp(x, 1800) * (0.6 + 0.4 * smooth_noise(r, n, 1.5)) + bp(x, 2000, 6000) * 0.1
    return norm(stereo(rng, one), 0.45)


ATMO = {"regen": atmo_regen, "wald": atmo_wald, "feuer": atmo_feuer,
        "stadt": atmo_stadt, "maschine": atmo_maschine, "wasser": atmo_wasser}


# ---------------------------------------------------------------- Musik
CHORDS = {
    # Grundton-Frequenzen (Hz) pro Akkord; langsam wechselnd
    "drone_moll": [[73.4, 110.0, 174.6], [58.3, 116.5, 174.6], [65.4, 98.0, 155.6], [55.0, 110.0, 164.8]],
    "drone_dunkel": [[61.7, 92.5, 146.8], [55.0, 82.4, 130.8], [65.4, 98.0, 155.6], [49.0, 98.0, 146.8]],
    "drone_stahl": [[82.4, 123.5, 196.0], [73.4, 110.0, 174.6], [65.4, 130.8, 196.0], [61.7, 92.5, 185.0]],
}


def music(rng, n, kind, wende_start, endcard_start):
    chords = CHORDS.get(kind, CHORDS["drone_moll"])
    t = np.arange(n) / SR
    seg = 8.0
    out = np.zeros((2, n))
    for ci in range(int(n / SR / seg) + 2):
        notes = chords[ci % len(chords)]
        a, b = ci * seg - 1.5, (ci + 1) * seg + 1.5
        win = np.clip(np.minimum((t - a) / 1.5, (b - t) / 1.5), 0, 1)
        if not win.any():
            continue
        for ch in range(2):
            for f in notes:
                for det in (-0.6, 0.0, 0.7):
                    ph = rng.random() * 6.28
                    fd = f * (1 + det / 1200 * 8) * (1.0 + 0.002 * ch)
                    saw = 2 * ((t * fd + ph / 6.28) % 1) - 1
                    out[ch] += saw * win * 0.15
    # weiches Filter, das sich langsam öffnet
    for ch in range(2):
        out[ch] = lp(out[ch], 700, 2)
    breath = 0.7 + 0.3 * np.sin(2 * np.pi * t / 11.0)
    out *= breath
    # Wendepunkt: tiefe Trommeln (Herzschlag, schneller werdend)
    if wende_start is not None:
        tt = wende_start
        bpm = 70.0
        while tt < endcard_start - 0.2:
            place(out, drum(rng) * 1.4, tt)
            place(out, drum(rng) * 0.9, tt + 60 / bpm * 0.35)
            tt += 60 / bpm
            bpm = min(110, bpm + 6)
    return norm(out, 0.5)


# ---------------------------------------------------------------- SFX
def drum(rng):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    f = 52 + 70 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    skin = lp(rng.standard_normal(n), 900) * np.exp(-t * 30) * 0.4
    return body + skin


def boom(rng, length=2.4):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = 34 + 90 * np.exp(-t * 9)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    crack = lp(rng.standard_normal(n), 2500) * np.exp(-t * 25) * 0.7
    tail = lp(rng.standard_normal(n), 300) * np.exp(-t * 3) * 0.5
    x = sub + crack + tail
    return norm(np.stack([x, np.roll(x, 240)]), 1.0)


def whoosh(rng, length=0.9):
    n = int(length * SR)
    x = rng.standard_normal(n)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    sweep = np.linspace(400, 3000, n)
    y = np.zeros(n)
    # zeitvariable Bandpass-Annäherung: zwei Hälften
    y[: n // 2] = bp(x[: n // 2], 300, 1500)
    y[n // 2:] = bp(x[n // 2:], 900, 4000)
    y = lp(y, 5000) * e
    pan = np.linspace(-1, 1, n)
    return norm(np.stack([y * (1 - pan) / 2, y * (1 + pan) / 2]), 0.8)


def riser(rng, length=2.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    y = bp(x, 500, 6000) * (t / length) ** 2.5
    tone = np.sin(2 * np.pi * np.cumsum(80 + 220 * (t / length) ** 2) / SR) * (t / length) ** 2 * 0.4
    return norm(np.stack([y + tone, y + tone]), 0.8)


def speer(rng):  # kurzes Zischen eines fliegenden Speers + dumpfer Einschlag
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    z = bp(rng.standard_normal(n), 1500, 7000) * np.sin(np.linspace(0, np.pi, n)) ** 3
    thud = np.zeros(n)
    k = int(0.38 * SR)
    m = n - k
    tt = np.arange(m) / SR
    thud[k:] = np.sin(2 * np.pi * 90 * tt) * np.exp(-tt * 30) * 1.2
    pan = rng.random() * 2 - 1
    y = z * 0.8 + thud
    return np.stack([y * (1 - pan * 0.6), y * (1 + pan * 0.6)])


def glocke(rng, length=2.5):  # elektrische Alarmglocke
    n = int(length * SR)
    t = np.arange(n) / SR
    strike = (np.sin(2 * np.pi * 22 * t) > 0).astype(float)
    tone = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(1180, 1), (2950, 0.5), (4100, 0.25)])
    y = tone * (0.6 + 0.4 * strike) * np.minimum(1, (length - t) * 4)
    return norm(np.stack([y, y]), 0.5)


def kratzen(rng, length=2.6):  # Eisberg schrammt an der Bordwand
    n = int(length * SR)
    t = np.arange(n) / SR
    grind = bp(rng.standard_normal(n), 150, 1200) * (0.5 + 0.5 * smooth_noise(rng, n, 9))
    groan = np.sin(2 * np.pi * np.cumsum(55 + 15 * np.sin(t * 2.1)) / SR)
    e = np.minimum(1, t * 3) * np.minimum(1, (length - t) * 1.5)
    y = (grind + groan * 0.6) * e
    return norm(np.stack([y, np.roll(y, 900)]), 0.9)


def beben(rng, length=2.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    y = lp(rng.standard_normal(n), 90, 4) * np.sin(np.pi * t / length) ** 2
    return norm(np.stack([y, y]), 0.9)


def einbruch(rng, length=4.0):  # Wasser schießt herein
    n = int(length * SR)
    t = np.arange(n) / SR
    y = lp(rng.standard_normal(n), 2500) * np.minimum(1, t * 6) * np.minimum(1, (length - t))
    return norm(np.stack([y, np.roll(y, 300)]), 0.9)


def steine(rng, length=3.0):
    n = int(length * SR)
    y = np.zeros(n)
    idx = rng.integers(0, n, size=40)
    y[idx] = rng.random(40)
    y = bp(y, 300, 3000) * 8
    return norm(np.stack([y, np.roll(y, 1200)]), 0.6)


SFX = {"boom": boom, "whoosh": whoosh, "riser": riser, "speer": speer, "glocke": glocke,
       "kratzen": kratzen, "beben": beben, "einbruch": einbruch, "steine": steine}


# ---------------------------------------------------------------- Mix
def read_voice(path):
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "v.wav"
        # tiefe, warme Erzählstimme: Hochpass, Wärme, Präsenz, leichte Kompression
        af = ("highpass=f=70,equalizer=f=160:t=q:w=1:g=3,equalizer=f=320:t=q:w=1:g=-2,"
              "equalizer=f=3200:t=q:w=1.2:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=120,"
              "aecho=0.8:0.5:28|47:0.12|0.07")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-af", af,
                        "-ar", str(SR), "-ac", "1", str(out)], check=True)
        with wave.open(str(out)) as w:
            data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
    return data


def main():
    plan = json.load(open(sys.argv[1], encoding="utf-8"))
    rng = np.random.default_rng(plan.get("seed", 1))
    n = int(plan["duration"] * SR)
    voice = read_voice(plan["voice"])
    v = np.zeros(n)
    v[: min(n, len(voice))] = voice[:n]

    # Atmo
    bed = np.zeros((2, n))
    for i, a in enumerate(plan.get("atmo", [])):
        if a in ATMO:
            bed += ATMO[a](rng, n) * (1.0 if i == 0 else 0.7)
    # Stille-Szenen: Atmo fällt fast weg
    pts = [(0, 1.0)]
    for s in plan["scenes"]:
        if s.get("ton") == "stille":
            pts += [(s["start"] - 0.05, 1.0), (s["start"] + 0.6, 0.08), (s["end"] - 0.3, 0.08), (s["end"], 1.0)]
    pts.append((plan["duration"], 1.0))
    pts.sort()
    bed *= env_points(n, pts)

    mus = music(rng, n, plan.get("musik", "drone_moll"), plan.get("wende_start"), plan["endcard_start"])
    mpts = [(0, 0.0), (0.3, 1.0)]
    for s in plan["scenes"]:
        if s.get("ton") == "stille":
            mpts += [(s["start"], 1.0), (s["start"] + 0.4, 0.0), (s["end"] - 0.05, 0.0), (s["end"], 1.0)]
    mpts += [(plan["duration"] - 1.2, 1.0), (plan["duration"], 0.0)]
    mpts.sort()
    mus *= env_points(n, mpts)

    # --- Klare Sprache: Hintergrund aus dem Sprachbereich nehmen (1,5–4 kHz) und Höhen zähmen
    def clear_for_voice(x, top=6500):
        y = np.stack([lp(hp(ch, 70), top) for ch in x])
        presence = np.stack([bp(ch, 1500, 4000) for ch in y])
        return y - 0.55 * presence          # ca. -7 dB im Sprachband

    bed = clear_for_voice(bed, 6000)
    mus = clear_for_voice(mus, 5000)

    # --- Sidechain-Ducking: weich (Attack ~60 ms, Release ~450 ms), ca. -12 dB unter der Stimme
    lvl = np.abs(v)
    fast = lp(lvl, 8)
    slow = lp(lvl, 1.2)
    venv = np.maximum(fast, slow)
    venv = np.clip(venv / (np.percentile(venv[venv > 1e-4], 90) if (venv > 1e-4).any() else 1), 0, 1)
    duck = 1.0 - 0.75 * venv                # 1.0 in Pausen, 0.25 (= -12 dB) beim Sprechen

    # --- Effekte: wenige, gezielt; nur Schlüsselmomente bleiben voll, der Rest weicht der Stimme
    sfx = np.zeros((2, n))       # wird geduckt
    hits = np.zeros((2, n))      # Hook, Wendepunkt, Endkarte: nicht geduckt (liegen nicht auf Sprache)
    place(hits, boom(rng), plan.get("hook_hit", 0.0) + 0.02, 0.7)
    whoosh_takes = [whoosh(rng, 0.7), whoosh(rng, 0.9), whoosh(rng, 1.1)]
    last_w = -9.0
    for i, s in enumerate(plan["scenes"][1:]):
        # Whoosh höchstens alle 6 s und nie in Stille-Szenen
        if s.get("ton") == "stille" or s["start"] - last_w < 6.0:
            continue
        place(sfx, whoosh_takes[i % 3], s["start"] - 0.35, 0.12)
        last_w = s["start"]
    if plan.get("wende_start") is not None:
        place(sfx, riser(rng, 1.8), plan["wende_start"] - 1.8, 0.22)
        place(hits, boom(rng, 2.0), plan["wende_start"] + 0.02, 0.55)
    for ev in plan.get("events", []):
        fn = SFX.get(ev["typ"])
        if fn:
            place(sfx, fn(rng), ev["t"], ev.get("gain", 0.6) * 0.7)
    place(hits, boom(rng, 3.0), plan["endcard_start"] + 0.02, 0.6)
    sfx = clear_for_voice(sfx, 9000)

    voice2 = np.stack([v, v])
    mix = (voice2 * 1.0
           + bed * duck * 0.055
           + mus * duck * 0.05
           + sfx * (1.0 - 0.6 * venv) * 0.35
           + hits * 0.35)
    # Kontrolle: Abstand Stimme zu Hintergrund während des Sprechens (Ziel >= 15 dB)
    speaking = venv > 0.5
    if speaking.any():
        back = (bed * duck * 0.055 + mus * duck * 0.05 + sfx * (1.0 - 0.6 * venv) * 0.35)[:, speaking]
        snr = 20 * np.log10((np.sqrt((voice2[:, speaking] ** 2).mean()) + 1e-9) / (np.sqrt((back ** 2).mean()) + 1e-9))
        print(f"Stimme/Hintergrund beim Sprechen: {snr:.1f} dB", file=sys.stderr)
    mix = np.clip(mix, -1, 1)

    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw.wav"
        with wave.open(str(raw), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((mix.T * 32767).astype(np.int16).tobytes())
        loudnorm(str(raw), plan["out"])
    print(json.dumps({"out": plan["out"], "duration": plan["duration"]}))


def loudnorm(src, dst, target=-15.0):
    """Zwei-Pass-Lautheitsnormalisierung auf -15 LUFS, True Peak -2 dBTP (TikTok-tauglich, nicht zu laut)."""
    first = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af",
                            f"loudnorm=I={target}:TP=-2:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True)
    txt = first.stderr
    m = json.loads(txt[txt.rindex("{"): txt.rindex("}") + 1])
    af = (f"loudnorm=I={target}:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", af, "-ar", str(SR), dst], check=True)


if __name__ == "__main__":
    main()
