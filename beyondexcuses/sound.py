"""Original soundtrack: soft piano + pad (minor -> major at the turn), wind, footsteps, sfx.
Usage: sound.py events.json duration turn_time out.wav"""
import json, sys, wave, subprocess
import numpy as np
from scipy import signal

SR = 44100
rng = np.random.default_rng(1)
ev = json.load(open(sys.argv[1])); DUR = float(sys.argv[2]); TURN = float(sys.argv[3]); OUT = sys.argv[4]
N = int(DUR * SR); t_all = np.arange(N) / SR
mix = np.zeros((N, 2))


def mtof(m): return 440 * 2 ** ((m - 69) / 12)


def lp(x, f): return signal.sosfilt(signal.butter(2, f, "lowpass", fs=SR, output="sos"), x)
def bp(x, a, b): return signal.sosfilt(signal.butter(2, [a, b], "bandpass", fs=SR, output="sos"), x)


def add(x, at, gain=1.0, pan=0.0):
    s = int(at * SR); e = min(N, s + len(x))
    if e <= s: return
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    mix[s:e, 0] += gain * l * x[: e - s]; mix[s:e, 1] += gain * r * x[: e - s]


def piano(m, dur=2.5, vel=0.25):
    f = mtof(m); t = np.arange(int(dur * SR)) / SR
    y = sum(np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k)) * (0.6 ** (k - 1)) * np.exp(-t * (1.2 + 0.9 * k)) for k in range(1, 7))
    y *= np.minimum(1, t / 0.004)
    return vel * lp(y, 3500)


def pad(ms, dur, vel=0.05):
    t = np.arange(int(dur * SR)) / SR
    y = sum(np.sin(2 * np.pi * mtof(m) * t + 0.3 * np.sin(2 * np.pi * 0.2 * t)) + 0.3 * np.sin(2 * np.pi * mtof(m) * 2.003 * t) for m in ms)
    env = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.2)
    return vel * lp(y * env, 1800)


# chord progression; minor before the turn, major after
minor = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
major = [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]]   # C G Am F
bar = 2.4
t = 0.3; i = 0
while t < DUR - 0.5:
    ch = (minor if t < TURN else major)[i % 4]
    add(pad([m - 12 for m in ch] + ch[:1], bar + 1.2, 0.035), t)
    arp = ch + [ch[1] + 12, ch[2] + 12, ch[1] + 12]
    for k, m in enumerate(arp):
        add(piano(m + 12 * (t >= TURN), 2.2, 0.16 if k else 0.2), t + k * bar / 6, pan=-0.3 + 0.12 * k)
    add(piano(ch[0] - 12, 3.0, 0.22), t)
    t += bar; i += 1

# wind bed
w = lp(rng.standard_normal(N), 500) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t_all)) * 0.05
mix[:, 0] += w; mix[:, 1] += np.roll(w, 2000)

for e in ev:
    kind, at = e[0], e[1]
    if kind == "step":
        n = int(0.09 * SR); x = bp(rng.standard_normal(n), 300, 2500) * np.exp(-np.arange(n) / SR * 45)
        add(x, at, 0.10 if not e[2] else 0.12, pan=0.25)
    elif kind == "slip":
        n = int(0.55 * SR); env = np.linspace(1, 0.2, n)
        add(bp(rng.standard_normal(n), 800, 6000) * env * 0.3, at, pan=0.3)
    elif kind == "thud":
        n = int(0.6 * SR); tt = np.arange(n) / SR
        add((np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 9) + lp(rng.standard_normal(n), 400) * np.exp(-tt * 15) * 0.6) * 0.5, at, pan=0.3)
    elif kind == "sunrise":
        n = int(2.6 * SR); tt = np.arange(n) / SR
        add(bp(rng.standard_normal(n), 4000, 12000) * (tt / 2.6) ** 2 * 0.08, at)
    elif kind == "summit":
        for k, m in enumerate([72, 76, 79, 84]):
            add(piano(m, 3.0, 0.15), at + k * 0.09, pan=-0.2 + 0.15 * k)
    elif kind == "jump":
        n = int(0.35 * SR); env = np.sin(np.linspace(0, np.pi, n)) ** 2
        add(bp(rng.standard_normal(n), 600, 3000) * env * 0.12, at, pan=0.2)
    elif kind == "land":
        n = int(0.25 * SR); tt = np.arange(n) / SR
        add((np.sin(2 * np.pi * 110 * tt) * np.exp(-tt * 25) + bp(rng.standard_normal(n), 200, 2000) * np.exp(-tt * 30) * 0.5) * 0.25, at, pan=0.2)
    elif kind == "splash":
        n = int(0.8 * SR); tt = np.arange(n) / SR
        add(bp(rng.standard_normal(n), 500, 7000) * np.exp(-tt * 5) * 0.25, at)
    elif kind == "pop":
        n = int(0.12 * SR); tt = np.arange(n) / SR
        add(np.sin(2 * np.pi * (500 + 900 * tt / 0.12) * tt) * np.exp(-tt * 40) * 0.12, at, pan=-0.3)
    elif kind == "slide":
        n = int(0.9 * SR); tt = np.arange(n) / SR
        add(bp(rng.standard_normal(n), 1500, 7000) * np.exp(-tt * 2.5) * 0.12, at)
    elif kind == "rope":
        n = int(0.5 * SR); tt = np.arange(n) / SR
        add(bp(rng.standard_normal(n), 300, 1500) * np.sin(np.pi * tt / 0.5) * 0.15, at)
    elif kind == "thunder":
        n = int(3.0 * SR); tt = np.arange(n) / SR
        add(lp(rng.standard_normal(n), 180) * (np.exp(-tt * 1.2) * (1 + 0.5 * np.sin(tt * 9))) * 0.9, at)
    elif kind == "rain":  # e = ["rain", start, end]
        a0, a1 = int(at * SR), int(min(DUR, e[2]) * SR); n = a1 - a0
        if n > 0:
            env = np.minimum(1, np.minimum(np.arange(n) / SR / 0.8, (n - np.arange(n)) / SR / 1.5))
            r = bp(rng.standard_normal(n), 1500, 9000) * 0.09 * env
            mix[a0:a1, 0] += r; mix[a0:a1, 1] += np.roll(r, 900)
    elif kind in ("text", "text2"):
        n = int(1.8 * SR); tt = np.arange(n) / SR
        boom = np.sin(2 * np.pi * (48 * np.exp(-tt * 1.5) + 32) * tt) * np.exp(-tt * 2.2)
        add(boom * (0.35 if kind == "text" else 0.25), at)

fo = int(0.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
fi = int(0.03 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]   # no slow fade-in: the first frame must be heard
mix /= np.abs(mix).max() / 0.9
pcm = (mix * 32767).astype(np.int16)
with wave.open(OUT + ".raw.wav", "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(pcm.tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", OUT + ".raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", OUT], check=True)
