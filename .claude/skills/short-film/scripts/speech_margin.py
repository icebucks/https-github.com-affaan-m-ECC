#!/usr/bin/env python3
"""How far the voice sits above the music in the speech band, over time.

Usage: speech_margin.py VOICE.wav MUSIC.wav [--band 1000 4000] [--offset 0] [--target 12]

VOICE and MUSIC are the stems exactly as they sit in the mix (same start, same gain).
Prints the median margin (dB) while the voice speaks, the worst 10% and the seconds where
the margin is below the target. Also writes a phone-simulation mix next to VOICE
(<voice>_phone.wav: mono, 450 Hz-7 kHz band) for a quick listen.
Needs: numpy scipy soundfile
"""
import argparse, os
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt

ap = argparse.ArgumentParser()
ap.add_argument("voice"); ap.add_argument("music")
ap.add_argument("--band", nargs=2, type=float, default=[1000, 4000])
ap.add_argument("--offset", type=float, default=0.0, help="voice start inside the music file, seconds")
ap.add_argument("--target", type=float, default=12.0)
a = ap.parse_args()

def mono(p):
    x, sr = sf.read(p, always_2d=True); return x.mean(1), sr
v, sr = mono(a.voice); m, sr2 = mono(a.music)
assert sr == sr2, "resample both stems to the same rate first"
v = np.concatenate([np.zeros(int(a.offset * sr)), v]); n = max(len(v), len(m))
v = np.pad(v, (0, n - len(v))); m = np.pad(m, (0, n - len(m)))
sos = butter(4, a.band, btype="band", fs=sr, output="sos")
vb, mb = sosfiltfilt(sos, v), sosfiltfilt(sos, m)
hop = int(0.05 * sr); k = n // hop
def db(x): return 10 * np.log10(np.maximum((x[:k * hop].reshape(k, hop) ** 2).mean(1), 1e-12))
vdb, mdb = db(vb), db(mb)
speaking = vdb > vdb.max() - 30
marg = (vdb - mdb)[speaking]; ts = (np.arange(k) * 0.05)[speaking]
if not len(marg): raise SystemExit("no speech found in the voice stem")
print(f"speech band {a.band[0]:.0f}-{a.band[1]:.0f} Hz, {speaking.sum() * 0.05:.1f} s of speech")
print(f"median margin {np.median(marg):+.1f} dB, worst 10% {np.percentile(marg, 10):+.1f} dB (target {a.target:+.0f})")
low = ts[marg < a.target]
if len(low):
    spans, s0, prev = [], low[0], low[0]
    for t in low[1:]:
        if t - prev > 0.11: spans.append((s0, prev + 0.05)); s0 = t
        prev = t
    spans.append((s0, prev + 0.05))
    print("below target:", ", ".join(f"{x:.2f}-{y:.2f}s" for x, y in spans if y - x >= 0.2) or "only short blips")
phone = sosfiltfilt(butter(4, [450, 7000], btype="band", fs=sr, output="sos"), v + m)
phone *= 0.9 / max(1e-9, np.abs(phone).max())
p = os.path.splitext(a.voice)[0] + "_phone.wav"; sf.write(p, phone, sr); print("phone simulation:", p)
